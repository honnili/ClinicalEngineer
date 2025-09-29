import streamlit as st
from services.ai_utils import call_ai
from services.db_utils import save_boss_problem, save_diagram_with_manual

def run_auto_mode():
    st.subheader("⚡ Autoモード")

    mode = st.radio("生成モードを選択してください", [
        "シナリオ自動生成",
        "国家試験モード",
        "演習モード",
        "光太郎モード"
    ])

    if mode == "シナリオ自動生成":
        run_scenario_mode()
    elif mode == "国家試験モード":
        run_exam_mode()
    elif mode == "演習モード":
        run_practice_mode()
    elif mode == "光太郎モード":
        run_fun_mode()

def run_scenario_mode():
    st.write("ここで症例を入力して問題＋図解を自動生成")
    # さっき作ったシナリオ→問題＋図解生成の処理を呼ぶ

def run_exam_mode():
    st.write("ここで国家試験風の問題を自動生成")
    # 国家試験スタイルのプロンプトを投げる

def run_practice_mode():
    st.write("ここでタグ指定して演習問題を出す")
    # fetch_problems_by_tag を使って出題

def run_fun_mode():
    st.write("ここで古典風やユーモア混じりの問題を生成")
    # 遊び心ある生成プロンプトを投げる