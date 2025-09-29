import sqlite3
import json
from datetime import datetime
from collections import defaultdict

DB_PATH = "learning.db"

# -------------------------
# 問題保存
# -------------------------
def save_boss_problem(difficulty, field, mode, question, options, answer, explanation, meta):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS problems (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            difficulty TEXT,
            field TEXT,
            mode TEXT,
            question TEXT,
            options TEXT,
            answer TEXT,
            explanation TEXT,
            meta TEXT
        )
    """)
    c.execute("""
        INSERT INTO problems (difficulty, field, mode, question, options, answer, explanation, meta)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        difficulty,
        field,
        mode,
        question,
        json.dumps(options, ensure_ascii=False),
        answer,
        explanation,
        json.dumps(meta, ensure_ascii=False)
    ))
    conn.commit()
    conn.close()

# -------------------------
# ノート保存
# -------------------------
def save_note(kind, text):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kind TEXT,
            text TEXT,
            created_at TEXT
        )
    """)
    c.execute("""
        INSERT INTO notes (kind, text, created_at)
        VALUES (?, ?, ?)
    """, (kind, text, datetime.now().isoformat()))
    conn.commit()
    conn.close()

# -------------------------
# 解答履歴保存
# -------------------------
def save_answer_history(problem_id, tags, is_correct):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS answer_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            problem_id TEXT,
            tags TEXT,
            is_correct INTEGER,
            timestamp TEXT
        )
    """)
    c.execute("""
        INSERT INTO answer_history (problem_id, tags, is_correct, timestamp)
        VALUES (?, ?, ?, ?)
    """, (
        problem_id,
        json.dumps(tags, ensure_ascii=False),
        1 if is_correct else 0,
        datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()

# -------------------------
# タグ統計取得
# -------------------------
def get_tag_statistics(threshold=0.7):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT tags, is_correct FROM answer_history")
    rows = c.fetchall()
    conn.close()

    tag_stats = defaultdict(lambda: {"correct": 0, "total": 0})

    for tags_json, is_correct in rows:
        try:
            tags = json.loads(tags_json)
        except:
            tags = []
        for tag in tags:
            tag_stats[tag]["total"] += 1
            if is_correct == 1:
                tag_stats[tag]["correct"] += 1

    results = []
    for tag, stats in tag_stats.items():
        total = stats["total"]
        correct = stats["correct"]
        accuracy = correct / total if total > 0 else 0
        results.append({
            "tag": tag,
            "total": total,
            "correct": correct,
            "accuracy": accuracy,
            "is_weak": accuracy < threshold
        })

    return sorted(results, key=lambda x: x["accuracy"])

# -------------------------
# タグで問題取得（復習用）
# -------------------------
def fetch_problems_by_tag(tag, limit=5):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, question, options, answer, explanation, meta FROM problems")
    rows = c.fetchall()
    conn.close()

    results = []
    for row in rows:
        pid, q, opts, ans, exp, meta_json = row
        try:
            meta = json.loads(meta_json)
        except:
            meta = {}
        tags = meta.get("tags", [])
        if tag in tags:
            results.append({
                "id": pid,
                "question": q,
                "options": json.loads(opts) if opts else [],
                "answer": ans,
                "explanation": exp,
                "tags": tags
            })
    return results[:limit]