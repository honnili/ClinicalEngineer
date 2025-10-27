import sqlite3
import json
from datetime import datetime

DB_PATH = "learning.db"

# -------------------------
# DB初期化
# -------------------------
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        # ユーザー情報（ニックネーム用）
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                email TEXT,
                nickname TEXT
            )
        """)
        # ボス問題アーカイブ
        cur.execute("""
        CREATE TABLE IF NOT EXISTS boss_archive (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            question TEXT,
            options TEXT,
            answer TEXT,
            explanation TEXT,
            choice TEXT,
            correct INTEGER,
            mode TEXT,
            field TEXT,
            difficulty TEXT,
            timestamp TEXT,
            meta TEXT
        )
        """)
        # 問題テーブル
        cur.execute("""
        CREATE TABLE IF NOT EXISTS problems (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            question TEXT,
            options TEXT,
            answer TEXT,
            explanation TEXT,
            mode TEXT,
            field TEXT,
            difficulty TEXT,
            timestamp TEXT
        )
        """)
        # クイズ結果
        cur.execute("""
        CREATE TABLE IF NOT EXISTS quiz_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            tag TEXT,
            correct INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)
        conn.commit()

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

# -------------------------
# ニックネーム関連
# -------------------------
def load_nickname(user_id: str):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT nickname FROM users WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        return row[0] if row else None

def save_nickname(user_id: str, nickname: str, email: str = None):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO users (user_id, email, nickname)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                email=excluded.email,
                nickname=excluded.nickname
        """, (user_id, email, nickname))
        conn.commit()

# -------------------------
# ボス問題アーカイブ保存
# -------------------------
def save_boss_archive(user_id, question, options, answer, explanation,
                      choice, correct, mode, field, difficulty, meta=None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO boss_archive
    (user_id, question, options, answer, explanation, choice, correct,
     mode, field, difficulty, timestamp, meta)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        question,
        json.dumps(options, ensure_ascii=False),
        answer,
        explanation,
        choice,
        1 if correct else 0,
        mode,
        field,
        difficulty,
        datetime.now().isoformat(timespec="seconds"),
        json.dumps(meta or {}, ensure_ascii=False)
    ))
    conn.commit()
    conn.close()

def list_boss_problems():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM boss_archive ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()

    items = []
    for r in rows:
        items.append({
            "id": r[0],
            "user_id": r[1],
            "question": r[2],
            "options": json.loads(r[3]),
            "answer": r[4],
            "explanation": r[5],
            "choice": r[6],
            "correct": bool(r[7]),
            "mode": r[8],
            "field": r[9],
            "difficulty": r[10],
            "timestamp": r[11],
            "meta": json.loads(r[12]) if r[12] else {}
        })
    return items

# -------------------------
# 解答履歴の保存
# -------------------------
def record_result(user_id: str, tag: str, correct: bool):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS quiz_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            tag TEXT,
            correct INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    c.execute(
        "INSERT INTO quiz_results (user_id, tag, correct) VALUES (?, ?, ?)",
        (user_id, tag, 1 if correct else 0)
    )
    conn.commit()
    conn.close()

# -------------------------
# タグごとの正答率を集計
# -------------------------
def get_tag_stats(user_id: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT tag, SUM(correct), COUNT(*)
        FROM quiz_results
        WHERE user_id=?
        GROUP BY tag
    """, (user_id,))
    rows = c.fetchall()
    conn.close()

    stats = {}
    for tag, correct, total in rows:
        stats[tag] = {
            "correct": correct,
            "total": total,
            "rate": round(correct / total * 100, 1) if total > 0 else 0
        }
    return stats

from datetime import date

# -------------------------
# 問題保存
# -------------------------
def save_boss_problem(user_id, difficulty, field, mode, question, options, answer, explanation, meta):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS problems (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            difficulty TEXT,
            field TEXT,
            mode TEXT,
            question TEXT,
            options TEXT,
            answer TEXT,
            explanation TEXT,
            meta TEXT,
            created_at TEXT
        )
    """)
    c.execute("""
        INSERT INTO problems (user_id, difficulty, field, mode, question, options, answer, explanation, meta, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        difficulty,
        field,
        mode,
        question,
        json.dumps(options, ensure_ascii=False),
        answer,
        explanation,
        json.dumps(meta, ensure_ascii=False),
        datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()

# -------------------------
# 図解保存（tags対応）
# -------------------------
def save_diagram_with_manual(user_id, diagram_code=None, notes="", tags=None, image_path=None):
    if tags is None:
        tags = []
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS diagrams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            diagram_code TEXT,
            notes TEXT,
            tags TEXT,
            image_path TEXT,
            created_at TEXT
        )
    """)
    c.execute("""
        INSERT INTO diagrams (user_id, diagram_code, notes, tags, image_path, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        diagram_code,
        notes,
        json.dumps(tags, ensure_ascii=False),
        image_path,
        datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()

# -------------------------
# タグ別問題取得
# -------------------------
def fetch_problems_by_tag(tag, user_id, limit=5):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT id, question, options, answer, explanation, meta
        FROM problems
        WHERE user_id=? AND field=?
        ORDER BY created_at DESC
        LIMIT ?
    """, (user_id, tag, limit))
    rows = c.fetchall()
    conn.close()
    return [
        {
            "id": r[0],
            "question": r[1],
            "options": json.loads(r[2]),
            "answer": r[3],
            "explanation": r[4],
            "meta": json.loads(r[5]) if r[5] else {}
        }
        for r in rows
    ]

# -------------------------
# タグ別図解取得
# -------------------------
def fetch_diagrams_by_tag(tag, user_id, limit=5):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT diagram_code, notes, tags
        FROM diagrams
        WHERE user_id=?
        ORDER BY created_at DESC
        LIMIT ?
    """, (user_id, limit))
    rows = c.fetchall()
    conn.close()

    results = []
    for code, notes, tags_json in rows:
        tags = json.loads(tags_json) if tags_json else []
        if tag in tags:
            results.append({"diagram_mermaid": code, "manual_text": notes, "tags": tags})
    return results

from datetime import date

# -------------------------
# 問題保存
# -------------------------
def save_boss_problem(user_id, difficulty, field, mode, question, options, answer, explanation, meta):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS problems (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            difficulty TEXT,
            field TEXT,
            mode TEXT,
            question TEXT,
            options TEXT,
            answer TEXT,
            explanation TEXT,
            meta TEXT,
            created_at TEXT
        )
    """)
    c.execute("""
        INSERT INTO problems (user_id, difficulty, field, mode, question, options, answer, explanation, meta, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        difficulty,
        field,
        mode,
        question,
        json.dumps(options, ensure_ascii=False),
        answer,
        explanation,
        json.dumps(meta, ensure_ascii=False),
        datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()

# -------------------------
# 図解保存（tags対応）
# -------------------------
def save_diagram_with_manual(user_id, diagram_code=None, notes="", tags=None, image_path=None):
    if tags is None:
        tags = []
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS diagrams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            diagram_code TEXT,
            notes TEXT,
            tags TEXT,
            image_path TEXT,
            created_at TEXT
        )
    """)
    c.execute("""
        INSERT INTO diagrams (user_id, diagram_code, notes, tags, image_path, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        diagram_code,
        notes,
        json.dumps(tags, ensure_ascii=False),
        image_path,
        datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()

# -------------------------
# タグ別問題取得
# -------------------------
def fetch_problems_by_tag(tag, user_id, limit=5):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT id, question, options, answer, explanation, meta
        FROM problems
        WHERE user_id=? AND field=?
        ORDER BY created_at DESC
        LIMIT ?
    """, (user_id, tag, limit))
    rows = c.fetchall()
    conn.close()
    return [
        {
            "id": r[0],
            "question": r[1],
            "options": json.loads(r[2]),
            "answer": r[3],
            "explanation": r[4],
            "meta": json.loads(r[5]) if r[5] else {}
        }
        for r in rows
    ]

# -------------------------
# タグ別図解取得
# -------------------------
def fetch_diagrams_by_tag(tag, user_id, limit=5):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT diagram_code, notes, tags
        FROM diagrams
        WHERE user_id=?
        ORDER BY created_at DESC
        LIMIT ?
    """, (user_id, limit))
    rows = c.fetchall()
    conn.close()

    results = []
    for code, notes, tags_json in rows:
        tags = json.loads(tags_json) if tags_json else []
        if tag in tags:
            results.append({"diagram_mermaid": code, "manual_text": notes, "tags": tags})
    return results

