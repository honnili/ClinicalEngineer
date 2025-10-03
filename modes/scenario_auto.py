import streamlit as st
import json, re
from services.gpt_utils import gpt_text

# JSON安全パース
def safe_json_loads(text: str):
    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return None
    except Exception:
        return None

# 多職種共同モード用の問題生成
def generate_multidisciplinary_question():
    prompt = """
    あなたは臨床工学技士国家試験の出題者です。
    多職種連携（医師・看護師・薬剤師・理学療法士・臨床検査技師など）をテーマにした臨床シナリオ問題を1問作成してください。
    場面は急変対応、手術、在宅医療、ICU、透析室などからランダムに選んでください。
    出力は必ず JSON のみで返してください。余計な文章は書かないでください。

    {
      "situation": "患者の状態や場面",
      "question": "臨床工学技士としての対応を問う問題文",
      "options": ["選択肢A", "選択肢B", "選択肢C", "選択肢D"],
      "answer": "正解の選択肢",
      "explanation": "解説文"
    }
    """
    raw = gpt_text(prompt, temperature=0.3)
    return safe_json_loads(raw)

# -------------------------
# 多職種共同モード本体
# -------------------------
def render():
    st.subheader("多職種共同モード（シナリオ演習・選択式）")

    num_questions = st.slider("出題数を選んでください", 1, 5, 3)

    if st.button("シナリオ問題を生成する"):
        for i in range(num_questions):
            qdata = generate_multidisciplinary_question()
            if not qdata:
                st.error("問題生成に失敗しました")
                continue

            st.markdown(f"### 第{i+1}問")
            st.write(f"**状況:** {qdata['situation']}")
            st.write(f"**Q: {qdata['question']}**")

            choice = st.radio("対応を選んでください", qdata["options"], key=f"choice_{i}")
            if st.button(f"解答する_{i}"):
                if choice == qdata["answer"]:
                    st.success("正解！ 🎉")
                else:
                    st.error(f"不正解… 正しい対応は {qdata['answer']} です")
                st.info(qdata["explanation"])