import streamlit as st
from services.db_utils import (
    get_tag_statistics,
    fetch_problems_by_tag,
    fetch_diagrams_by_tag
)

def render_dashboard():
    st.subheader("📊 ダッシュボード & ノート")

    # --- タグ別統計 ---
    stats = get_tag_statistics(user_id=st.session_state["user_id"])
    if not stats:
        st.info("まだ学習データがありません")
        return

    st.write("### タグ別正答率")
    for tag, data in stats.items():
        st.write(f"- {tag}: {data['correct']}/{data['total']} 正答率 {data['accuracy']:.1f}%")

    # --- 復習用問題 ---
    st.write("### 復習問題")
    tag = st.selectbox("復習するタグを選んでください", list(stats.keys()))
    problems = fetch_problems_by_tag(tag, user_id=st.session_state["user_id"])
    if problems:
        for p in problems:
            st.markdown(f"**Q: {p['question']}**")
            st.write(p["options"])
            st.write(f"解答: {p['answer']}")
            st.write(f"解説: {p['explanation']}")
            st.divider()
    else:
        st.info("このタグの問題はまだありません")

    # --- 関連図解（ノート一覧） ---
    st.write("### 関連図解・ノート")
    diagrams = fetch_diagrams_by_tag(tag, user_id=st.session_state["user_id"])
    if diagrams:
        for d in diagrams:
            st.markdown(f"#### {d['scenario_text']}")
            st.code(d["diagram_mermaid"], language="mermaid")
            st.write(d["manual_text"])
            st.divider()
    else:
        st.info("このタグの図解はまだありません")