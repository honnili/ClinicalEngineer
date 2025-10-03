# services/ocr_utils.py
import pytesseract
import cv2
import numpy as np
from PIL import Image

def run_ocr(image_input, lang="jpn"):
    """
    画像またはnumpy配列からテキストを抽出する
    """
    if isinstance(image_input, np.ndarray):
        img = cv2.cvtColor(image_input, cv2.COLOR_RGBA2RGB)
    else:
        img = Image.open(image_input)

    text = pytesseract.image_to_string(img, lang=lang)
    return text.strip()


def generate_tags(text: str, max_tags: int = 5):
    """
    ノートや回答テキストからタグを自動生成する
    """
    prompt = f"""
    次の文章から重要なキーワードを抽出し、{max_tags} 個以内のタグを日本語で出力してください。
    出力はJSON配列形式で返してください。
    文章: {text}
    """

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an assistant that extracts concise study tags."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
    )

    # JSON配列をパース
    import json, re
    raw = resp.choices[0].message.content.strip()
    match = re.search(r"\[.*\]", raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except:
            return [raw]
    return [raw]