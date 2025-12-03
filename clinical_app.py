import streamlit as st
from services.db_utils import init_db
from services.auth_utils import login_google
from modes import daily, boss, diagram, koutaro, research, company
from modes import scenario_auto, scenario_rpg
from modes import dashboard, weakpoints

st.set_page_config(
    page_title="医療学習シミュレーション",
    page_icon="🩺",
    layout="wide"
)

init_db()

def profession_select_page():
    st.title("医療学習シミュレーション")
    st.subheader("職業選択ページ")
    st.write("まずはあなたの職業を選んでください")

    profession = st.radio(
        "職業を選択してください",
        ["臨床工学技士", "歯科衛生士"]
    )

    if st.button("決定"):
        st.session_state["profession"] = profession
        st.session_state["profession_selected"] = True
        st.rerun()

def main_page():
    st.title("医療学習シミュレーション")
    st.write("国家試験対策や臨床現場の理解をサポートを目的とした学習アプリです。AIによる解答、解説なので100%という保証はありません。")

    st.success(f"ログイン中: {st.session_state['nickname']}")
    st.success(f"選択された職業: {st.session_state['profession']}")

    # サイドバーで職業変更可能
    with st.sidebar:
        st.session_state["profession"] = st.selectbox(
            "職業を変更する",
            ["臨床工学技士", "歯科衛生士"],
            index=["臨床工学技士", "歯科衛生士"].index(st.session_state["profession"])
        )

    # --- サイドバーでカテゴリ選択 ---
    st.sidebar.title("モード選択")
    category = st.sidebar.selectbox(
        "カテゴリを選んでください",
        ["学習系", "論文系", "シナリオ系", "分析系"]
    )

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
            koutaro.render()
        elif mode == "国家試験モード":
            company.render()

    elif category == "論文系":
        if st.sidebar.radio("モード", ["論文参照モード"]) == "論文参照モード":
            research.render()

    elif category == "シナリオ系":
        mode = st.sidebar.radio("モード", ["多職種共同モード", "シナリオRPG"])
        if mode == "多職種共同モード":
            scenario_auto.render()
        elif mode == "シナリオRPG":
            scenario_rpg.render()

    elif category == "分析系":
        mode = st.sidebar.radio("モード", ["ダッシュボード", "弱点抽出"])
        if mode == "ダッシュボード":
            dashboard.render()
        elif mode == "弱点抽出":
            weakpoints.render()

def main():
    st.title("医療学習シミュレーション")

    # --- Googleログインを最初に必ず実行 ---
    login_google()

    if "user_id" not in st.session_state:
        st.info("Googleでログインしてください")
        return

    # --- 職業選択ページへ ---
    if "profession" not in st.session_state or not st.session_state.get("profession_selected", False):
        profession_select_page()
    else:
        main_page()

if __name__ == "__main__":
    main()