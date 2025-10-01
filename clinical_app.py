import sys, os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
import streamlit as st
from login import login_google
from ClinicalEngineer.pages import auto
from ClinicalEngineer.modes import dashboard

def main():
    st.set_page_config(page_title="学習プラットフォーム", layout="wide")
    st.title("📚 学習プラットフォーム")

    # --- ログイン処理 ---
    login_google()
    if "user_id" not in st.session_state:
        st.stop()  # ログインするまでアプリを進めない

    st.sidebar.success(f"ログイン中: {st.session_state['user_id']}")

    # --- ページ切り替え ---
    page = st.sidebar.radio("ページ選択", ["Autoモード", "ダッシュボード"])

    if page == "Autoモード":
        auto.run_auto_mode()
    elif page == "ダッシュボード":
        dashboard.render_dashboard()

if __name__ == "__main__":
    main()
