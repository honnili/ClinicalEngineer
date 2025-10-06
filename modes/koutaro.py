import streamlit as st
import re, json, difflib
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
# 記述式採点ロジック
# -------------------------
def extract_keywords(text: str):
    text = re.sub(r"[、。,.]", " ", text)
    return [w for w in text.split() if len(w) > 1]

def grade_free_answer(user_answer: str, correct_answer: str):
    ratio = difflib.SequenceMatcher(None, user_answer, correct_answer).ratio()
    base_score = int(ratio * 100)
    keywords = extract_keywords(correct_answer)
    found = [kw for kw in keywords if kw in user_answer]
    keyword_score = int(len(found) / len(keywords) * 100) if keywords else 100
    final_score = int((base_score * 0.5) + (keyword_score * 0.5))
    feedback = "完璧です！" if final_score == 100 else (
        f"惜しい点: {', '.join([kw for kw in keywords if kw not in user_answer]) or '主要キーワードは含まれています'}\n"
        "改善点: 欠けているキーワードを補うとより正確になります"
    )
    return final_score, feedback

# -------------------------
# 通常問題生成
# -------------------------
def generate_question(big_field: str, sub_field: str):
    prompt = f"""
    臨床工学技士向けの{sub_field}に関する四択問題を1問作成してください。
    出力は必ず JSON のみで返してください。
    {{
      "question": "問題文",
      "options": ["選択肢A", "選択肢B", "選択肢C", "選択肢D"],
      "answer": "正解の選択肢",
      "explanation": "解説文",
      "improvement": "間違えた場合の改善点"
    }}
    """
    raw = gpt_text(prompt, temperature=0.2)
    return safe_json_loads(raw) or {
        "question": f"{sub_field}の基本的な確認問題",
        "options": ["A", "B", "C", "D"],
        "answer": "A",
        "explanation": "ダミー解説",
        "improvement": "参考資料を確認しましょう"
    }

# -------------------------
# 分野辞書
# -------------------------
field_dict = {
    "基礎医学": ["解剖学", "生理学", "病理学", "薬理学"],
        "医用工学概論": ["電気電子工学", "情報工学", "材料工学", "医用計測"],
        "呼吸": ["人工呼吸器", "酸素療法", "血液ガス", "換気モニタリング"],
        "循環": ["ペースメーカ", "補助循環（IABP・ECMO）", "心電図", "血圧モニタ"],
        "血液浄化": ["血液透析", "腹膜透析", "血漿交換", "吸着療法"],
        "代謝・栄養": ["酸塩基平衡", "電解質管理", "栄養管理"],
        "医用機器安全管理": ["電気安全", "機器点検", "感染対策", "リスクマネジメント"],
        "手術室・集中治療": ["麻酔器", "人工心肺", "ICU管理", "モニタリング機器"],
        "ME機器全般": ["基本原理", "保守管理", "トラブルシュート"],
        "臨床応用": ["救急医療", "在宅医療", "チーム医療"],
    }

# -------------------------
# 本体
# -------------------------
def render():
    st.subheader("光太郎モード（連続演習）")

    num_questions = st.slider("出題数を選んでください", 1, 5, 3, key="koutaro_num")
    big_field = st.selectbox("大分類を選んでください", list(field_dict.keys()), key="koutaro_big")
    sub_field = st.selectbox("中分類を選んでください", field_dict[big_field], key="koutaro_sub")
    answer_mode = st.radio("解答形式を選んでください", ["選択式", "記述式"], horizontal=True, key="koutaro_mode")

    if st.button("問題を生成する", key="koutaro_generate"):
        st.session_state["koutaro_questions"] = [generate_question(big_field, sub_field) for _ in range(num_questions)]
        st.session_state["koutaro_answers"] = {}

    questions = st.session_state.get("koutaro_questions", [])
    for i, qdata in enumerate(questions):
        st.markdown(f"### 第{i+1}問")
        st.write(f"**Q: {qdata['question']}**")

        if answer_mode == "選択式":
            with st.form(f"choice_form_{i}"):
                choice = st.radio("選択肢", qdata["options"], key=f"choice_{i}")
                submitted = st.form_submit_button("解答する")
                if submitted:
                    st.session_state["koutaro_answers"][i] = {"mode": "choice", "value": choice}

            ans = st.session_state.get("koutaro_answers", {}).get(i)
            if ans and ans["mode"] == "choice":
                correct = (ans["value"] == qdata["answer"])
                st.success("正解！ 🎉") if correct else st.error(f"不正解… 正解は {qdata['answer']} です")
                st.info(qdata.get("improvement", "ここを復習しましょう"))

        else:
            with st.form(f"text_form_{i}"):
                text = st.text_area("解答を入力してください", key=f"text_{i}")
                submitted = st.form_submit_button("採点する")
                if submitted:
                    st.session_state["koutaro_answers"][i] = {"mode": "text", "value": text}

            ans = st.session_state.get("koutaro_answers", {}).get(i)
            if ans and ans["mode"] == "text":
                score, feedback = grade_free_answer(ans["value"], qdata["answer"])
                st.write(f"採点結果: {score}%")
                st.info(feedback)

        st.text_area("質問・メモ", key=f"memo_{i}")