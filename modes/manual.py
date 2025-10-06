import streamlit as st
import json, re, difflib
from services.gpt_utils import gpt_text
from services.diagram_utils import render_mermaid

# -------------------------
# 採点ロジック（光太郎モード用）
# -------------------------
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

    if final_score == 100:
        feedback = "完璧です！"
    else:
        feedback = f"惜しい点: {', '.join(missing) if missing else '主要キーワードは含まれています'}\n"
        feedback += "改善点: 欠けているキーワードを補うとより正確になります"

    return final_score, feedback

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
# 問題生成
# -------------------------
def generate_question(big_field: str, sub_field: str):
    prompt = f"""
    臨床工学技士向けの{sub_field}に関する演習問題を1問作成してください。
    出力は必ず JSON のみで返してください。余計な文章は一切書かないでください。
    {{
      "question": "問題文",
      "options": ["選択肢A", "選択肢B", "選択肢C"],
      "answer": "正解の選択肢",
      "explanation": "解説文",
      "improvement": "間違えた場合の改善点"
    }}
    """
    raw = gpt_text(prompt, temperature=0.2)
    return safe_json_loads(raw)

def generate_diagram(big_field: str, sub_field: str):
    prompt = f"""
    臨床工学技士向けの{sub_field}に関する図解問題を1問作成してください。
    出力は必ず JSON のみで返してください。余計な文章は一切書かないでください。
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
# 大分類と中分類の辞書
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
    "臨床応用": ["救急医療", "在宅医療", "チーム医療"]
}

# -------------------------
# 図解モード
# -------------------------
def render_diagram():
    st.subheader("図解問題モード")

    col1, col2 = st.columns(2)
    with col1:
        big_field = st.selectbox("大分類を選んでください", list(field_dict.keys()), key="diagram_big")
        sub_field = st.selectbox("中分類を選んでください", field_dict[big_field], key="diagram_sub")
    with col2:
        mode = st.radio("モードを選んでください", ["閲覧", "解答"], horizontal=True, key="diagram_mode")

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


# -------------------------
# 光太郎モード
# -------------------------
def render_koutaro():
    st.subheader("光太郎モード（連続演習）")

    num_questions = st.slider("出題数を選んでください", 1, 5, 3, key="koutaro_num")
    big_field = st.selectbox("大分類を選んでください", list(field_dict.keys()), key="koutaro_big")
    sub_field = st.selectbox("中分類を選んでください", field_dict[big_field], key="koutaro_sub")
    answer_mode = st.radio("解答形式を選んでください", ["選択式", "記述式"], horizontal=True, key="koutaro_mode")

    # 問題生成ボタン
    if st.button("問題を生成する", key="koutaro_generate"):
        st.session_state["koutaro_questions"] = []
        for i in range(num_questions):
            qdata = generate_question(big_field, sub_field)
            if qdata:
                st.session_state["koutaro_questions"].append(qdata)

    # --- 問題表示 ---
    questions = st.session_state.get("koutaro_questions", [])
    for i, qdata in enumerate(questions):
        st.markdown(f"### 第{i+1}問")
        st.write(f"**Q: {qdata['question']}**")

        if answer_mode == "選択式":
            with st.form(f"choice_form_{i}"):
                choice = st.radio("選択肢", qdata["options"], key=f"choice_{i}")
                submitted = st.form_submit_button("解答する")
                if submitted:
                    correct = (choice == qdata["answer"])
                    if correct:
                        st.success("正解！ 🎉")
                    else:
                        st.error(f"不正解… 正解は {qdata['answer']} です")
                    st.info(qdata.get("improvement", "ここを復習しましょう"))

        else:  # 記述式
            with st.form(f"text_form_{i}"):
                text = st.text_area("解答を入力してください", key=f"text_{i}")
                submitted = st.form_submit_button("採点する")
                if submitted:
                    score, feedback = grade_free_answer(text, qdata["answer"])
                    st.write(f"採点結果: {score}%")
                    st.info(feedback)

        # 質問・メモ欄
        st.text_area("質問・メモ", key=f"memo_{i}")