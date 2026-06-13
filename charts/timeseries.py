import pandas as pd
import plotly.express as px
import streamlit as st

from charts.call_rate import render_call_rate_chart
from charts.exchange_market import render_exchange_market_chart
from charts.monetary_base import render_monetary_base_chart
from charts.tankan_actual_forecast import render_tankan_actual_forecast_chart
from config import SERIES_GROUPS
from ui.tankan_series_groups import build_tankan_actual_forecast_presets
from charts.depositor_deposits import render_depositor_deposits_chart


def render_line_chart(long_df: pd.DataFrame) -> None:
    """標準の時系列折れ線グラフを表示する"""

    fig = px.line(
        long_df,
        x="SURVEY_DATE_LABEL",
        y="VALUE",
        color="NAME_OF_TIME_SERIES_J",
        markers=True,
        hover_data={
            "SERIES_CODE": True,
            "UNIT_J": True,
            "FREQUENCY": True,
            "VALUE": ":,.4f",
        },
        title="選択系列の時系列推移",
    )

    fig.update_layout(
        xaxis_title="時点",
        yaxis_title="値",
        legend_title="系列",
        hovermode="x unified",
    )

    st.plotly_chart(fig, use_container_width=True)


def get_selected_group_config(
    db: str,
    selected_group_name: str | None,
    series_df: pd.DataFrame | None = None,
) -> dict | None:
    """選択された系列グループの設定を取得する"""

    if not selected_group_name:
        return None

    group_config = SERIES_GROUPS.get(db, {}).get(selected_group_name)

    if group_config:
        return group_config

    if db == "CO" and series_df is not None:
        tankan_groups = build_tankan_actual_forecast_presets(series_df)
        return tankan_groups.get(selected_group_name)

    return None


def render_chart(
    db: str,
    long_df: pd.DataFrame,
    selected_group_name: str | None = None,
    series_df: pd.DataFrame | None = None,
) -> None:
    """
    DB・系列グループ別にグラフを切り替える。
    """

    group_config = get_selected_group_config(
        db=db,
        selected_group_name=selected_group_name,
        series_df=series_df,
    )

    if group_config and group_config.get("chart_type") == "exchange_market":
        render_exchange_market_chart(
            db=db,
            long_df=long_df,
            selected_group_name=selected_group_name,
        )
        return

    if group_config and group_config.get("chart_type") == "call_rate":
        render_call_rate_chart(
            db=db,
            long_df=long_df,
            selected_group_name=selected_group_name,
        )
        return

    if group_config and group_config.get("chart_type") == "monetary_base":
        render_monetary_base_chart(
            db=db,
            long_df=long_df,
            selected_group_name=selected_group_name,
        )
        return

    if group_config and group_config.get("chart_type") == "tankan_actual_forecast":
        render_tankan_actual_forecast_chart(
            long_df=long_df,
            selected_group_name=selected_group_name,
        )
        return

    if group_config and group_config.get("chart_type") == "depositor_deposits":
        render_depositor_deposits_chart(
            db=db,
            long_df=long_df,
            selected_group_name=selected_group_name,
        )
        return

    render_line_chart(long_df)
