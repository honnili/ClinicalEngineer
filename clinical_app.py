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
        st.rerun()  # ← 修正ポイント（experimental_rerun → rerun）

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

    # 以下はモード選択処理（省略）

def main():
    st.title("医療学習シミュレーション")  # ログイン前もタイトルを表示
    login_google()

    if "user_id" not in st.session_state:
        st.info("Googleでログインしてください")
        return

    if "profession" not in st.session_state:
        profession_select_page()
    else:
        main_page()

if __name__ == "__main__":
    main()