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

def gpt_mermaid(prompt: str, temperature: float = 0.2):
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Output only Mermaid diagram code without explanations."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
        )
        code = resp.choices[0].message.content.strip()
        if "```mermaid" in code:
            code = code.split("```mermaid")[1].split("```")[0].strip()
        return code
    except Exception:
        st.error("🔒 OpenAI 認証エラーが発生しました。OPENAI_API_KEY を確認してください。")
        st.write("エラー詳細はログを確認してください。")
        traceback.print_exc()
        st.stop()

def summarize_notes(text: str):
    prompt = f"以下の学習メモを200字程度で要約し、重要点を3箇条で箇条書きにしてください。\n\n{text}"
    return gpt_text(prompt, temperature=0.3)

def call_ai(prompt: str, temperature: float = 0.2):
    return gpt_text(prompt, temperature)