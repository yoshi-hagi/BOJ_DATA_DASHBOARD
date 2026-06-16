import re

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from config import SERIES_GROUPS


def get_balance_of_payments_group_config(
    db: str,
    selected_group_name: str,
) -> dict:
    """
    国際収支統計チャート用の系列グループ設定を取得する。
    """

    group_config = SERIES_GROUPS.get(db, {}).get(selected_group_name)

    if not group_config:
        raise ValueError(
            f"系列グループ設定が見つかりません: {db} / {selected_group_name}"
        )

    return group_config


def detect_period_column(long_df: pd.DataFrame) -> str:
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


def normalize_period_value(value: object) -> str | None:
    """
    時点値を正規化する。

    想定:
        202501
        202501.0
        2025-01
        2025/01
        20250131
        2025-01-31
    """

    if pd.isna(value):
        return None

    text = str(value).strip()

    # 202501.0 のような値を 202501 に戻す
    if re.fullmatch(r"\d+\.0", text):
        text = text[:-2]

    # 数字だけ取り出す
    digits = re.sub(r"\D", "", text)

    if len(digits) == 4:
        return digits

    if len(digits) == 6:
        return digits

    if len(digits) == 8:
        return digits

    return None


def period_to_datetime(period: str | None) -> pd.Timestamp | None:
    """
    YYYY / YYYYMM / YYYYMMDD を datetime に変換する。
    """

    if period is None:
        return pd.NaT

    if len(period) == 4:
        return pd.to_datetime(period, format="%Y", errors="coerce")

    if len(period) == 6:
        return pd.to_datetime(period, format="%Y%m", errors="coerce")

    if len(period) == 8:
        return pd.to_datetime(period, format="%Y%m%d", errors="coerce")

    return pd.NaT


def period_to_label(period: str | None) -> str | None:
    """
    グラフ横軸用のカテゴリラベルを作る。
    """

    if period is None:
        return None

    if len(period) == 4:
        return period

    if len(period) == 6:
        return f"{period[:4]}-{period[4:6]}"

    if len(period) == 8:
        return f"{period[:4]}-{period[4:6]}-{period[6:8]}"

    return period


def make_current_account_df(
    long_df: pd.DataFrame,
    group_config: dict,
) -> pd.DataFrame:
    """
    経常収支用の縦持ちデータを、チャート用の横持ちデータに変換する。

    重要:
        total が欠損していても、内訳が存在する時点は残す。
        月次データは date 軸ではなく x_label のカテゴリ軸で表示する。
    """

    long_df = long_df.copy()
    long_df.columns = long_df.columns.map(str)

    required_cols = ["SERIES_CODE", "VALUE"]

    missing_cols = [col for col in required_cols if col not in long_df.columns]
    if missing_cols:
        raise ValueError(f"必要な列がありません: {missing_cols}")

    long_df["SERIES_CODE"] = long_df["SERIES_CODE"].astype(str)

    period_col = detect_period_column(long_df)

    fields = group_config["fields"]

    total_code = fields["total"]
    component_codes = fields.get("components", [])

    required_codes = [total_code] + component_codes

    chart_df = long_df.pivot_table(
        index=period_col,
        columns="SERIES_CODE",
        values="VALUE",
        aggfunc="first",
        dropna=False,
    ).reset_index()

    chart_df.columns = chart_df.columns.map(str)

    missing_codes = [code for code in required_codes if code not in chart_df.columns]

    if missing_codes:
        raise ValueError(
            "経常収支チャートに必要な系列コードが不足しています: "
            + ", ".join(missing_codes)
        )

    rename_map = {
        period_col: "period_raw",
        total_code: "total",
    }

    for i, component_code in enumerate(component_codes, start=1):
        rename_map[component_code] = f"component_{i}"

    chart_df = chart_df.rename(columns=rename_map)

    chart_df["period"] = chart_df["period_raw"].map(normalize_period_value)
    chart_df["date"] = chart_df["period"].map(period_to_datetime)
    chart_df["x_label"] = chart_df["period"].map(period_to_label)

    value_cols = ["total"] + [
        f"component_{i}" for i in range(1, len(component_codes) + 1)
    ]

    for col in value_cols:
        chart_df[col] = pd.to_numeric(chart_df[col], errors="coerce")

    # date が作れない行だけ落とす
    chart_df = chart_df.dropna(subset=["date"])

    # total だけを基準に落とさない。
    # 経常収支本体が欠損していても、内訳が存在する月は残す。
    chart_df = chart_df.dropna(
        subset=value_cols,
        how="all",
    )

    chart_df = chart_df.sort_values("date")

    chart_df.columns = chart_df.columns.map(str)

    return chart_df


def make_bop_summary_df(
    long_df: pd.DataFrame,
    group_config: dict,
) -> pd.DataFrame:
    """
    国際収支統計のサマリ系プリセット用データを作成する。

    想定:
        上段: total の折れ線
        下段: components の積み上げ棒グラフ

    重要:
        total が欠損していても、components が存在する時点は残す。
        月次データは x_label のカテゴリ軸で表示する。
    """

    long_df = long_df.copy()
    long_df.columns = long_df.columns.map(str)

    required_cols = ["SERIES_CODE", "VALUE"]

    missing_cols = [col for col in required_cols if col not in long_df.columns]
    if missing_cols:
        raise ValueError(f"必要な列がありません: {missing_cols}")

    long_df["SERIES_CODE"] = long_df["SERIES_CODE"].astype(str)

    period_col = detect_period_column(long_df)

    fields = group_config["fields"]

    total_code = fields["total"]
    component_codes = fields.get("components", [])
    negative_components = set(fields.get("negative_components", []))

    required_codes = [total_code] + component_codes

    chart_df = long_df.pivot_table(
        index=period_col,
        columns="SERIES_CODE",
        values="VALUE",
        aggfunc="first",
        dropna=False,
    ).reset_index()

    chart_df.columns = chart_df.columns.map(str)

    missing_codes = [code for code in required_codes if code not in chart_df.columns]

    if missing_codes:
        st.warning(
            "一部の系列コードが取得結果に含まれていないため、"
            "取得できた系列だけでチャートを作成します。"
        )
    st.code(", ".join(missing_codes))

    available_component_codes = [
        code for code in component_codes if code in chart_df.columns
    ]

    if total_code not in chart_df.columns:
        raise ValueError("合計系列が取得結果に含まれていません: " + total_code)

    rename_map = {
        period_col: "period_raw",
        total_code: "total",
    }

    component_col_map: dict[str, str] = {}

    for i, component_code in enumerate(available_component_codes, start=1):
        component_col = f"component_{i}"
        rename_map[component_code] = component_col
        component_col_map[component_code] = component_col

    chart_df = chart_df.rename(columns=rename_map)

    chart_df["period"] = chart_df["period_raw"].map(normalize_period_value)
    chart_df["date"] = chart_df["period"].map(period_to_datetime)
    chart_df["x_label"] = chart_df["period"].map(period_to_label)

    value_cols = ["total"] + [
        f"component_{i}" for i in range(1, len(available_component_codes) + 1)
    ]

    for col in value_cols:
        chart_df[col] = pd.to_numeric(chart_df[col], errors="coerce")

    # 表示用に、指定系列だけ符号を反転する
    for component_code in negative_components:
        component_col = component_col_map.get(component_code)

        if component_col and component_col in chart_df.columns:
            chart_df[component_col] = chart_df[component_col] * -1

    chart_df = chart_df.dropna(subset=["date"])

    # total だけを基準に行を落とさない
    chart_df = chart_df.dropna(
        subset=value_cols,
        how="all",
    )

    chart_df = chart_df.sort_values("date")

    chart_df.columns = chart_df.columns.map(str)

    chart_df.attrs["component_codes"] = available_component_codes

    return chart_df


def render_bop_summary_chart(
    db: str,
    long_df: pd.DataFrame,
    selected_group_name: str,
) -> None:
    """
    国際収支統計のサマリ系チャートを表示する。

    上段:
        total の折れ線グラフ

    下段:
        components の積み上げ棒グラフ
    """

    try:
        group_config = get_balance_of_payments_group_config(
            db=db,
            selected_group_name=selected_group_name,
        )

        chart_df = make_bop_summary_df(
            long_df=long_df,
            group_config=group_config,
        )

    except Exception as e:
        st.error("国際収支チャート用データの作成に失敗しました。")
        st.exception(e)
        return

    if chart_df.empty:
        st.warning("国際収支チャートとして表示できるデータがありません。")
        return

    fields = group_config["fields"]
    labels = fields.get("labels", {})

    total_code = fields["total"]
    component_codes = chart_df.attrs.get(
        "component_codes",
        fields.get("components", []),
    )

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

    # 上段: 合計系列の折れ線
    fig.add_trace(
        go.Scatter(
            x=chart_df["x_label"],
            y=chart_df["total"],
            mode="lines+markers",
            name=total_label,
            connectgaps=False,
            hovertemplate=(
                "%{x}<br>" + f"{total_label}: " + "%{y:,.0f}<extra></extra>"
            ),
        ),
        row=1,
        col=1,
    )

    # 下段: 内訳の積み上げ棒グラフ
    for i, component_code in enumerate(component_codes, start=1):
        component_col = f"component_{i}"

        if component_col not in chart_df.columns:
            continue

        component_label = labels.get(component_code, component_code)

        fig.add_trace(
            go.Bar(
                x=chart_df["x_label"],
                y=chart_df[component_col],
                name=component_label,
                width=0.75,
                hovertemplate=(
                    "%{x}<br>" + f"{component_label}: " + "%{y:,.0f}<extra></extra>"
                ),
            ),
            row=2,
            col=1,
        )

    fig.update_layout(
        title=selected_group_name,
        yaxis_title=total_label,
        yaxis2_title="内訳",
        hovermode="x unified",
        barmode="relative",
        xaxis_rangeslider_visible=False,
        legend_title="系列",
        height=750,
    )

    fig.update_xaxes(
        type="category",
        tickangle=-45,
        row=1,
        col=1,
    )

    fig.update_xaxes(
        type="category",
        tickangle=-45,
        title_text="時点",
        row=2,
        col=1,
    )

    st.plotly_chart(fig, use_container_width=True)


def render_current_account_chart(
    db: str,
    long_df: pd.DataFrame,
    selected_group_name: str,
) -> None:
    """
    BP01 経常収支チャートを表示する。
    """

    render_bop_summary_chart(
        db=db,
        long_df=long_df,
        selected_group_name=selected_group_name,
    )


def render_trade_services_chart(
    db: str,
    long_df: pd.DataFrame,
    selected_group_name: str,
) -> None:
    """
    BP01 貿易・サービス収支チャートを表示する。
    """

    render_bop_summary_chart(
        db=db,
        long_df=long_df,
        selected_group_name=selected_group_name,
    )
