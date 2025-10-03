import streamlit as st
import pandas as pd
from services.db_utils import get_tag_statistics

def render():
    st.subheader("📉 弱点抽出モード")

    stats = get_tag_statistics()
    if not stats:
        st.info("まだ解答データがありません。テストやボス問題を解いてから確認してください。")
        return

    df = pd.DataFrame(stats)
    df["正答率(%)"] = round(df["correct"] / (df["correct"] + df["wrong"]) * 100, 1)

    st.dataframe(df, use_container_width=True)

    # 優先復習タグを提示
    weak_tags = df.sort_values("正答率(%)").head(3)
    st.subheader("🔥 優先復習タグ")
    for _, row in weak_tags.iterrows():
        st.markdown(f"- {row['tag']}（正答率 {row['正答率(%)']}%）")