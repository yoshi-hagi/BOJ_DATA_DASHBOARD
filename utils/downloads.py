import io
import pandas as pd


def make_download_csv(df: pd.DataFrame) -> bytes:
    """DataFrameをCSV bytesに変換"""
    buffer = io.StringIO()
    df.to_csv(buffer, index=False, encoding="utf-8-sig")
    return buffer.getvalue().encode("utf-8-sig")
