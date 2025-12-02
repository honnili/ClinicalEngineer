import streamlit as st
import json
from services.gpt_utils import gpt_text

major_options_dict = {
    "臨床工学技士": {
        "基礎医学": ["解剖学", "生理学", "病理学", "薬理学"],
        "臨床応用": ["救急医療", "在宅医療", "チーム医療"],
    },
    "歯科衛生士": {
        "保健指導": ["ブラッシング指導", "食生活指導", "口腔衛生教育", "禁煙支援", "高齢者口腔ケア"],
        "公衆衛生": ["地域歯科保健", "疫学", "感染予防", "学校歯科保健"],
    }
}

def render():
    profession = st.session_state.get("profession", "臨床工学技士")
    st.subheader(f"光太郎モード（{profession}向け）")

    fields = major_options_dict.get(profession, {})
    major = st.selectbox("大分類を選択してください", list(fields.keys()))
    middle = st.selectbox("中分類を選択してください", fields[major])

    if st.button("問題を生成"):
        prompt = f"""
        {profession}向けの{major} - {middle}に関するユニークな問題を1問作成してください。
        出力は必ずJSON形式で返してください。
        {{
          "question": "問題文",
          "options": ["選択肢A","選択肢B","選択肢C","選択肢D"],
          "answer": "正解の選択肢",
          "explanation": "解説文"
        }}
        """
        raw = gpt_text(prompt, temperature=0.3)
        try:
            data = json.loads(raw)
            st.markdown(f"**Q. {data['question']}**")
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