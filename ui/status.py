import streamlit as st


def render_api_status(payload: dict) -> None:
    """APIレスポンスのステータス情報を表示する"""

    status_col1, status_col2, status_col3 = st.columns(3)

    with status_col1:
        st.metric("STATUS", payload.get("STATUS"))

    with status_col2:
        st.metric("MESSAGEID", payload.get("MESSAGEID"))

    with status_col3:
        st.metric("系列数", len(payload.get("RESULTSET", [])))

    message = payload.get("MESSAGE")
    if message:
        st.caption(f"API MESSAGE：{message}")


def render_api_summary(payload: dict) -> None:
    """APIレスポンスの概要を表示する"""

    with st.expander("APIレスポンスの概要"):
        st.json(
            {
                "STATUS": payload.get("STATUS"),
                "MESSAGEID": payload.get("MESSAGEID"),
                "MESSAGE": payload.get("MESSAGE"),
                "DATE": payload.get("DATE"),
                "PARAMETER": payload.get("PARAMETER"),
                "NEXTPOSITION": payload.get("NEXTPOSITION"),
            }
        )
