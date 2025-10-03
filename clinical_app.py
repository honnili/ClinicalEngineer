import streamlit as st
from services.db_utils import init_db
from services.auth_utils import login_google
from modes import daily, boss, diagram, manual, notes, practice, company
from modes import review, scenario_auto, scenario_rpg
from modes import dashboard, weakpoints


st.set_page_config(page_title="臨床工学技士シミュレーター", layout="wide")
init_db()

def main():
    # --- ログイン処理 ---
    login_google()

    if "user_id" not in st.session_state:
        st.info("未ログインです")
        return

    st.success(f"ログイン中: {st.session_state['nickname']}")

    # --- サイドバーでカテゴリ選択 ---
    st.sidebar.title("モード選択")
    category = st.sidebar.selectbox(
        "カテゴリを選んでください",
        ["学習系", "ノート系", "シナリオ系", "分析系"]
    )

    # --- 学習系 ---
    if category == "学習系":
        mode = st.sidebar.radio("モード", [
            "デイリー問題",
            "ボス問題アーカイブ",
            "図解問題",
            "光太郎モード",
            "国家試験モード"
        ])
        if mode == "デイリー問題":
            daily.render()
        elif mode == "ボス問題アーカイブ":
            boss.render()
        elif mode == "図解問題":
            diagram.render()
        elif mode == "光太郎モード":
            manual.render()
        elif mode == "国家試験モード":
            company.render()

    # --- ノート系 ---
    elif category == "ノート系":
        mode = st.sidebar.radio("モード", ["実習ノート", "実習モード", "復習リマインダー"])
        if mode == "実習ノート":
            notes.render()
        elif mode == "実習モード":
            practice.render()
        elif mode == "復習リマインダー":
            review.render()

    # --- シナリオ系 ---
    elif category == "シナリオ系":
        mode = st.sidebar.radio("モード", ["多職種共同モード", "シナリオRPG"])
        if mode == "多職種共同モード":
            scenario_auto.render()
        elif mode == "シナリオRPG":
            scenario_rpg.render()

    # --- 分析系 ---
    elif category == "分析系":
        mode = st.sidebar.radio("モード", ["ダッシュボード", "弱点抽出"])
        if mode == "ダッシュボード":
            dashboard.render()
        elif mode == "弱点抽出":
            weakpoints.render()

if __name__ == "__main__":
    main()

    