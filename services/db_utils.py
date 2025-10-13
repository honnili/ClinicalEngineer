import sqlite3
import json
from datetime import datetime, date


DB_PATH = "learning.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()


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

    # ← ここに problems テーブルを追加
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

    conn.commit()
    conn.close()

def get_connection():
    # DB に接続してコネクションを返す
    return sqlite3.connect(DB_PATH, check_same_thread=False)




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

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                email TEXT,
                nickname TEXT
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                kind TEXT,
                text TEXT,
                image BLOB,
                timestamp TEXT
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS review_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                note_id INTEGER,
                user_id TEXT,
                done_at TEXT
            )
        """)
        conn.commit()


def list_notes(user_id: str = "global"):
    """
    保存済みノートを一覧で返す
    """
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM notes WHERE user_id = ? ORDER BY timestamp DESC", (user_id,))
        return [dict(row) for row in cur.fetchall()]

def mark_review_done(note_id: int, user_id: str = "global"):
    """
    指定したノートを復習済みにマーク（履歴を残す）
    """
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS review_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                note_id INTEGER,
                user_id TEXT,
                done_at TEXT
            )
        """)
        cur.execute(
            "INSERT INTO review_status (note_id, user_id, done_at) VALUES (?, ?, ?)",
            (note_id, user_id, datetime.now().isoformat())
        )
        conn.commit()

def get_review_status(note_id: int, user_id: str = "global"):
    """
    指定したノートの復習履歴を返す（最新が先頭）
    """
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT done_at FROM review_status
            WHERE note_id = ? AND user_id = ?
            ORDER BY done_at DESC
        """, (note_id, user_id))
        rows = cur.fetchall()
        return [r[0] for r in rows]


def get_tag_stats(user_id: str = "global"):
    """
    タグごとのノート数と復習済み数を返す
    """
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        # ノートを取得
        cur.execute("SELECT id, text FROM notes WHERE user_id = ?", (user_id,))
        notes = cur.fetchall()

        stats = {}
        for n in notes:
            try:
                import json
                parsed = json.loads(n["text"])
                tags = parsed.get("meta", {}).get("tags", [])
            except Exception:
                tags = []

            for tag in tags:
                stats.setdefault(tag, {"total": 0, "reviewed": 0})
                stats[tag]["total"] += 1

                # 復習済みか確認
                cur.execute(
                    "SELECT COUNT(*) FROM review_status WHERE note_id = ? AND user_id = ?",
                    (n["id"], user_id)
                )
                count = cur.fetchone()[0]
                if count > 0:
                    stats[tag]["reviewed"] += 1

        return stats

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


# -------------------------
# タグ別統計
# -------------------------
def get_tag_statistics(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS answer_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            problem_id INTEGER,
            is_correct INTEGER,
            answered_at TEXT
        )
    """)
    c.execute("""
        SELECT p.field, SUM(a.is_correct), COUNT(*)
        FROM answer_history a
        JOIN problems p ON a.problem_id = p.id
        WHERE a.user_id=?
        GROUP BY p.field
    """, (user_id,))
    rows = c.fetchall()
    conn.close()

    stats = {}
    for field, correct, total in rows:
        stats[field] = {
            "correct": correct,
            "total": total,
            "accuracy": (correct / total * 100) if total > 0 else 0.0
        }
    return stats


# -------------------------
# デイリー問題（1日1回キャッシュ）
# -------------------------
def get_or_create_daily(kind: str, generator_func, user_id: str = "global"):
    today = date.today().isoformat()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS daily (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            kind TEXT,
            day TEXT,
            content TEXT
        )
    """)
    c.execute(
        "SELECT content FROM daily WHERE user_id=? AND kind=? AND day=?",
        (user_id, kind, today)
    )
    row = c.fetchone()
    if row:
        conn.close()
        return json.loads(row[0])

    data = generator_func()
    c.execute(
        "INSERT INTO daily (user_id, kind, day, content) VALUES (?,?,?,?)",
        (user_id, kind, today, json.dumps(data, ensure_ascii=False))
    )
    conn.commit()
    conn.close()
    return data


# -------------------------
# ボス問題一覧取得
# -------------------------
def list_boss_problems(user_id: str = "global", limit: int = 20):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT id, question, options, answer, explanation, meta, difficulty, field, mode, created_at
        FROM problems
        WHERE user_id=? AND (mode='boss' OR mode='scenario')
        ORDER BY created_at DESC
        LIMIT ?
    """, (user_id, limit))
    rows = c.fetchall()
    conn.close()

    results = []
    for r in rows:
        results.append({
            "id": r[0],
            "question": r[1],
            "options": json.loads(r[2]) if r[2] else [],
            "answer": r[3],
            "explanation": r[4],
            "meta": json.loads(r[5]) if r[5] else {},
            "difficulty": r[6],
            "field": r[7],
            "mode": r[8],
            "timestamp": r[9]
        })
    return results


