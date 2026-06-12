import pandas as pd
import streamlit as st

from utils.downloads import make_download_csv
from utils.dataframe import normalize_column_names


def render_data_tabs(
    db: str,
    long_df: pd.DataFrame,
    wide_df: pd.DataFrame,
) -> None:
    """縦持ち・横持ちデータとCSVダウンロードボタンを表示する"""
    long_df = normalize_column_names(long_df)
    wide_df = normalize_column_names(wide_df)

    st.subheader("4. データ")

    tab1, tab2 = st.tabs(["縦持ちデータ", "横持ちデータ"])

    with tab1:
        st.dataframe(long_df, width="stretch", height=400)

        st.download_button(
            label="縦持ちCSVをダウンロード",
            data=make_download_csv(long_df),
            file_name=f"boj_{db}_long.csv",
            mime="text/csv",
        )

    with tab2:
        st.dataframe(wide_df, width="stretch", height=400)

        st.download_button(
            label="横持ちCSVをダウンロード",
            data=make_download_csv(wide_df),
            file_name=f"boj_{db}_wide.csv",
            mime="text/csv",
        )
