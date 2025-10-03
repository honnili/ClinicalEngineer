import streamlit as st
import json, re, difflib
from services.gpt_utils import gpt_text

# 採点ロジック（記述式用）
def extract_keywords(text: str):
    text = re.sub(r"[、。,.]", " ", text)
    return [w for w in text.split() if len(w) > 1]

def grade_free_answer(user_answer: str, correct_answer: str):
    ratio = difflib.SequenceMatcher(None, user_answer, correct_answer).ratio()
    base_score = int(ratio * 100)

    keywords = extract_keywords(correct_answer)
    found = [kw for kw in keywords if kw in user_answer]
    missing = [kw for kw in keywords if kw not in user_answer]

    keyword_score = int(len(found) / len(keywords) * 100) if keywords else 100
    final_score = int((base_score * 0.5) + (keyword_score * 0.5))

    return final_score

# JSON安全パース
def safe_json_loads(text: str):
    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return None
    except Exception:
        return None

# 問題生成
def generate_question(big_field: str, sub_field: str):
    prompt = f"""
    臨床工学技士国家試験風の{sub_field}に関する問題を1問作成してください。
    出力は必ず JSON のみで返してください。
    {{
      "question": "問題文",
      "options": ["選択肢A", "選択肢B", "選択肢C"],
      "answer": "正解の選択肢",
      "explanation": "解説文"
    }}
    """
    raw = gpt_text(prompt, temperature=0.2)
    return safe_json_loads(raw)

# 大分類と中分類
field_dict = {
    "基礎医学": ["解剖学", "生理学", "病理学", "薬理学"],
    "呼吸": ["人工呼吸器", "酸素療法", "血液ガス", "換気モニタリング"],
    "循環": ["ペースメーカ", "補助循環（IABP・ECMO）", "心電図", "血圧モニタ"],
    "血液浄化": ["血液透析", "腹膜透析", "血漿交換", "吸着療法"],
    "代謝・栄養": ["酸塩基平衡", "電解質管理", "栄養管理"],
    "手術室・集中治療": ["麻酔器", "人工心肺", "ICU管理", "モニタリング機器"],
}

# -------------------------
# 国家試験モード本体
# -------------------------
def render():
    st.subheader("国家試験モード")

    num_questions = st.slider("出題数を選んでください", 10, 50, 20)
    big_field = st.selectbox("大分類を選んでください", list(field_dict.keys()))
    sub_field = st.selectbox("中分類を選んでください", field_dict[big_field])
    answer_mode = st.radio("解答形式を選んでください", ["選択式", "記述式"], horizontal=True)

    if st.button("試験開始"):
        questions = [generate_question(big_field, sub_field) for _ in range(num_questions)]

        # 問題をまとめて表示（途中採点なし）
        for i, qdata in enumerate(questions):
            st.markdown(f"### 第{i+1}問")
            st.write(f"**Q: {qdata['question']}**")
            if answer_mode == "選択式":
                st.radio("選択肢", qdata["options"], key=f"choice_{i}")
            else:
                st.text_area("解答を入力してください", key=f"text_{i}")

        # 採点ボタン
        if st.button("採点する"):
            score = 0
            for i, qdata in enumerate(questions):
                if answer_mode == "選択式":
                    choice = st.session_state.get(f"choice_{i}")
                    if choice == qdata["answer"]:
                        score += 1
                else:
                    text = st.session_state.get(f"text_{i}", "")
                    s = grade_free_answer(text, qdata["answer"])
                    if s > 70:  # 70%以上なら正解扱い
                        score += 1

            st.success(f"あなたの得点: {score}/{len(questions)}")
            if score >= int(len(questions) * 0.6):
                st.balloons()
                st.write("🎉 合格ライン突破！")
            else:
                st.write("💡 もう少し復習しましょう")