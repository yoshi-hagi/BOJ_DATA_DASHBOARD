from datetime import datetime
import streamlit as st
from config import DB_OPTIONS


def render_sidebar() -> tuple[str, str, str]:
    """サイドバーを表示し、検索条件を返す"""

    with st.sidebar:
        st.header("検索条件")

        db = st.selectbox(
            "DBを選択",
            options=list(DB_OPTIONS.keys()),
            format_func=lambda x: f"{x}：{DB_OPTIONS[x]}",
            index=0,
        )

        st.divider()

        today = datetime.today()

        default_start_date = f"{today.year}01"
        default_end_date = today.strftime("%Y%m")

        start_date = st.text_input(
            "開始期",
            value=default_start_date,
            help=(
                "例：月次は 202501、四半期は 202501、"
                "年度・暦年は 2025 のように指定します。"
            ),
        )

        end_date = st.text_input(
            "終了期",
            value=default_end_date,
            help="例：月次は 202512、四半期は 202504 のように指定します。",
        )

        st.divider()

        st.info(
            "コードAPIでは、複数系列を指定する場合、同じ期種の系列だけを指定してください。"
        )

    return db, start_date, end_date
