# utils/review.py
import datetime

def get_review_targets(notes):
    """
    ノート一覧から復習対象を抽出する
    - 保存から1日後・7日後・30日後のノートを返す
    """
    today = datetime.date.today()
    targets = []
    for n in notes:
        try:
            note_date = datetime.datetime.strptime(n["timestamp"], "%Y-%m-%d %H:%M:%S").date()
        except Exception:
            continue
        days = (today - note_date).days
        if days in [1, 7, 30]:
            targets.append((n, days))
    return targets