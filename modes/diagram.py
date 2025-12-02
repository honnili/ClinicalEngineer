import streamlit as st
import json
from services.gpt_utils import gpt_text
from services.diagram_utils import render_mermaid

# 職業ごとのフィルター
major_options_dict = {
    "臨床工学技士": {
        "呼吸": ["人工呼吸器", "酸素療法", "血液ガス", "換気モニタリング"],
        "循環": ["ペースメーカ", "補助循環（IABP・ECMO）", "心電図", "血圧モニタ"],
        "血液浄化": ["血液透析", "腹膜透析", "血漿交換", "吸着療法"],
    },
    "歯科衛生士": {
        "予防処置": ["歯石除去", "プラークコントロール", "フッ化物応用", "シーラント", "PMTC"],
        "臨床歯科": ["歯周病学", "小児歯科学", "高齢者歯科", "口腔外科補助", "矯正歯科補助"],
    }
}

def render():
    profession = st.session_state.get("profession", "臨床工学技士")
    st.subheader(f"図解モード（{profession}向け）")

    fields = major_options_dict.get(profession, {})
    major = st.selectbox("大分類を選択してください", list(fields.keys()))
    middle = st.selectbox("中分類を選択してください", fields[major])

    if st.button("図解問題を生成"):
        prompt = f"""
        {profession}向けの{major} - {middle}に関する図解問題を1問作成してください。
        出力は必ずJSON形式で返してください。
        {{
          "question": "問題文",
          "options": ["選択肢A","選択肢B","選択肢C"],
          "answer": "正解の選択肢",
          "explanation": "解説文",
          "mermaid": "graph TD; ..."
        }}
        """
        raw = gpt_text(prompt, temperature=0.2)
        try:
            data = json.loads(raw)
            st.markdown(f"**Q. {data['question']}**")
            render_mermaid(data["mermaid"])
            choice = st.radio("回答を選んでください", data["options"])
            if st.button("解答する"):
                if choice == data["answer"]:
                    st.success("正解！ 🎉")
                else:
                    st.error(f"不正解… 正解は {data['answer']} です")
                st.info(data["explanation"])
        except Exception:
            st.error("JSONパースに失敗しました")
            st.write(raw)