
from pathlib import Path
import json
import re

BASE_DIR = Path(__file__).resolve().parent

TXT_PATH = BASE_DIR / "output" / "C1-E_A.txt"
JSON_PATH = BASE_DIR / "output" / "C1-E_A.json"


def main():
    text = TXT_PATH.read_text(encoding="utf-8")

    parts = re.split(r"===== Page (\d+) =====", text)

    pages = []

    for i in range(1, len(parts), 2):
        page_number = int(parts[i])
        page_text = parts[i + 1].strip()

        pages.append({
            "source": "C1-E_A.pdf",
            "page": page_number,
            "text": page_text
        })

    with open(JSON_PATH, "w", encoding="utf-8") as file:
        json.dump(pages, file, ensure_ascii=False, indent=4)

    print(f"成功处理 {len(pages)} 页")
    print(f"JSON 已保存到：{JSON_PATH}")


if __name__ == "__main__":
    main()
