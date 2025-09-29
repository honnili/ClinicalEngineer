# modes/daily.py
import streamlit as st
from services.db_utils import get_or_create_daily
from services.gpt_utils import gpt_text, gpt_mermaid
from services.diagram_utils import render_mermaid

def _gen_daily_quiz():
    prompt = (
        "Generate one ultra-difficult multiple-choice question for clinical engineering. "
        "Format:\nQ: <question>\nOptions:\nA)\nB)\nC)\nD)\nAnswer:\nExplanation:"
    )
    text = gpt_text(prompt, temperature=0.1)
    return {"text": text}

def _gen_daily_diagram():
    prompt = (
        "Create a very challenging Mermaid flowchart (graph TD) for ventilator alarm response with decisions and actions. "
        "Output only valid Mermaid code."
    )
    code = gpt_mermaid(prompt, temperature=0.1)
    return {"mermaid": code}

def render():
    st.subheader("デイリー問題（1日1回・激むず）")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 今日の一問（激むず）")
        quiz = get_or_create_daily("quiz", _gen_daily_quiz)
        st.code(quiz["text"])
    with col2:
        st.markdown("#### 今日の図解問題（激むず）")
        diagram = get_or_create_daily("diagram", _gen_daily_diagram)
        render_mermaid(diagram["mermaid"])