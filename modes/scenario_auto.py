import streamlit as st
import json, re
from services.gpt_utils import gpt_text

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
# 多職種共同モード用の問題生成（職業対応）
# -------------------------
def generate_multidisciplinary_question(partners, profession: str):
    partners_str = "、".join(partners) if partners else "医師・看護師"
    prompt = f"""
    あなたは{profession}国家試験の出題者です。
    多職種連携（{partners_str}）をテーマにした臨床シナリオ問題を1問作成してください。
    場面は急変対応、手術、在宅医療、ICU、透析室、歯科診療室などからランダムに選んでください。

    出力は必ず JSON のみで返してください。余計な文章は書かないでください。

    {{
      "situation": "患者の状態や場面",
      "roles": {{
        "医師": "診断・治療方針",
        "看護師": "バイタル観察・処置補助",
        "{profession}": "専門的対応・安全管理"
      }},
      "question": "{profession}としての対応を問う問題文",
      "options": ["対応A", "対応B", "対応C", "対応D"],
      "answer": ["対応A","対応C"], 
      "explanation": "解説文",
      "feedback": {{
        "医師": "この対応があると診断がスムーズになる",
        "看護師": "患者安全の観点から重要",
        "薬剤師": "薬物投与のタイミングに影響"
      }}
    }}
    """
    raw = gpt_text(prompt, temperature=0.3)
    return safe_json_loads(raw)

# -------------------------
# 多職種共同モード本体
# -------------------------
def render():
    profession = st.session_state.get("profession", "臨床工学技士")
    st.subheader(f"多職種共同モード（{profession}向け・シナリオ演習・複数回答対応）")

    # 職種選択
    partners = st.multiselect(
        "一緒にシナリオを進める職種を選んでください",
        ["医師", "看護師", "薬剤師", "理学療法士", "臨床検査技師", "歯科衛生士"],
        default=["医師", "看護師"]
    )
    st.info(f"今回のチーム: {', '.join(partners)}")

    num_questions = st.slider("出題数を選んでください", 1, 5, 3)

    if st.button("シナリオ問題を生成する"):
        st.session_state["multi_questions"] = [
            generate_multidisciplinary_question(partners, profession) for _ in range(num_questions)
        ]

    questions = st.session_state.get("multi_questions", [])
    for i, qdata in enumerate(questions):
        if not qdata:
            continue

        st.markdown(f"### 第{i+1}問")
        st.write(f"**状況:** {qdata['situation']}")

        # 役割分担の明示
        st.write("### チーム構成と役割")
        for role, desc in qdata.get("roles", {}).items():
            st.markdown(f"- **{role}**: {desc}")

        st.write(f"**Q: {qdata['question']}**")

        # --- 解答フォーム ---
        with st.form(f"answer_form_{i}"):
            choices = st.multiselect("対応を選んでください", qdata["options"], key=f"multi_choice_{i}")
            submitted = st.form_submit_button("解答する")

            if submitted:
                st.session_state[f"answered_{i}"] = True
                st.session_state[f"selected_{i}"] = choices

        # --- 解答後の表示 ---
        if st.session_state.get(f"answered_{i}", False):
            chosen_set = set(st.session_state[f"selected_{i}"])
            correct_set = set(qdata["answer"])

            if chosen_set == correct_set:
                st.success("正解！ 🎉")
            else:
                st.error(f"不正解… 正しい対応は {', '.join(qdata['answer'])} です")

            st.info(qdata["explanation"])

            # 多層フィードバック
            if "feedback" in qdata:
                st.markdown("### 他職種からのフィードバック")
                for role, fb in qdata["feedback"].items():
                    st.markdown(f"- **{role}**: {fb}")