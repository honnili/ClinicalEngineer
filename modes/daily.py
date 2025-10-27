import streamlit as st
import json, re
from services.db_utils import get_or_create_daily
from services.gpt_utils import gpt_text
from services.diagram_utils import render_mermaid

# --- JSON安全パース関数 ---
def safe_json_loads(text: str):
    try:
        # JSONっぽい部分だけ抽出
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return None
    except Exception:
        return None

# --- デイリー四択問題 ---
def _gen_daily_quiz():
    prompt = """
    臨床工学技士向けの超難問の四択問題を1問作成してください。
    出力は必ず JSON のみで返してください。余計な文章は一切書かないでください。
    {
      "question": "問題文",
      "options": ["選択肢A", "選択肢B", "選択肢C", "選択肢D"],
      "answer": "正解の選択肢",
      "explanation": "解説文"
    }
    """
    text = gpt_text(prompt, temperature=0.1)
    return {"text": text}

# --- デイリー図解問題 ---
def _gen_daily_diagram():
    prompt = """
    臨床工学技士向けの超難問の図解問題を1問作成してください。
    出力は必ず JSON のみで返してください。余計な文章は一切書かないでください。
    {
      "question": "問題文",
      "options": ["選択肢A", "選択肢B", "選択肢C"],
      "answer": "正解の選択肢",
      "explanation": "解説文",
      "mermaid": "graph TD; ..."
    }
    """
    text = gpt_text(prompt, temperature=0.1)
    return {"text": text}

# --- メイン描画 ---
def render():
    st.subheader("デイリー問題（1日1回・激むず）")

    col1, col2 = st.columns(2)

    # --- 今日の一問 ---
    with col1:
        st.markdown("#### 今日の一問（激むず）")
        quiz = get_or_create_daily("quiz", _gen_daily_quiz)
        data = safe_json_loads(quiz.get("text", ""))

        if not data:
            st.error("デイリー問題のJSONパースに失敗しました。AIの出力を確認してください。")
            st.write(quiz)  # ← KeyError回避のため辞書ごと表示
        else:
            st.markdown(f"**Q. {data['question']}**")
            choice = st.radio("回答を選んでください", data["options"], key="daily_choice")

            if st.button("解答する", key="quiz_answer"):
                correct = (choice == data["answer"])
                if correct:
                    st.success("正解！ 🎉")
                else:
                    st.error(f"不正解… 正解は {data['answer']} です")
                    save_boss_archive(
                        user_id=st.session_state["user_id"],
                        question=data["question"],
                        options=data["options"],
                        answer=data["answer"],
                        explanation=data["explanation"],
                        choice=choice,
                        correct=correct,
                        mode="daily",
                        field="未分類",
                        difficulty="激むず"
                    )
                st.info(data["explanation"])

    # --- 今日の図解問題 ---
    with col2:
        st.markdown("#### 今日の図解問題（激むず）")
        diagram = get_or_create_daily("diagram", _gen_daily_diagram)
        data = safe_json_loads(diagram.get("text", ""))

        if not data:
            st.error("図解問題のJSONパースに失敗しました。AIの出力を確認してください。")
            st.write(diagram)  # ← KeyError回避のため辞書ごと表示
        else:
            st.markdown(f"**Q. {data['question']}**")
            render_mermaid(data["mermaid"])
            choice = st.radio("回答を選んでください", data["options"], key="diagram_choice")

            if st.button("解答する", key="diagram_answer"):
                correct = (choice == data["answer"])
                if correct:
                    st.success("正解！ 🎉")
                else:
                    st.error(f"不正解… 正解は {data['answer']} です")
                    save_boss_archive(
                        user_id=st.session_state["user_id"],
                        question=data["question"],
                        options=data["options"],
                        answer=data["answer"],
                        explanation=data["explanation"],
                        choice=choice,
                        correct=correct,
                        mode="diagram",
                        field="未分類",
                        difficulty="激むず"
                    )
                st.info(data["explanation"])