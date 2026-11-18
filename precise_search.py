
from pathlib import Path
import json
import re
import unicodedata


BASE_DIR = Path(__file__).resolve().parent
KNOWLEDGE_PATH = BASE_DIR / "output" / "knowledge_base.json"
RESULT_PATH = BASE_DIR / "output" / "search_results.json"


def normalize_with_positions(text):
    normalized = []
    positions = []

    for i, char in enumerate(text):
        decomposed = unicodedata.normalize(
            "NFD", char.casefold()
        )

        for letter in decomposed:
            if unicodedata.category(letter) == "Mn":
                continue

            if letter.isspace():
                letter = " "

            normalized.append(letter)
            positions.append(i)

    return "".join(normalized), positions


def search(keyword, knowledge_base, context_size=200):
    results = []

    normalized_keyword, _ = normalize_with_positions(
        keyword.strip()
    )

    if not normalized_keyword:
        return results

    for page in knowledge_base:
        text = page["text"]
        normalized_text, positions = normalize_with_positions(text)

        for match in re.finditer(
            re.escape(normalized_keyword),
            normalized_text
        ):
            start = positions[match.start()]
            end = positions[match.end() - 1] + 1

            context_start = max(0, start - context_size)
            context_end = min(len(text), end + context_size)

            results.append({
                "keyword": keyword,
                "source": page["source"],
                "page": page["page"],
                "matched_text": text[start:end],
                "context": text[context_start:context_end],
                "start": start,
                "end": end
            })

    return results


def main():
    if not KNOWLEDGE_PATH.exists():
        print("请先运行 batch_ocr.py")
        return

    with open(KNOWLEDGE_PATH, "r", encoding="utf-8") as file:
        knowledge_base = json.load(file)

    keyword = input("请输入知识点关键词：").strip()

    results = search(keyword, knowledge_base)

    print(f"\n找到 {len(results)} 处匹配结果\n")

    for result in results:
        print("=" * 60)
        print(f"文件：{result['source']}")
        print(f"页码：{result['page']}")
        print(f"匹配：{result['matched_text']}")
        print(f"原文：\n{result['context']}\n")

    with open(RESULT_PATH, "w", encoding="utf-8") as file:
        json.dump(results, file, ensure_ascii=False, indent=4)

    print(f"搜索结果已保存：{RESULT_PATH}")


if __name__ == "__main__":
    main()
