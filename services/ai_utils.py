from openai import OpenAI
import streamlit as st

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# -------------------------
# クイズ生成
# -------------------------
def generate_quiz(topic: str, num_questions: int = 5):
    """
    指定トピックに基づいてクイズを生成する
    """
    prompt = f"{topic} に関する臨床工学技士向けのクイズを {num_questions} 問作ってください。\n各問題は選択肢付きで、正解を明示してください。"

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert clinical engineering educator."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
    )
    return resp.choices[0].message.content.strip()

# -------------------------
# タグ自動生成（簡易版）
# -------------------------
def generate_tags(text: str):
    """
    ノート本文からタグを自動生成する（簡易版）
    本当はAIでキーワード抽出するが、今はルールベースで仮実装
    """
    tags = []
    if "呼吸" in text:
        tags.append("呼吸器")
    if "心臓" in text or "循環" in text:
        tags.append("循環")
    if "糖" in text or "インスリン" in text:
        tags.append("代謝")
    if "薬" in text:
        tags.append("薬理")
    if not tags:
        tags.append("その他")
    return tags