import streamlit as st
import json
from services.db_utils import save_boss_problem
from services.gpt_utils import gpt_text
from services.gpt_utils import gpt_text

def _build_prompt(source: str, mode: str, difficulty: str, answer_style: str,
                  major_section: str, middle_section: str, field: str) -> str:
    """
    シナリオRPGや自動生成モードで使うプロンプトを構築する
    """
    prompt = f"""
    You are generating a clinical engineering training scenario.
    Source: {source}
    Mode: {mode}
    Difficulty: {difficulty}
    Answer style: {answer_style}
    Major section: {major_section}
    Middle section: {middle_section}
    Field: {field}

    Please output a JSON with keys:
    - question
    - options
    - answer
    - explanation
    - meta
    """
    return prompt


def _ai_complete_json(prompt: str, temperature: float = 0.3):
    """
    GPTにJSON形式で回答させるための共通関数
    """
    text = gpt_text(prompt, temperature=temperature)
    return text

def _ai_complete_json(prompt: str, temperature: float = 0.3):
    text = gpt_text(prompt, temperature=temperature)
    return text

# --- 回答形式ラベルを内部キーに変換する関数 ---
def map_answer_style(label: str) -> str:
    if label == "選択式":
        return "multiple_choice"
    elif label == "記述式":
        return "free_text"
    elif label in ["手書き式", "ハイブリッド"]:
        return "other"
    return "unknown"

def render(
    learning_mode,
    source,
    mode,
    difficulty,
    answer_style,
    major_section,
    middle_section,
    field,
    max_questions,
    target_accuracy
):
    # --- UIラベルを内部キーに変換 ---
    answer_style_key = map_answer_style(answer_style)

    st.subheader(f"📘 {learning_mode}")
    st.caption(f"出題ソース: {source}, モード: {mode}, 難易度: {difficulty}, 回答形式: {answer_style}")
        # --- 出題処理（例: 単発モード） ---
    if learning_mode == "単発モード":
        prompt = f"""
あなたは臨床工学シミュレーター用の教材作成AIです。
以下の条件に基づいて問題を1問生成してください。

【条件】
- 難易度: {difficulty}
- 回答形式: {answer_style}
- 大分類: {major_section}
- 中分類: {middle_section}
- フィールド: {field}

【出力形式】
{{
  "question": "...",
  "options": [...],
  "answer": "...",
  "explanation": "...",
  "tags": ["...", "..."],
  "difficulty": "{difficulty}",
  "mode": "{mode}",
  "answer_style": "{answer_style_key}"
}}
"""
        case = _ai_complete_json(prompt)

        if case:
            save_boss_problem(
                difficulty=difficulty,
                field=field,
                mode=mode,
                question=case.get("question", ""),
                options=case.get("options", []),
                answer=case.get("answer", ""),
                explanation=case.get("explanation", ""),
                meta={
                    "tags": case.get("tags", []),
                    "source": source,
                    "answer_style": answer_style_key
                }
            )
            st.success("✅ 問題を生成・保存しました！")
            st.write("**Q:**", case.get("question"))
            if case.get("options"):
                st.write("**選択肢:**", case.get("options"))
            st.write("**正答:**", case.get("answer"))
            st.write("**解説:**", case.get("explanation"))
        else:
            st.error("AIによる問題生成に失敗しました。")