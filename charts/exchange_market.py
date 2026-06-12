import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from config import SERIES_GROUPS


def get_exchange_market_group_config(
    db: str,
    selected_group_name: str,
) -> dict:
    """
    為替市況グループの設定を取得する。

    Args:
        db: DB名
        selected_group_name: 選択された系列グループ名

    Returns:
        為替市況グループ設定
    """

    group_config = SERIES_GROUPS.get(db, {}).get(selected_group_name)

    if not group_config:
        raise ValueError(
            f"系列グループ設定が見つかりません: {db} / {selected_group_name}"
        )

    if group_config.get("chart_type") != "exchange_market":
        raise ValueError(
            f"為替市況チャート用のグループではありません: {selected_group_name}"
        )

    return group_config


def detect_date_column(long_df: pd.DataFrame) -> str:
    """
    long_df から日付列を判定する。

    resultset_to_long_df の作りによって、
    SURVEY_DATE または SURVEY_DATE_LABEL のどちらかを使う。
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
    YYYYMMDD / YYYY-MM-DD の両方に対応して datetime に変換する。

    日銀APIの日次データは、通常 YYYYMMDD 形式で返る想定。
    ただし、加工済みDataFrameで YYYY-MM-DD になっている可能性も考慮する。
    """

    date_values = series.astype(str)

    # まずは pandas の自動判定で変換
    converted = pd.to_datetime(
        date_values,
        errors="coerce",
    )

    # 20250131 のような YYYYMMDD が自動判定できない場合に再変換
    mask = converted.isna()

    if mask.any():
        converted.loc[mask] = pd.to_datetime(
            date_values.loc[mask],
            format="%Y%m%d",
            errors="coerce",
        )

    return converted


def make_exchange_market_df(
    long_df: pd.DataFrame,
    group_config: dict,
) -> pd.DataFrame:
    """
    為替市況用の縦持ちデータを、ローソク足用の横持ちデータに変換する。

    変換後の列:
        date_raw: 元の日付文字列
        date: datetime型の日付
        open: 始値
        high: 高値
        low: 安値
        close: 終値
        line: ローソク足に重ねる折れ線。設定がある場合のみ
        bar_1, bar_2, ...: 下段に表示する棒グラフ
    """

    long_df = long_df.copy()
    long_df.columns = long_df.columns.map(str)
    required_cols = ["SERIES_CODE", "VALUE"]

    missing_cols = [col for col in required_cols if col not in long_df.columns]
    if missing_cols:
        raise ValueError(f"必要な列がありません: {missing_cols}")

    long_df["SERIES_CODE"] = long_df["SERIES_CODE"].astype(str)

    date_col = detect_date_column(long_df)

    fields = group_config["fields"]

    ohlc_codes = [
        fields["open"],
        fields["high"],
        fields["low"],
        fields["close"],
    ]

    line_code = fields.get("line")
    bar_codes = fields.get("bars", [])

    required_codes = ohlc_codes + bar_codes

    if line_code:
        required_codes.append(line_code)

    chart_df = long_df.pivot_table(
        index=date_col,
        columns="SERIES_CODE",
        values="VALUE",
        aggfunc="first",
    ).reset_index()

    chart_df.columns = chart_df.columns.map(str)

    missing_codes = [code for code in required_codes if code not in chart_df.columns]

    if missing_codes:
        raise ValueError(
            "為替市況チャートに必要な系列コードが不足しています: "
            + ", ".join(missing_codes)
        )

    rename_map = {
        date_col: "date_raw",
        fields["open"]: "open",
        fields["high"]: "high",
        fields["low"]: "low",
        fields["close"]: "close",
    }

    if line_code:
        rename_map[line_code] = "line"

    for i, bar_code in enumerate(bar_codes, start=1):
        rename_map[bar_code] = f"bar_{i}"

    chart_df = chart_df.rename(columns=rename_map)

    chart_df["date"] = convert_to_datetime(chart_df["date_raw"])

    value_cols = ["open", "high", "low", "close"]

    if line_code:
        value_cols.append("line")

    value_cols += [f"bar_{i}" for i in range(1, len(bar_codes) + 1)]

    for col in value_cols:
        chart_df[col] = pd.to_numeric(chart_df[col], errors="coerce")

    chart_df = chart_df.dropna(
        subset=["date", "open", "high", "low", "close"],
        how="any",
    )

    chart_df.columns = chart_df.columns.map(str)

    chart_df = chart_df.sort_values("date")

    return chart_df


def render_exchange_market_chart(
    db: str,
    long_df: pd.DataFrame,
    selected_group_name: str,
) -> None:
    """
    FM08 為替市況用チャートを表示する。

    表示内容:
        上段:
            ローソク足
            必要に応じて中心相場の折れ線

        下段:
            スポット出来高
            スワップ出来高
    """

    try:
        group_config = get_exchange_market_group_config(
            db=db,
            selected_group_name=selected_group_name,
        )

        chart_df = make_exchange_market_df(
            long_df=long_df,
            group_config=group_config,
        )

    except Exception as e:
        st.error("為替市況チャート用データの作成に失敗しました。")
        st.exception(e)
        return

    if chart_df.empty:
        st.warning("ローソク足チャートとして表示できるデータがありません。")
        return

    fields = group_config["fields"]

    line_code = fields.get("line")
    line_label = fields.get("line_label") or "中心相場"

    bar_codes = fields.get("bars", [])
    bar_labels = fields.get("bar_labels", {})

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

    # 上段: ローソク足
    fig.add_trace(
        go.Candlestick(
            x=chart_df["date"],
            open=chart_df["open"],
            high=chart_df["high"],
            low=chart_df["low"],
            close=chart_df["close"],
            name=f"{selected_group_name} OHLC",
        ),
        row=1,
        col=1,
    )

    # 上段: 中心相場の折れ線
    # ユーロドル市況のように line が None の場合は表示しない
    if line_code and "line" in chart_df.columns:
        fig.add_trace(
            go.Scatter(
                x=chart_df["date"],
                y=chart_df["line"],
                mode="lines+markers",
                name=line_label,
            ),
            row=1,
            col=1,
        )

    # 下段: 出来高棒グラフ
    for i, bar_code in enumerate(bar_codes, start=1):
        bar_col = f"bar_{i}"

        if bar_col not in chart_df.columns:
            continue

        bar_label = bar_labels.get(bar_code, bar_code)

        fig.add_trace(
            go.Bar(
                x=chart_df["date"],
                y=chart_df[bar_col],
                name=bar_label,
            ),
            row=2,
            col=1,
        )

    fig.update_layout(
        title=selected_group_name,
        yaxis_title="為替レート",
        yaxis2_title="出来高",
        hovermode="x unified",
        barmode="group",
        xaxis_rangeslider_visible=False,
        legend_title="系列",
        height=700,
    )

    # 上段の横軸
    fig.update_xaxes(
        type="date",
        tickformat="%Y-%m-%d",
        hoverformat="%Y-%m-%d",
        dtick=24 * 60 * 60 * 1000,
        tickangle=-45,
        row=1,
        col=1,
    )

    # 下段の横軸
    fig.update_xaxes(
        type="date",
        tickformat="%Y-%m-%d",
        hoverformat="%Y-%m-%d",
        dtick=24 * 60 * 60 * 1000,
        tickangle=-45,
        title_text="日付",
        row=2,
        col=1,
    )

    st.plotly_chart(fig, width="stretch")
