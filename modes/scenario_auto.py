import streamlit as st
from services.ai_utils import generate_scenario
from services.db_utils import save_boss_problem, save_diagram_with_manual

def run_auto_mode():
    st.subheader("⚡ シナリオモード")

    if st.button("問題生成"):
        scenario, problem, diagram, manual = generate_scenario()

        st.write(problem["question"])
        st.write(problem["options"])

        # 保存処理（user_id付き）
        save_boss_problem(
            difficulty="auto",
            field="auto",
            mode="scenario",
            question=problem["question"],
            options=problem["options"],
            answer=problem["answer"],
            explanation=problem["explanation"],
            meta={"tags": problem["tags"]},
            user_id=st.session_state["user_id"]
        )

        save_diagram_with_manual(
            kind="scenario",
            scenario_text=scenario,
            diagram_mermaid=diagram,
            manual_text=manual,
            user_id=st.session_state["user_id"]
        )