# modes/manual.py
import streamlit as st

def render():
    st.subheader("マニュアル（参照／演習）")
    tab1, tab2 = st.tabs(["参照", "演習"])
    with tab1:
        device = st.text_input("装置名", "ICU Ventilator")
        st.write(f"{device} の仕組み・操作手順（マニュアル本文は後で追加）")
    with tab2:
        st.write("手順に基づく演習問題（採点は後で追加）")