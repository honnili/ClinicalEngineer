# services/gpt_utils.py
import os
import streamlit as st
from openai import OpenAI
import traceback

# 環境変数優先、なければ Streamlit secrets
api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")

if not api_key or not isinstance(api_key, str):
    raise RuntimeError("OPENAI_API_KEY が設定されていません。環境変数か .streamlit/secrets.toml に設定してください。")

# 改行や空白を除去
api_key = api_key.strip()

# プロジェクトキー形式チェック
if not (api_key.startswith("sk-") or api_key.startswith("sk-proj-")):
    raise RuntimeError("OPENAI_API_KEY の形式が正しくありません。最新のキーを確認してください。")

client = OpenAI(api_key=api_key)

def gpt_text(prompt: str, temperature: float = 0.2):
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",  # プロジェクトで有効なモデルか要確認
            messages=[
                {"role": "system", "content": "You are an expert clinical engineering educator. Respond concisely and clearly."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"🔒 OpenAI 認証エラー: {str(e)}")
        traceback.print_exc()
        st.stop()

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