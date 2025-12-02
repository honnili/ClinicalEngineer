import streamlit as st
import random

def select_common_filters():
    # 職業ごとの大分類・中分類
    major_options_dict = {
        "臨床工学技士": {
            "基礎医学": ["解剖学", "生理学", "病理学", "薬理学"],
            "医用工学概論": ["電気電子工学", "情報工学", "材料工学", "医用計測"],
            "呼吸": ["人工呼吸器", "酸素療法", "血液ガス", "換気モニタリング"],
            "循環": ["ペースメーカ", "補助循環（IABP・ECMO）", "心電図", "血圧モニタ"],
            "血液浄化": ["血液透析", "腹膜透析", "血漿交換", "吸着療法"],
            "代謝・栄養": ["酸塩基平衡", "電解質管理", "栄養管理"],
            "医用機器安全管理": ["電気安全", "機器点検", "感染対策", "リスクマネジメント"],
            "手術室・集中治療": ["麻酔器", "人工心肺", "ICU管理", "モニタリング機器"],
            "ME機器全般": ["基本原理", "保守管理", "トラブルシュート"],
            "臨床応用": ["救急医療", "在宅医療", "チーム医療"],
        },
        "歯科衛生士": {
            "基礎歯科医学": ["口腔解剖学", "口腔生理学", "歯牙解剖学", "歯科材料学", "歯科放射線学"],
            "予防処置": ["歯石除去", "プラークコントロール", "フッ化物応用", "シーラント", "PMTC"],
            "保健指導": ["ブラッシング指導", "食生活指導", "口腔衛生教育", "禁煙支援", "高齢者口腔ケア"],
            "臨床歯科": ["歯周病学", "小児歯科学", "高齢者歯科", "口腔外科補助", "矯正歯科補助"],
            "公衆衛生": ["地域歯科保健", "疫学", "感染予防", "学校歯科保健"],
        }
    }

    # 現在の職業をセッションから取得
    profession = st.session_state.get("profession", "臨床工学技士")
    major_options = major_options_dict.get(profession, {})

    major = st.selectbox("大分類を選択してください", ["なし"] + list(major_options.keys()))
    if major == "なし":
        middle = "なし"
    else:
        middle = st.selectbox("中分類を選択してください", ["なし"] + major_options[major])

    difficulty = st.radio("難易度を選択してください", ["なし", "初級", "中級", "上級"])

    # 全部「なし」の場合はランダム選択
    if major == "なし" and middle == "なし" and difficulty == "なし":
        major = random.choice(list(major_options.keys()))
        middle = random.choice(major_options[major])
        difficulty = random.choice(["初級", "中級", "上級"])
        st.info(f"完全ランダム選択: {major} / {middle} / {difficulty}")

    return major, middle, difficulty