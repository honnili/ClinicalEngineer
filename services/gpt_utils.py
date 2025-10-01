# services/gpt_utils.py
import streamlit as st
from OpenAI import OpenAI

# secrets.toml からキーを読み込む
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def gpt_text(prompt: str, temperature: float = 0.2):
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert clinical engineering educator. Respond concisely and clearly."},
            {"role": "user", "content": prompt}
        ],
        temperature=temperature,
    )
    return resp.choices[0].message.content.strip()

def gpt_mermaid(prompt: str, temperature: float = 0.2):
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

def summarize_notes(text: str):
    prompt = f"以下の学習メモを200字程度で要約し、重要点を3箇条で箇条書きにしてください。\n\n{text}"
    return gpt_text(prompt, temperature=0.3)