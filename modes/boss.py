import streamlit as st
from services.db_utils import list_boss_problems
import json

def render():
    st.subheader("👹 ボス問題アーカイブ（解けなかった問題）")

    items = list_boss_problems()
    if not items:
        st.info("まだボス問題はありません。間違えた問題がここに自動保存されます。")
        return

    for it in items:
        with st.container():
            # メタ情報
            st.markdown(
                f"**日時:** {it['timestamp']} | **難易度:** {it['difficulty']} | **分野:** {it['field']} | **モード:** {it['mode']}"
            )
            st.markdown(f"### ❗ 難問: {it['question']}")

            # 選択肢を番号付きで表示
            st.subheader("選択肢")
            for i, opt in enumerate(it["options"], start=1):
                st.markdown(f"{i}. {opt}")

            cols = st.columns(3)
            with cols[0]:
                with st.expander(f"解説を見る #{it['id']}"):
                    st.write(it["explanation"])

            with cols[1]:
                if st.button(f"再挑戦 #{it['id']}", key=f"retry_{it['id']}"):
                    # 再挑戦用にセッションに格納
                    st.session_state.current_boss = it
                    st.session_state.mode = "boss_retry"
                    st.success("この問題を再挑戦モードに読み込みました！")

            with cols[2]:
                st.caption(
                    f"状態: {it['meta'].get('tier','-')} / "
                    f"経過秒: {it['meta'].get('elapsed','-')} / "
                    f"合併症: {it['meta'].get('complication','-')}"
                )

            st.markdown("---")

    # 再挑戦モードが有効なら出題
    if st.session_state.get("mode") == "boss_retry" and "current_boss" in st.session_state:
        boss = st.session_state.current_boss
        st.markdown("## 🔥 再挑戦モード")
        st.write("Q:", boss["question"])
        for i, opt in enumerate(boss["options"], start=1):
            st.markdown(f"{i}. {opt}")

        # 回答選択
        choice = st.radio("選択肢を選んでください", boss["options"], key="boss_answer")
        if st.button("解答する", key="boss_submit"):
            if choice == boss["answer"]:
                st.success("正解！克服しました 💪")
            else:
                st.error(f"不正解… 正解は {boss['answer']} でした")
            st.info(boss["explanation"])
            # 再挑戦終了
            st.session_state.mode = None