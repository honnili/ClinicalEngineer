import streamlit as st
import json
from services.gpt_utils import call_ai

def render(source=None, mode=None, difficulty="中級", answer_style="choice",
           major_section=None, middle_section=None, field=None):
    st.subheader("🎮 シナリオRPG")
    # 引数を使うならここで利用

    # 初期化
    if "rpg_history" not in st.session_state:
        st.session_state["rpg_history"] = []

    case = st.text_area("シナリオの舞台や患者情報を入力してください（任意）")

    # --- シナリオ開始 ---
    if st.button("シナリオ開始"):
        prompt = f"""
        あなたは臨床工学技士です。
        舞台: {case or "自由に舞台を設定してください"}

        RPG風に、状況説明と3つの選択肢を必ずJSON形式で返してください。
        {{
          "scenario": "状況説明文",
          "options": ["選択肢A", "選択肢B", "選択肢C"]
        }}
        """
        result = call_ai(prompt)
        try:
            data = json.loads(result)
            st.session_state["rpg_history"] = [data]  # 最初のターンを保存
        except:
            st.error("JSON形式で返ってきませんでした")
            st.write(result)

    # --- 現在のターンを表示 ---
    if st.session_state["rpg_history"]:
        current = st.session_state["rpg_history"][-1]
        st.markdown(f"### シナリオ\n{current['scenario']}")

        choice = st.radio("行動を選んでください", current["options"], key=f"choice_{len(st.session_state['rpg_history'])}")

        # --- 次のターンへ ---
        if st.button("次へ"):
            prompt = f"""
            これまでのシナリオ:
            {st.session_state['rpg_history']}

            プレイヤーの選択: {choice}

            この続きのシナリオをRPG風に生成してください。
            必ずJSON形式で返してください:
            {{
              "scenario": "状況説明文",
              "options": ["選択肢A", "選択肢B", "選択肢C"]
            }}
            """
            result = call_ai(prompt)
            try:
                data = json.loads(result)
                st.session_state["rpg_history"].append(data)
            except:
                st.error("JSON形式で返ってきませんでした")
                st.write(result)