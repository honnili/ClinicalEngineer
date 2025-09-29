import time
import streamlit as st
import random
from services.diagram_utils import generate_diagram
from modes.learning import _build_prompt, _ai_complete_json

def render(source, mode, difficulty, answer_style, major_section, middle_section, field):
    st.subheader("シナリオ進行モード（RPG風）")

    # HP初期化
    if "hp" not in st.session_state:
        st.session_state.hp = 100

    # 制限時間設定
    time_limit = {"初級": 60, "中級": 30, "上級": 15}.get(difficulty, 30)

    # シナリオ開始
    if st.button("シナリオ開始"):
        prompt = _build_prompt(mode, difficulty, major_section, middle_section, field)
        case = _ai_complete_json(prompt)
        if not case:
            st.error("シナリオ生成に失敗しました。")
            return
        st.session_state.current_case = case
        st.session_state.case_start_time = time.time()
        st.session_state.phase = 1

    case = st.session_state.get("current_case")
    if not case:
        st.info("シナリオを開始してください。")
        return

    # HPバー表示
    hp = st.session_state.hp
    color = "green" if hp > 60 else ("orange" if hp > 30 else "red")
    st.markdown(f"""
    <div style="width:100%;background:#ddd;border-radius:5px;">
      <div style="width:{hp}%;background:{color};padding:5px;color:white;text-align:center;">
        HP: {hp}%
      </div>
    </div>
    """, unsafe_allow_html=True)

    # タイマー表示
    elapsed = int(time.time() - st.session_state.case_start_time)
    remaining = max(0, time_limit - elapsed)
    timer_color = "#2ecc71" if remaining > 10 else "#e74c3c"
    st.markdown(f"<h4 style='color:{timer_color}'>残り時間: {remaining} 秒</h4>", unsafe_allow_html=True)

    # 問題文と選択肢
    st.write("Q:", case["question"])

    st.subheader("選択肢")
    for i, opt in enumerate(case["options"], start=1):
        st.markdown(f"{i}. {opt}")
            # 回答ボタン
    if st.button("解答する"):
        if elapsed <= 10:
            st.success("迅速対応 → 改善！")
            st.session_state.hp = min(100, st.session_state.hp + 20)
        elif elapsed <= time_limit:
            st.info("ギリギリ対応 → 現状維持")
            st.session_state.hp = max(0, st.session_state.hp - 10)
        else:
            st.error("遅延対応 → 悪化！")
            st.session_state.hp = max(0, st.session_state.hp - 30)

        # 次の問題に進む準備
        st.session_state.phase = 2

    # フェーズ2：解説や図解を表示（ダミー処理）
    if st.session_state.get("phase") == 2:
        st.subheader("解説")
        st.write(case.get("explanation", "解説はまだありません。"))

        # 図解生成（ダミー）
        if st.button("図解を生成する"):
            diagram = generate_diagram(case["question"], case.get("answer", ""))
            if diagram:
                st.image(diagram, caption="生成された図解", use_column_width=True)
            else:
                st.warning("図解生成に失敗しました。")

        # 次の問題へ進む
        if st.button("次の問題へ"):
            st.session_state.phase = 1
            st.session_state.current_case = None
