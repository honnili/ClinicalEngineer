import streamlit as st
import json, re
from services.gpt_utils import gpt_text
from services.diagram_utils import render_mermaid

# -------------------------
# JSON安全パース
# -------------------------
def safe_json_loads(text: str):
    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return None
    except Exception:
        return None

# -------------------------
# マニュアル生成
# -------------------------
def generate_manual(big_field: str, sub_field: str):
    prompt = f"""
    あなたは臨床工学技士国家試験の専門講師です。
    次の分野について、学習者向けに段階的なマニュアルを作成してください。

    大分類: {big_field}
    中分類: {sub_field}

    出力は必ず JSON のみで返してください。
    {{
      "overview": "概要（全体像と学習の優先度）",
      "details": "詳細解説（定義・公式・臨床応用・試験で狙われやすい知識）",
      "pitfalls": "誤答ポイント（混同しやすい用語・計算の落とし穴・試験特有の注意点）"
    }}
    """
    raw = gpt_text(prompt, temperature=0.2)
    return safe_json_loads(raw)

# -------------------------
# 図解問題生成
# -------------------------
def generate_diagram(big_field: str, sub_field: str):
    prompt = f"""
    臨床工学技士向けの{sub_field}に関する図解問題を1問作成してください。
    出力は必ず JSON のみで返してください。
    {{
      "question": "問題文",
      "options": ["選択肢A", "選択肢B", "選択肢C"],
      "answer": "正解の選択肢",
      "explanation": "解説文",
      "mermaid": "graph TD; ..."
    }}
    """
    raw = gpt_text(prompt, temperature=0.1)
    return safe_json_loads(raw)

# -------------------------
# 図解モード本体
# -------------------------
def render_diagram():
    st.subheader("図解問題モード")

    col1, col2 = st.columns(2)
    with col1:
        big_field = st.selectbox("大分類を選んでください", list(field_dict.keys()), key="diagram_big")
        sub_field = st.selectbox("中分類を選んでください", field_dict[big_field], key="diagram_sub")
    with col2:
        mode = st.radio(
            "モードを選んでください",
            ["マニュアル", "閲覧", "解答"],
            horizontal=True,
            key="diagram_mode"
        )

    # --- マニュアルモード ---
    if mode == "マニュアル":
        st.info(f"【{big_field} - {sub_field}】のマニュアル")

        if st.button("マニュアルを生成する", key="manual_generate"):
            data = generate_manual(big_field, sub_field)
            if data:
                st.session_state["manual_data"] = data

        manual_data = st.session_state.get("manual_data")
        if manual_data:
            tab1, tab2, tab3 = st.tabs(["概要", "詳細解説", "誤答ポイント"])
            with tab1:
                st.markdown(f"### 概要\n{manual_data['overview']}")
            with tab2:
                st.markdown(f"### 詳細解説\n{manual_data['details']}")
            with tab3:
                st.markdown(f"### 誤答ポイント\n{manual_data['pitfalls']}")
        return


    # --- 問題生成 ---
    if st.button("問題を生成する", key="diagram_generate"):
        data = generate_diagram(big_field, sub_field)
        if data:
            st.session_state["diagram_data"] = data
            st.session_state["diagram_answered"] = False

    data = st.session_state.get("diagram_data")
    if data:
        st.markdown(f"**Q. {data['question']}**")
        render_mermaid(data["mermaid"])

        if mode == "閲覧":
            st.info(data["explanation"])

        elif mode == "解答":
            with st.form("diagram_answer_form"):
                choice = st.radio("回答を選んでください", data["options"], key="diagram_choice")
                submitted = st.form_submit_button("解答する")
                if submitted:
                    st.session_state["diagram_answered"] = True
                    st.session_state["diagram_choice"] = choice

            if st.session_state.get("diagram_answered", False):
                correct = (st.session_state["diagram_choice"] == data["answer"])
                if correct:
                    st.success("正解！ 🎉")
                else:
                    st.error(f"不正解… 正解は {data['answer']} です")
                st.info(data["explanation"])