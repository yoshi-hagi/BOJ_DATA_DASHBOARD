import pandas as pd


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    DataFrameの列名をすべて文字列に統一する。

    Streamlit内部のArrow変換で、
    column names of mixed type の警告が出るのを防ぐ。
    """

    df = df.copy()
    df.columns = df.columns.map(str)
    return df
