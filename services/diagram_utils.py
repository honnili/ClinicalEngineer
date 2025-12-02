# services/diagram_utils.py
import streamlit as st
from services.gpt_utils import gpt_mermaid

def render_mermaid(code: str, height: int = 420):
    mermaid_html = f"""
    <div class="mermaid">
    {code}
    </div>
    <script>
    const scriptId = 'mermaid-js';
    if (!document.getElementById(scriptId)) {{
        const s = document.createElement('script');
        s.src = 'https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js';
        s.id = scriptId;
        s.onload = () => {{
            mermaid.initialize({{ startOnLoad: true, securityLevel: 'loose' }});
            mermaid.init();
        }};
        document.head.appendChild(s);
    }} else {{
        mermaid.initialize({{ startOnLoad: true, securityLevel: 'loose' }});
        mermaid.init();
    }}
    </script>
    """
    st.components.v1.html(mermaid_html, height=height, scrolling=True)

def generate_diagram(title: str, question_text: str):
    st.subheader(title)

    # 職業をセッションから取得
    profession = st.session_state.get("profession", "臨床工学技士")

    prompt = (
        f"Create a Mermaid flowchart (graph TD) for a {profession} problem. "
        f"Include key decision points and actions related to: {question_text}. Output only Mermaid."
    )
    code = gpt_mermaid(prompt, temperature=0.1)
    render_mermaid(code)