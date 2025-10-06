import streamlit as st
import json, re
from services.db_utils import save_boss_archive
from services.gpt_utils import gpt_text
from services.diagram_utils import render_mermaid
from datetime import datetime

# --- JSON安全パース ---
def safe_json_loads(text: str):
    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return None
    except Exception:
        return None

# --- 図解問題生成 ---
def _gen_diagram(big_field: str, sub_field: str):
    prompt = f"""
    臨床工学技士向けの{sub_field}に関する図解問題を1問作成してください。
    出力は必ず JSON のみで返してください。余計な文章は一切書かないでください。
    {{
      "question": "問題文",
      "options": ["選択肢A", "選択肢B", "選択肢C"],
      "answer": "正解の選択肢",
      "explanation": "解説文",
      "mermaid": "graph TD; ..."
    }}
    """
    return gpt_text(prompt, temperature=0.1)

# --- メイン描画 ---
def render():
    st.subheader("図解問題モード")

    # 大分類と中分類の辞書
    field_dict = {
        "基礎医学": ["解剖学", "生理学", "病理学", "薬理学"],
        "医用工学概論": ["電気電子工学", "情報工学", "材料工学", "医用計測"],
        "呼吸": ["人工呼吸器", "酸素療法", "血液ガス", "換気モニタリング"],
        "循環": ["ペースメーカ", "補助循環（IABP・ECMO）", "心電図", "血圧モニタ"],
        "血液浄化": ["血液透析", "腹膜透析", "血漿交換", "吸着療法"],
        "代謝・栄養": ["酸塩基平衡", "電解質管理", "栄養管理"],
        "医用機器安全管理": ["電気安全", "機器点検", "感染対策", "リスクマネジメント"],
        "手術室・集中治療": ["麻酔器", "人工心肺", "ICU管理", "モニタリング機器"],
        "ME機器全般": ["基本原理", "保守管理", "トラブルシュート"],
        "臨床応用": ["救急医療", "在宅医療", "チーム医療"]
    }

    # --- 最初に全部選ばせる ---
    col1, col2 = st.columns(2)
    with col1:
        big_field = st.selectbox("大分類を選んでください", list(field_dict.keys()))
        sub_field = st.selectbox("中分類を選んでください", field_dict[big_field])
    with col2:
        mode = st.radio("モードを選んでください", ["閲覧", "解答"], horizontal=True)

    # 問題生成ボタン
    if st.button("問題を生成する"):
        raw = _gen_diagram(big_field, sub_field)
        data = safe_json_loads(raw)
        if not data:
            st.error("図解問題の生成に失敗しました")
            st.write(raw)
            return
        # ← session_state に保存
        st.session_state["diagram_data"] = data
        st.session_state["answered"] = False

    # --- 問題表示 ---
    data = st.session_state.get("diagram_data")
    if data:
        st.markdown(f"**Q. {data['question']}**")
        render_mermaid(data["mermaid"])

        if mode == "閲覧":
            # 生成直後から解説を表示
            st.info(data["explanation"])

        elif mode == "解答":
            # フォームで回答と送信を一括処理
            with st.form("answer_form"):
                choice = st.radio("回答を選んでください", data["options"])
                submitted = st.form_submit_button("解答する")

                if submitted:
                    st.session_state["answered"] = True
                    st.session_state["choice"] = choice

            # 回答後にだけ解説を表示
            if st.session_state.get("answered", False):
                correct = (st.session_state["choice"] == data["answer"])
                if correct:
                    st.success("正解！ 🎉")
                else:
                    st.error(f"不正解… 正解は {data['answer']} です")
                st.info(data["explanation"])