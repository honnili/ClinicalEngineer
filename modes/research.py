import streamlit as st
import json
from services.gpt_utils import gpt_text

def render():
    st.subheader("📑 論文参照モード")

    # --- モード切り替え ---
    mode = st.radio("モードを選んでください", ["論文クイズ", "引用解説"], horizontal=True)

    keyword = st.text_input("検索キーワード", "人工呼吸器 PEEP")

    if st.button("検索"):
        if mode == "論文クイズ":
            prompt = f"""
            キーワード「{keyword}」に関連する代表的な医学論文を1本紹介してください。
            さらに、その要約から選択式クイズを1問作成してください。
            出力は必ずJSON形式で返してください。
            {{
              "title": "論文タイトル",
              "authors": "著者名",
              "summary": "要約（3〜5行）",
              "link": "外部リンク",
              "quiz": {{
                "question": "クイズ問題文",
                "options": ["選択肢A","選択肢B","選択肢C"],
                "answer": "正解の選択肢",
                "explanation": "解説文"
              }}
            }}
            """
        else:  # 引用解説モード
            prompt = f"""
            キーワード「{keyword}」に関連する代表的な医学論文を1本紹介してください。
            出力は必ずJSON形式で返してください。
            {{
              "title": "論文タイトル",
              "authors": "著者名",
              "summary": "学習者向けの要約（3〜5行）",
              "quote": "本文から1文だけ短く引用",
              "quote_explained": "その引用文の解説",
              "link": "外部リンク"
            }}
            """
        raw = gpt_text(prompt, temperature=0.2)
        try:
            st.session_state["paper"] = json.loads(raw)
        except Exception:
            st.error("論文情報の取得に失敗しました")

    # --- 表示 ---
    paper = st.session_state.get("paper")
    if paper:
        st.markdown(f"### {paper['title']}")
        st.caption(f"👤 {paper['authors']}")
        st.write(paper["summary"])
        if paper.get("link"):
            st.markdown(f"[🔗 論文リンク]({paper['link']})")

        if mode == "論文クイズ":
            quiz = paper["quiz"]
            st.markdown("### 🎯 クイズで確認")
            choice = st.radio(quiz["question"], quiz["options"], key="quiz_choice")
            if st.button("解答する"):
                if choice == quiz["answer"]:
                    st.success("正解！ 🎉")
                else:
                    st.error(f"不正解… 正解は {quiz['answer']} です")
                st.info(quiz["explanation"])
        else:
            st.markdown(f"> {paper['quote']}")
            st.caption(f"💡 解説: {paper['quote_explained']}")