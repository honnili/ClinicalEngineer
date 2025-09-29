import streamlit as st
import json
from services.db_utils import list_notes, mark_review_done, get_review_status, get_tag_stats
from utils.review import get_review_targets

def render():
    st.subheader("⏰ 復習リマインダー")

    notes = list_notes(limit=500)
    targets = get_review_targets(notes)

    if not targets:
        st.info("今日は復習対象のノートはありません。")
        return

    # --- 弱点タグを抽出 ---
    stats = get_tag_stats()
    weak_tags = []
    if stats:
        df = pd.DataFrame(stats)
        df["正答率"] = df["correct"] / (df["correct"] + df["wrong"])
        weak_tags = df.sort_values("正答率").head(3)["tag"].tolist()

    # --- 復習対象を弱点優先で並べ替え ---
    def priority(note):
        try:
            parsed = json.loads(note["text"])
            tags = parsed.get("meta", {}).get("tags", [])
        except Exception:
            tags = []
        return 0 if any(t in weak_tags for t in tags) else 1

    targets_sorted = sorted(targets, key=lambda x: priority(x[0]))

    # --- 表示 ---
    for n, days in targets_sorted:
        try:
            parsed = json.loads(n["text"])
            manual_text = parsed.get("manual", "")
            meta = parsed.get("meta", {})
        except Exception:
            manual_text, meta = n["text"], {}

        status = get_review_status(n["id"])

        # タイトルに弱点タグが含まれていれば🔥マーク
        is_weak = any(t in weak_tags for t in meta.get("tags", []))
        title = f"### {'🔥 ' if is_weak else ''}📝 {n['timestamp']} のノート（{days}日前）"

        st.markdown(title)
        if manual_text:
            st.write(manual_text[:200] + ("..." if len(manual_text) > 200 else ""))
        if meta.get("tags"):
            st.caption("🏷️ タグ: " + ", ".join(meta["tags"]))
        if meta.get("ref_link"):
            st.caption(f"🔗 [参考リンク]({meta['ref_link']})")

        # 復習状態ボタン
        if status == "done":
            st.success("✅ 復習済み")
        elif status == "skip":
            st.warning("⏭ スキップ済み")
        else:
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"復習完了 #{n['id']}", key=f"done_{n['id']}"):
                    mark_review_done(n["id"], "done")
                    st.experimental_rerun()
            with col2:
                if st.button(f"スキップ #{n['id']}", key=f"skip_{n['id']}"):
                    mark_review_done(n["id"], "skip")
                    st.experimental_rerun()

        st.markdown("---")