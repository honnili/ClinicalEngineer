# modes/diagram.py
import streamlit as st
from services.diagram_utils import generate_diagram

def render():
    st.subheader("図解問題")
    mode = st.radio("モード", ["閲覧", "解答"])

    if mode == "閲覧":
        topic = st.text_input("図解テーマ（例：人工呼吸器アラーム対応フロー）", "人工呼吸器アラーム対応フロー")
        field = st.selectbox("分野", ["呼吸療法装置", "人工心肺装置", "透析装置", "医用電気機器"])
        if st.button("図解を生成"):
            generate_diagram("図解閲覧", topic, field)
    else:
        st.write("図を見て解答（採点ロジックは後で追加可能）")
        st.info("今は図解表示のみ。採点は次のスプリントで実装予定。")