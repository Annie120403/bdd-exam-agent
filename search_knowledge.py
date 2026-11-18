
from pathlib import Path
import json
import re
import unicodedata


BASE_DIR = Path(__file__).resolve().parent

KNOWLEDGE_PATH = (
    BASE_DIR / "output" / "knowledge_base.json"
)


def normalize(text):
    # 统一大小写
    text = text.casefold()

    # 去除法语重音符号
    text = unicodedata.normalize("NFD", text)

    text = "".join(
        char for char in text
        if unicodedata.category(char) != "Mn"
    )

    # 统一空格和换行
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def load_knowledge():
    with open(KNOWLEDGE_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def search(keyword, knowledge_base):
    results = []

    normalized_keyword = normalize(keyword)

    if not normalized_keyword:
        return results

    for page in knowledge_base:
        text = page["text"]

        if normalized_keyword in normalize(text):
            results.append({
                "source": page["source"],
                "page": page["page"],
                "text": text
            })

    return results


def show_results(results):
    if not results:
        print("\n没有找到相关内容。")
        return

    print(f"\n共找到 {len(results)} 个相关页面。\n")

    for index, result in enumerate(results, start=1):
        print("=" * 60)
        print(f"结果 {index}")
        print(f"文件：{result['source']}")
        print(f"页码：{result['page']}")
        print("-" * 60)

        text = result["text"]

        # 暂时只显示每页前 500 个字符
        print(text[:500])

        if len(text) > 500:
            print("\n...内容已截断")

        print()


def main():
    if not KNOWLEDGE_PATH.exists():
        print("找不到 knowledge_base.json")
        print("请先运行 python batch_ocr.py")
        return

    knowledge_base = load_knowledge()

    print("BDD Exam Assistant - 知识点搜索")
    print(f"已加载 {len(knowledge_base)} 页资料")
    print("输入 exit 退出程序")

    while True:
        keyword = input("\n请输入搜索关键词：").strip()

        if keyword.lower() == "exit":
            print("搜索结束。")
            break

        if not keyword:
            print("关键词不能为空。")
            continue

        results = search(keyword, knowledge_base)
        show_results(results)


if __name__ == "__main__":
    main()
