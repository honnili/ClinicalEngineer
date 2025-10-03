import sqlite3
import json
from services.db_utils import DB_PATH

# -------------------------
# 復習対象を抽出
# -------------------------
def get_review_targets(notes, days_threshold=3):
    """
    ノート一覧から復習対象を抽出する。
    ここではダミーで全ノートを対象にしている。
    将来的には created_at から経過日数を計算してフィルタする。
    """
    targets = []
    for n in notes:
        # ダミー: 全部対象にする（days=1固定）
        targets.append((n, 1))
    return targets


# -------------------------
# 復習状態を取得
# -------------------------
def get_review_status(note_id: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS review_status (
            note_id INTEGER PRIMARY KEY,
            status TEXT,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    c.execute("SELECT status FROM review_status WHERE note_id=?", (note_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else "pending"


# -------------------------
# 復習状態を更新
# -------------------------
def mark_review_done(note_id: int, status: str = "done"):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS review_status (
            note_id INTEGER PRIMARY KEY,
            status TEXT,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    c.execute("INSERT OR REPLACE INTO review_status (note_id, status) VALUES (?, ?)", (note_id, status))
    conn.commit()
    conn.close()