import pandas as pd
import streamlit as st

from job_api_functions import (
    get_all_boj_data,
    get_series_code,
    resultset_to_df,
    resultset_to_long_df,
)
from utils.dataframe import normalize_column_names


@st.cache_data(ttl=60 * 60)
def load_series_master(db: str) -> pd.DataFrame:
    """メタデータを取得してキャッシュする"""
    df = get_series_code(db)
    return normalize_column_names(df)


@st.cache_data(ttl=60 * 10)
def load_boj_data(
    db: str,
    codes: list[str],
    start_date: str,
    end_date: str,
) -> dict:
    """時系列データを取得してキャッシュする"""
    return get_all_boj_data(
        db=db,
        codes=codes,
        start_date=start_date,
        end_date=end_date,
        lang="jp",
        sleep_sec=1.0,
    )


def convert_payload_to_dataframes(payload: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    """APIレスポンスを横持ち・縦持ちDataFrameに変換する"""
    wide_df = resultset_to_df(payload)
    long_df = resultset_to_long_df(payload)

    wide_df = normalize_column_names(wide_df)
    long_df = normalize_column_names(long_df)

    return wide_df, long_df
