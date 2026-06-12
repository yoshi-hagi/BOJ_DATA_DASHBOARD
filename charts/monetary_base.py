import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from config import SERIES_GROUPS


def get_monetary_base_group_config(
    db: str,
    selected_group_name: str,
) -> dict:
    """
    マネタリーベースチャート用の系列グループ設定を取得する。
    """

    group_config = SERIES_GROUPS.get(db, {}).get(selected_group_name)

    if not group_config:
        raise ValueError(
            f"系列グループ設定が見つかりません: {db} / {selected_group_name}"
        )

    if group_config.get("chart_type") != "monetary_base":
        raise ValueError(
            f"マネタリーベースチャート用のグループではありません: {selected_group_name}"
        )

    return group_config


def detect_date_column(long_df: pd.DataFrame) -> str:
    """
    long_df から時点列を判定する。
    """

    if "SURVEY_DATE" in long_df.columns:
        return "SURVEY_DATE"

    if "SURVEY_DATE_LABEL" in long_df.columns:
        return "SURVEY_DATE_LABEL"

    raise ValueError(
        "時点列がありません: SURVEY_DATE または SURVEY_DATE_LABEL が必要です。"
    )


def convert_to_datetime(series: pd.Series) -> pd.Series:
    """
    YYYY / YYYYMM / YYYYMMDD / YYYY-MM-DD の形式に対応して datetime に変換する。
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

    mask = converted.isna()
    if mask.any():
        converted.loc[mask] = pd.to_datetime(
            date_values.loc[mask],
            format="%Y",
            errors="coerce",
        )

    return converted


def make_monetary_base_df(
    long_df: pd.DataFrame,
    group_config: dict,
) -> pd.DataFrame:
    """
    マネタリーベース用の縦持ちデータを、チャート用の横持ちデータに変換する。

    変換後の列:
        date_raw: 元の時点文字列
        date: datetime型の時点
        total: マネタリーベース平均残高
        component_1: 日本銀行券発行高
        component_2: 貨幣流通高
        component_3: 日銀当座預金
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

    total_code = fields["total"]
    component_codes = fields.get("components", [])

    required_codes = [total_code] + component_codes

    chart_df = long_df.pivot_table(
        index=date_col,
        columns="SERIES_CODE",
        values="VALUE",
        aggfunc="first",
    ).reset_index()

    # Streamlit / Arrow の mixed column type 警告対策
    chart_df.columns = chart_df.columns.map(str)

    missing_codes = [code for code in required_codes if code not in chart_df.columns]

    if missing_codes:
        raise ValueError(
            "マネタリーベースチャートに必要な系列コードが不足しています: "
            + ", ".join(missing_codes)
        )

    rename_map = {
        date_col: "date_raw",
        total_code: "total",
    }

    for i, component_code in enumerate(component_codes, start=1):
        rename_map[component_code] = f"component_{i}"

    chart_df = chart_df.rename(columns=rename_map)

    chart_df["date"] = convert_to_datetime(chart_df["date_raw"])

    value_cols = ["total"] + [
        f"component_{i}" for i in range(1, len(component_codes) + 1)
    ]

    for col in value_cols:
        chart_df[col] = pd.to_numeric(chart_df[col], errors="coerce")

    chart_df = chart_df.dropna(
        subset=["date", "total"],
        how="any",
    )

    chart_df = chart_df.sort_values("date")

    # 念のため最終列名も文字列化
    chart_df.columns = chart_df.columns.map(str)

    return chart_df


def render_monetary_base_chart(
    db: str,
    long_df: pd.DataFrame,
    selected_group_name: str,
) -> None:
    """
    MD01 マネタリーベースチャートを表示する。

    上段:
        マネタリーベース平均残高の折れ線チャート

    下段:
        内訳3系列の積み上げ面グラフ
    """

    try:
        group_config = get_monetary_base_group_config(
            db=db,
            selected_group_name=selected_group_name,
        )

        chart_df = make_monetary_base_df(
            long_df=long_df,
            group_config=group_config,
        )

    except Exception as e:
        st.error("マネタリーベースチャート用データの作成に失敗しました。")
        st.exception(e)
        return

    if chart_df.empty:
        st.warning("マネタリーベースチャートとして表示できるデータがありません。")
        return

    fields = group_config["fields"]
    labels = fields.get("labels", {})

    total_code = fields["total"]
    component_codes = fields.get("components", [])

    total_label = labels.get(total_code) or labels.get("total", "合計")

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        row_heights=[0.45, 0.55],
        specs=[
            [{"secondary_y": False}],
            [{"secondary_y": False}],
        ],
    )

    # 上段: 合計の折れ線
    fig.add_trace(
        go.Scatter(
            x=chart_df["date"],
            y=chart_df["total"],
            mode="lines+markers",
            name=total_label,
            hovertemplate=(
                "%{x|%Y-%m-%d}<br>" + f"{total_label}: " + "%{y:,.0f}<extra></extra>"
            ),
        ),
        row=1,
        col=1,
    )

    # 下段: 内訳の積み上げ面グラフ
    for i, component_code in enumerate(component_codes, start=1):
        component_col = f"component_{i}"

        if component_col not in chart_df.columns:
            continue

        component_label = labels.get(component_code, component_code)

        fig.add_trace(
            go.Scatter(
                x=chart_df["date"],
                y=chart_df[component_col],
                mode="lines",
                stackgroup="components",
                name=component_label,
                hovertemplate=(
                    "%{x|%Y-%m-%d}<br>"
                    + f"{component_label}: "
                    + "%{y:,.0f}<extra></extra>"
                ),
            ),
            row=2,
            col=1,
        )

    fig.update_layout(
        title=selected_group_name,
        yaxis_title="平均残高",
        yaxis2_title="内訳",
        hovermode="x unified",
        legend_title="系列",
        height=750,
    )

    # 上段の横軸
    fig.update_xaxes(
        type="date",
        tickformat="%Y-%m",
        hoverformat="%Y-%m-%d",
        tickangle=-45,
        row=1,
        col=1,
    )

    # 下段の横軸
    fig.update_xaxes(
        type="date",
        tickformat="%Y-%m",
        hoverformat="%Y-%m-%d",
        tickangle=-45,
        title_text="時点",
        row=2,
        col=1,
    )

    st.plotly_chart(fig, width="stretch")
