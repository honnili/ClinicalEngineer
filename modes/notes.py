import streamlit as st

from services.db_utils import save_note, list_notes
from services.diagram_utils import generate_diagram
from services.ai_utils import generate_quiz, generate_tags
import json, io
from PIL import Image

def render():
    st.subheader("📝 実習ノート（完全統合版）")

    # --- ペンUI ---
    pen_mode = st.radio("ペンの種類", ["ボールペン", "マーカー"], horizontal=True)
    if pen_mode == "ボールペン":
        color = st.radio("色", ["black", "red", "blue"], horizontal=True)
        stroke_width = 3
    else:
        color_name = st.radio("色", ["green", "yellow"], horizontal=True)
        color = "rgba(0,255,0,0.4)" if color_name == "green" else "rgba(255,255,0,0.4)"
        stroke_width = 15

    canvas_result = st_canvas(
        fill_color="rgba(255, 255, 255, 0)",
        stroke_width=stroke_width,
        stroke_color=color,
        background_color="#fff",
        update_streamlit=True,
        height=300,
        drawing_mode="freedraw",
        key="canvas",
    )

    # --- マニュアル ---
    manual_text = st.text_area("📖 マニュアル抜粋やメモ")

    # --- 図解 ---
    diagram_prompt = st.text_input("📊 図解生成プロンプト", "ICU Ventilator の仕組み")
    diagram_bytes = None
    if st.button("図解を生成してプレビュー"):
        diagram = generate_diagram(diagram_prompt)
        if diagram:
            st.image(diagram, caption="生成した図解")
            diagram_bytes = diagram

    # --- タグ & リンク ---
    # 手動タグに加えてAI自動タグも生成
    manual_tags = st.multiselect("🏷️ タグを追加", ["呼吸器", "循環", "薬理", "看護技術", "解剖", "病態"])
    ref_link = st.text_input("🔗 参考文献や論文のURL（任意）")

    # --- 保存 ---
    if st.button("保存する"):
        img_bytes = None
        if canvas_result.image_data is not None:
            img = Image.fromarray((canvas_result.image_data[:, :, :3]).astype("uint8"))
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            img_bytes = buf.getvalue()
        elif diagram_bytes is not None:
            img_bytes = diagram_bytes

        # AIでタグ自動生成
        auto_tags = generate_tags(manual_text) if manual_text else []
        tags = list(set(manual_tags + auto_tags))

        meta = {"tags": tags, "ref_link": ref_link}
        save_note(
            kind="report",
            text=json.dumps({"manual": manual_text, "meta": meta}, ensure_ascii=False),
            image_bytes=img_bytes
        )
        st.success(f"ノートを保存しました！（タグ: {', '.join(tags)}）")

    # --- 検索フィルタ ---
    st.markdown("---")
    st.subheader("📚 保存済みノート")
    search_tags = st.multiselect("タグで絞り込み", ["呼吸器", "循環", "薬理", "看護技術", "解剖", "病態"])
    keyword = st.text_input("キーワード検索")

    notes = list_notes()
    if not notes:
        st.info("まだノートはありません。")
        return

    grouped = {}
    for n in notes:
        grouped.setdefault(n["timestamp"][:10], []).append(n)

    for date, items in grouped.items():
        filtered = []
        for it in items:
            try:
                parsed = json.loads(it["text"])
                manual_text = parsed.get("manual", "")
                meta = parsed.get("meta", {})
            except Exception:
                manual_text = it["text"]
                meta = {}

            if search_tags and not set(search_tags).issubset(set(meta.get("tags", []))):
                continue
            if keyword and keyword not in manual_text:
                continue

            filtered.append((it, manual_text, meta))

        if not filtered:
            continue

        with st.expander(f"{date} のノートまとめ"):
            for it, manual_text, meta in filtered:
                st.markdown(f"### 📝 {it['timestamp']}")
                if manual_text:
                    st.write(manual_text)
                if meta.get("tags"):
                    st.write("🏷️ タグ:", ", ".join(meta["tags"]))
                if meta.get("ref_link"):
                    st.write(f"🔗 [参考リンク]({meta['ref_link']})")

                # --- AIクイズ化 ---
                if st.button(f"このノートからクイズを作る #{it['id']}", key=f"quiz_{it['id']}"):
                    quiz = generate_quiz(manual_text)
                    if isinstance(quiz, dict):
                        st.write("Q:", quiz.get("question", ""))
                        if quiz.get("answer"):
                            st.info(f"答え: {quiz['answer']}")
                    else:
                        st.write(quiz)