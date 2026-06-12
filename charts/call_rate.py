import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from config import SERIES_GROUPS


def get_call_rate_group_config(
    db: str,
    selected_group_name: str,
) -> dict:
    """
    コールレートチャート用の系列グループ設定を取得する。
    """

    group_config = SERIES_GROUPS.get(db, {}).get(selected_group_name)

    if not group_config:
        raise ValueError(
            f"系列グループ設定が見つかりません: {db} / {selected_group_name}"
        )

    if group_config.get("chart_type") != "call_rate":
        raise ValueError(
            f"コールレートチャート用のグループではありません: {selected_group_name}"
        )

    return group_config


def detect_date_column(long_df: pd.DataFrame) -> str:
    """
    long_df から日付列を判定する。
    """

    if "SURVEY_DATE" in long_df.columns:
        return "SURVEY_DATE"

    if "SURVEY_DATE_LABEL" in long_df.columns:
        return "SURVEY_DATE_LABEL"

    raise ValueError(
        "日付列がありません: SURVEY_DATE または SURVEY_DATE_LABEL が必要です。"
    )


def convert_to_datetime(series: pd.Series) -> pd.Series:
    """
    YYYYMMDD / YYYY-MM-DD / YYYYMM の形式に対応して datetime に変換する。
    """

    date_values = series.astype(str)

    converted = pd.to_datetime(
        date_values,
        errors="coerce",
    )

    mask = converted.isna()

    if mask.any():
        converted.loc[mask] = pd.to_datetime(
            date_values.loc[mask],
            format="%Y%m%d",
            errors="coerce",
        )

    mask = converted.isna()

    if mask.any():
        converted.loc[mask] = pd.to_datetime(
            date_values.loc[mask],
            format="%Y%m",
            errors="coerce",
        )

    return converted


def make_call_rate_df(
    long_df: pd.DataFrame,
    group_config: dict,
) -> pd.DataFrame:
    """
    コールレート用の縦持ちデータを、チャート用の横持ちデータに変換する。

    変換後の列:
        date_raw: 元の日付文字列
        date: datetime型の日付
        average: 平均値
        high: 最高値
        low: 最低値
        volume: 出来高
    """
    long_df = long_df.copy()
    long_df.columns = long_df.columns.map(str)

    required_cols = ["SERIES_CODE", "VALUE"]

    missing_cols = [col for col in required_cols if col not in long_df.columns]
    if missing_cols:
        raise ValueError(f"必要な列がありません: {missing_cols}")

    # 系列コードも文字列に統一
    long_df["SERIES_CODE"] = long_df["SERIES_CODE"].astype(str)

    date_col = detect_date_column(long_df)

    fields = group_config["fields"]

    required_codes = [
        fields["average"],
        fields["high"],
        fields["low"],
        fields["volume"],
    ]

    chart_df = long_df.pivot_table(
        index=date_col,
        columns="SERIES_CODE",
        values="VALUE",
        aggfunc="first",
    ).reset_index()

    missing_codes = [code for code in required_codes if code not in chart_df.columns]

    if missing_codes:
        raise ValueError(
            "コールレートチャートに必要な系列コードが不足しています: "
            + ", ".join(missing_codes)
        )

    chart_df = chart_df.rename(
        columns={
            date_col: "date_raw",
            fields["average"]: "average",
            fields["high"]: "high",
            fields["low"]: "low",
            fields["volume"]: "volume",
        }
    )

    chart_df["date"] = convert_to_datetime(chart_df["date_raw"])

    value_cols = ["average", "high", "low", "volume"]

    for col in value_cols:
        chart_df[col] = pd.to_numeric(chart_df[col], errors="coerce")

    chart_df = chart_df.dropna(
        subset=["date", "average", "high", "low"],
        how="any",
    )

    chart_df = chart_df.sort_values("date")

    # 念のため最終的な列名も文字列化
    chart_df.columns = chart_df.columns.map(str)

    return chart_df


def render_call_rate_chart(
    db: str,
    long_df: pd.DataFrame,
    selected_group_name: str,
) -> None:
    """
    FM01 コールレートチャートを表示する。

    上段:
        最高値・最低値レンジ
        平均値の折れ線

    下段:
        出来高の棒グラフ
    """

    try:
        group_config = get_call_rate_group_config(
            db=db,
            selected_group_name=selected_group_name,
        )

        chart_df = make_call_rate_df(
            long_df=long_df,
            group_config=group_config,
        )

    except Exception as e:
        st.error("コールレートチャート用データの作成に失敗しました。")
        st.exception(e)
        return

    if chart_df.empty:
        st.warning("コールレートチャートとして表示できるデータがありません。")
        return

    fields = group_config["fields"]
    labels = fields.get("labels", {})

    average_label = labels.get("average", "平均値")
    high_label = labels.get("high", "最高値")
    low_label = labels.get("low", "最低値")
    volume_label = labels.get("volume", "出来高")
    range_label = labels.get("range", "最高値・最低値レンジ")

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        row_heights=[0.7, 0.3],
        specs=[
            [{"secondary_y": False}],
            [{"secondary_y": False}],
        ],
    )

    # 上段: 最高値ライン
    # fill の基準になるため、先に high を描画する
    fig.add_trace(
        go.Scatter(
            x=chart_df["date"],
            y=chart_df["high"],
            mode="lines",
            name=high_label,
            line=dict(width=1),
            hovertemplate=(
                "%{x|%Y-%m-%d}<br>" + f"{high_label}: " + "%{y:,.4f}<extra></extra>"
            ),
        ),
        row=1,
        col=1,
    )

    # 上段: 最低値ライン + high との間を塗りつぶし
    fig.add_trace(
        go.Scatter(
            x=chart_df["date"],
            y=chart_df["low"],
            mode="lines",
            name=range_label,
            fill="tonexty",
            line=dict(width=1),
            hovertemplate=(
                "%{x|%Y-%m-%d}<br>" + f"{low_label}: " + "%{y:,.4f}<extra></extra>"
            ),
        ),
        row=1,
        col=1,
    )

    # 上段: 平均値の折れ線
    fig.add_trace(
        go.Scatter(
            x=chart_df["date"],
            y=chart_df["average"],
            mode="lines+markers",
            name=average_label,
            hovertemplate=(
                "%{x|%Y-%m-%d}<br>" + f"{average_label}: " + "%{y:,.4f}<extra></extra>"
            ),
        ),
        row=1,
        col=1,
    )

    # 下段: 出来高棒グラフ
    fig.add_trace(
        go.Bar(
            x=chart_df["date"],
            y=chart_df["volume"],
            name=volume_label,
            hovertemplate=(
                "%{x|%Y-%m-%d}<br>" + f"{volume_label}: " + "%{y:,.0f}<extra></extra>"
            ),
        ),
        row=2,
        col=1,
    )

    fig.update_layout(
        title=selected_group_name,
        yaxis_title="コールレート",
        yaxis2_title=volume_label,
        hovermode="x unified",
        xaxis_rangeslider_visible=False,
        legend_title="系列",
        height=700,
    )

    # 上段の横軸
    fig.update_xaxes(
        type="date",
        tickformat="%Y-%m-%d",
        hoverformat="%Y-%m-%d",
        tickangle=-45,
        row=1,
        col=1,
    )

    # 下段の横軸
    fig.update_xaxes(
        type="date",
        tickformat="%Y-%m-%d",
        hoverformat="%Y-%m-%d",
        tickangle=-45,
        title_text="日付",
        row=2,
        col=1,
    )

    st.plotly_chart(fig, width="stretch")
