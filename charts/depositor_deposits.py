import re

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from config import SERIES_GROUPS


def get_depositor_deposits_group_config(
    db: str,
    selected_group_name: str,
) -> dict:
    """
    預金者別預金チャート用の系列グループ設定を取得する。
    """

    group_config = SERIES_GROUPS.get(db, {}).get(selected_group_name)

    if not group_config:
        raise ValueError(
            f"系列グループ設定が見つかりません: {db} / {selected_group_name}"
        )

    if group_config.get("chart_type") != "depositor_deposits":
        raise ValueError(
            f"預金者別預金チャート用のグループではありません: {selected_group_name}"
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


def is_quarterly_data(long_df: pd.DataFrame) -> bool:
    """
    FREQUENCY列から四半期データかどうかを判定する。
    """

    if "FREQUENCY" not in long_df.columns:
        return False

    frequency_values = (
        long_df["FREQUENCY"].dropna().astype(str).str.upper().unique().tolist()
    )

    return any("QUARTER" in value or value == "Q" for value in frequency_values)


def convert_boj_period_to_datetime(
    series: pd.Series,
    quarterly: bool = False,
) -> pd.Series:
    """
    日銀APIの時点表記を datetime に変換する。

    対応形式:
        YYYY
        YYYYMM
        YYYYMMDD
        YYYY-MM-DD

    四半期データの場合:
        YYYY01 -> 第1四半期開始月
        YYYY02 -> 第2四半期開始月
        YYYY03 -> 第3四半期開始月
        YYYY04 -> 第4四半期開始月
    """

    values = series.astype(str).str.strip()

    result = pd.Series(pd.NaT, index=values.index, dtype="datetime64[ns]")

    quarter_month_map = {
        "01": "01",
        "02": "04",
        "03": "07",
        "04": "10",
    }

    for idx, value in values.items():
        if not value or value.lower() == "nan":
            continue

        # YYYY01〜YYYY04 を四半期として扱う
        if quarterly and re.fullmatch(r"\d{6}", value):
            year = value[:4]
            quarter = value[4:6]

            if quarter in quarter_month_map:
                result.loc[idx] = pd.to_datetime(
                    f"{year}{quarter_month_map[quarter]}01",
                    format="%Y%m%d",
                    errors="coerce",
                )
                continue

        if re.fullmatch(r"\d{8}", value):
            result.loc[idx] = pd.to_datetime(
                value,
                format="%Y%m%d",
                errors="coerce",
            )
            continue

        if re.fullmatch(r"\d{6}", value):
            result.loc[idx] = pd.to_datetime(
                value,
                format="%Y%m",
                errors="coerce",
            )
            continue

        if re.fullmatch(r"\d{4}", value):
            result.loc[idx] = pd.to_datetime(
                value,
                format="%Y",
                errors="coerce",
            )
            continue

        result.loc[idx] = pd.to_datetime(value, errors="coerce")

    return result


def build_series_label_map(long_df: pd.DataFrame) -> dict[str, str]:
    """
    SERIES_CODE -> 系列名 の辞書を作る。

    NAME_OF_TIME_SERIES_J がある場合はそれを凡例に使い、
    なければ系列コードをそのまま使う。
    """

    if "SERIES_CODE" not in long_df.columns:
        return {}

    if "NAME_OF_TIME_SERIES_J" not in long_df.columns:
        return {
            str(code): str(code)
            for code in long_df["SERIES_CODE"].dropna().astype(str).unique()
        }

    label_df = (
        long_df[["SERIES_CODE", "NAME_OF_TIME_SERIES_J"]]
        .dropna(subset=["SERIES_CODE"])
        .copy()
    )

    label_df["SERIES_CODE"] = label_df["SERIES_CODE"].astype(str)
    label_df["NAME_OF_TIME_SERIES_J"] = label_df["NAME_OF_TIME_SERIES_J"].astype(str)

    label_map = (
        label_df.drop_duplicates("SERIES_CODE")
        .set_index("SERIES_CODE")["NAME_OF_TIME_SERIES_J"]
        .to_dict()
    )

    return label_map


def make_depositor_deposits_df(
    long_df: pd.DataFrame,
    group_config: dict,
) -> tuple[pd.DataFrame, dict[str, str]]:
    """
    預金者別預金用の縦持ちデータをチャート用の横持ちデータに変換する。

    変換後の列:
        date_raw
        date
        bar_1, bar_2, ...
        line
    """

    long_df = long_df.copy()
    long_df.columns = long_df.columns.map(str)

    required_cols = ["SERIES_CODE", "VALUE"]

    missing_cols = [col for col in required_cols if col not in long_df.columns]
    if missing_cols:
        raise ValueError(f"必要な列がありません: {missing_cols}")

    long_df["SERIES_CODE"] = long_df["SERIES_CODE"].astype(str)

    date_col = detect_date_column(long_df)
    quarterly = is_quarterly_data(long_df)

    fields = group_config["fields"]

    bar_codes = fields.get("bars", [])
    line_code = fields["line"]

    required_codes = bar_codes + [line_code]

    label_map = build_series_label_map(long_df)

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
            "預金者別預金チャートに必要な系列コードが不足しています: "
            + ", ".join(missing_codes)
        )

    rename_map = {
        date_col: "date_raw",
        line_code: "line",
    }

    for i, bar_code in enumerate(bar_codes, start=1):
        rename_map[bar_code] = f"bar_{i}"

    chart_df = chart_df.rename(columns=rename_map)

    chart_df["date"] = convert_boj_period_to_datetime(
        chart_df["date_raw"],
        quarterly=quarterly,
    )

    value_cols = ["line"] + [f"bar_{i}" for i in range(1, len(bar_codes) + 1)]

    for col in value_cols:
        chart_df[col] = pd.to_numeric(chart_df[col], errors="coerce")

    # 半期作成データ対策:
    # VALUE が 0 のデータはチャート対象から除外する。
    # ここでは、棒グラフ系列・折れ線系列の全てが 0 または欠損の時点を除外する。
    non_zero_mask = chart_df[value_cols].fillna(0).ne(0).any(axis=1)
    chart_df = chart_df[non_zero_mask]

    chart_df = chart_df.dropna(
        subset=["date"],
        how="any",
    )

    chart_df = chart_df.sort_values("date")

    # 念のため最終列名も文字列化
    chart_df.columns = chart_df.columns.map(str)

    return chart_df, label_map


def render_depositor_deposits_chart(
    db: str,
    long_df: pd.DataFrame,
    selected_group_name: str,
) -> None:
    """
    MD10 預金者別預金チャートを表示する。

    上段:
        内訳系列の積み上げ棒グラフ

    下段:
        合計系列の折れ線グラフ
    """

    try:
        group_config = get_depositor_deposits_group_config(
            db=db,
            selected_group_name=selected_group_name,
        )

        chart_df, label_map = make_depositor_deposits_df(
            long_df=long_df,
            group_config=group_config,
        )

    except Exception as e:
        st.error("預金者別預金チャート用データの作成に失敗しました。")
        st.exception(e)
        return

    if chart_df.empty:
        st.warning("預金者別預金チャートとして表示できるデータがありません。")
        return

    fields = group_config["fields"]

    bar_codes = fields.get("bars", [])
    line_code = fields["line"]

    line_label = fields.get("line_label") or label_map.get(line_code, line_code)

    top_yaxis_title = fields.get("top_yaxis_title", "内訳")
    bottom_yaxis_title = fields.get("bottom_yaxis_title", "合計")

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        row_heights=[0.6, 0.4],
        specs=[
            [{"secondary_y": False}],
            [{"secondary_y": False}],
        ],
    )

    # 上段: 積み上げ棒グラフ
    for i, bar_code in enumerate(bar_codes, start=1):
        bar_col = f"bar_{i}"

        if bar_col not in chart_df.columns:
            continue

        bar_label = label_map.get(bar_code, bar_code)

        fig.add_trace(
            go.Bar(
                x=chart_df["date"],
                y=chart_df[bar_col],
                name=bar_label,
                hovertemplate=(
                    "%{x|%Y-%m-%d}<br>" + f"{bar_label}: " + "%{y:,.0f}<extra></extra>"
                ),
            ),
            row=1,
            col=1,
        )

    # 下段: 合計の折れ線グラフ
    fig.add_trace(
        go.Scatter(
            x=chart_df["date"],
            y=chart_df["line"],
            mode="lines+markers",
            name=line_label,
            hovertemplate=(
                "%{x|%Y-%m-%d}<br>" + f"{line_label}: " + "%{y:,.0f}<extra></extra>"
            ),
        ),
        row=2,
        col=1,
    )

    fig.update_layout(
        title=selected_group_name,
        barmode="stack",
        hovermode="x unified",
        legend_title="系列",
        height=750,
    )

    fig.update_yaxes(
        title_text=top_yaxis_title,
        row=1,
        col=1,
    )

    fig.update_yaxes(
        title_text=bottom_yaxis_title,
        row=2,
        col=1,
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

    st.plotly_chart(fig, use_container_width=True)
