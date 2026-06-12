import pandas as pd
import plotly.graph_objects as go
import streamlit as st


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
    YYYY / YYYYMM / YYYYMMDD / YYYY-MM-DD に対応して datetime に変換する。
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


def classify_tankan_series(series_code: str) -> str | None:
    """
    CO系列コードから実績/予測を判定する。

    右から5桁目:
        0 -> actual
        1 -> forecast
    """

    code = str(series_code)

    if len(code) < 5:
        return None

    flag = code[-5]

    if flag == "0":
        return "actual"

    if flag == "1":
        return "forecast"

    return None


def make_tankan_actual_forecast_df(long_df: pd.DataFrame) -> pd.DataFrame:
    """
    実績・予測ペアの縦持ちデータをチャート用に整形する。
    """

    df = long_df.copy()
    df.columns = df.columns.map(str)

    required_cols = ["SERIES_CODE", "VALUE"]

    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"必要な列がありません: {missing_cols}")

    date_col = detect_date_column(df)

    df["SERIES_CODE"] = df["SERIES_CODE"].astype(str)
    df["TANKAN_CLASS"] = df["SERIES_CODE"].map(classify_tankan_series)
    df["VALUE"] = pd.to_numeric(df["VALUE"], errors="coerce")
    df["date"] = convert_to_datetime(df[date_col])

    df = df.dropna(
        subset=[
            "date",
            "VALUE",
            "TANKAN_CLASS",
        ]
    )

    df = df.sort_values(["date", "TANKAN_CLASS"])

    return df


def render_tankan_actual_forecast_chart(
    long_df: pd.DataFrame,
    selected_group_name: str,
) -> None:
    """
    CO 短観の実績・予測ペアを表示する。

    表示内容:
        実績: 折れ線
        予測: 折れ線
    """

    try:
        chart_df = make_tankan_actual_forecast_df(long_df)

    except Exception as e:
        st.error("短観 実績・予測チャート用データの作成に失敗しました。")
        st.exception(e)
        return

    if chart_df.empty:
        st.warning("短観 実績・予測チャートとして表示できるデータがありません。")
        return

    label_map = {
        "actual": "実績",
        "forecast": "予測",
    }

    fig = go.Figure()

    for class_name in ["actual", "forecast"]:
        plot_df = chart_df[chart_df["TANKAN_CLASS"] == class_name]

        if plot_df.empty:
            continue

        fig.add_trace(
            go.Scatter(
                x=plot_df["date"],
                y=plot_df["VALUE"],
                mode="lines+markers",
                name=label_map[class_name],
                customdata=plot_df[["SERIES_CODE"]],
                hovertemplate=(
                    "%{x|%Y-%m-%d}<br>"
                    f"{label_map[class_name]}: "
                    "%{y:,.1f}<br>"
                    "系列コード: %{customdata[0]}"
                    "<extra></extra>"
                ),
            )
        )

    fig.update_layout(
        title=selected_group_name,
        xaxis_title="時点",
        yaxis_title="値",
        hovermode="x unified",
        legend_title="分類",
        height=600,
    )

    fig.update_xaxes(
        type="date",
        tickformat="%Y-%m",
        hoverformat="%Y-%m-%d",
        tickangle=-45,
    )

    st.plotly_chart(fig, use_container_width=True)
