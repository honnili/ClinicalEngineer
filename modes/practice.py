import streamlit as st
import io
from streamlit_drawable_canvas import st_canvas
from services.db_utils import save_note, list_notes
from services.gpt_utils import summarize_notes


def _map_kind(kind):
    return {
        "自由ノート": "free",
        "罫線ノート": "ruled",
        "方眼ノート": "grid",
        "日報テンプレート": "report"
    }.get(kind, "free")  # 万一未定義の値が来ても "free" にフォールバック


def render():
    st.subheader("📝 実習モード（ノート／メモ）")

    # ノートタイプ
    note_kind = st.radio(
        "ノートタイプ",
        ["自由ノート", "罫線ノート", "方眼ノート", "日報テンプレート"],
        horizontal=True
    )

    # テキストメモ
    text = st.text_area("テキストメモ", height=120, placeholder="重要点・手順・注意事項など")

    # キャンバス
    st.write("🖍 キャンバス（色分け・マーカー・けしごむ対応）")
    canvas = st_canvas(
        fill_color="rgba(255,255,255,0)",
        stroke_width=3,
        stroke_color="#e74c3c",
        background_color="#FFFFFF",
        height=300,
        width=600,
        drawing_mode="freedraw",
        key=f"note_canvas_{note_kind}"
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("保存"):
            img_bytes = None
            if canvas.image_data is not None:
                import PIL.Image
                im = PIL.Image.fromarray(canvas.image_data)
                buf = io.BytesIO()
                im.save(buf, format="PNG")
                img_bytes = buf.getvalue()

            save_note(
                kind=_map_kind(note_kind),
                text=text,
                image_bytes=img_bytes,
                user_id=st.session_state.get("user_id", "global")
            )
            st.success("保存しました。")

    with col2:
        if st.button("要約（AI）"):
            if text.strip():
                summary = summarize_notes(text)
                st.info(summary)
            else:
                st.warning("テキストメモが空です。要約対象がありません。")

    with col3:
        st.button("クリア", on_click=lambda: _clear_canvas_state(note_kind))

    st.markdown("### 保存済みノート一覧")
    notes = list_notes(user_id=st.session_state.get("user_id", "global"))
    if notes:
        for n in notes[:50]:
            st.write(f"[{n['timestamp']}] {n['kind']}: {n['text'][:100]}")
    else:
        st.write("まだ保存されたノートはありません。")


def _clear_canvas_state(kind):
    st.session_state.pop(f"note_canvas_{kind}", None)