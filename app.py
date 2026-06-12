import streamlit as st

from charts.timeseries import render_chart
from config import BOJ_CREDIT
from services.boj_service import (
    convert_payload_to_dataframes,
    load_boj_data,
    load_series_master,
)
from ui.data_view import render_data_tabs
from ui.series_selector import (
    render_series_selector,
    validate_selected_frequency,
)
from ui.sidebar import render_sidebar
from ui.status import render_api_status, render_api_summary

st.set_page_config(
    page_title="日銀統計データダッシュボード",
    page_icon="📈",
    layout="wide",
)


def main() -> None:
    st.title("📈 日銀統計データダッシュボード")
    st.caption(
        "日本銀行 時系列統計データ検索サイト API を利用したサンプルダッシュボード"
    )
    st.caption(BOJ_CREDIT)
    st.divider()

    db, start_date, end_date = render_sidebar()

    try:
        series_df = load_series_master(db)

    except Exception as e:
        st.error("メタデータの取得に失敗しました。")
        st.exception(e)
        return

    if series_df.empty:
        st.warning("系列コードが取得できませんでした。")
        return

    # selected_group_configはひとまず使わないのでアンダースコアで受ける
    selected_codes, selected_group_name, _ = render_series_selector(
        db=db,
        series_df=series_df,
    )

    if not selected_codes:
        return

    if not validate_selected_frequency(series_df, selected_codes):
        return

    st.subheader("2. データ取得")

    fetch_button = st.button("データを取得", type="primary")

    if not fetch_button:
        return

    try:
        with st.spinner("日銀APIからデータを取得しています..."):
            payload = load_boj_data(
                db=db,
                codes=selected_codes,
                start_date=start_date,
                end_date=end_date,
            )

        wide_df, long_df = convert_payload_to_dataframes(payload)

    except Exception as e:
        st.error("データ取得に失敗しました。")
        st.exception(e)
        return

    if wide_df.empty or long_df.empty:
        st.warning("取得できるデータがありませんでした。")
        return

    st.success("データ取得が完了しました。")

    render_api_status(payload)

    st.subheader("3. グラフ")
    render_chart(
        db=db,
        long_df=long_df,
        selected_group_name=selected_group_name,
        series_df=series_df,
    )

    render_data_tabs(
        db=db,
        long_df=long_df,
        wide_df=wide_df,
    )

    render_api_summary(payload)

    # st.divider()
    # st.caption(BOJ_CREDIT)


if __name__ == "__main__":
    main()
