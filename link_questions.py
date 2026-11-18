
from pathlib import Path
import json

from precise_search import search


BASE_DIR = Path(__file__).resolve().parent

KNOWLEDGE_PATH = BASE_DIR / "output" / "knowledge_base.json"
QUESTIONS_PATH = BASE_DIR / "exams" / "questions.json"
OUTPUT_PATH = BASE_DIR / "output" / "question_links.json"


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def main():
    knowledge_base = load_json(KNOWLEDGE_PATH)
    questions = load_json(QUESTIONS_PATH)

    # 避免把考试真题误当作课程知识来源
    exam_sources = {
        question["source"] for question in questions
    }

    course_pages = [
        page for page in knowledge_base
        if page["source"] not in exam_sources
    ]

    linked_questions = []

    for question in questions:
        matches = []

        for keyword in question["keywords"]:
            results = search(keyword, course_pages)

            for result in results:
                matches.append({
                    "keyword": keyword,
                    "source": result["source"],
                    "page": result["page"],
                    "context": result["context"]
                })

        # 相同关键词、文件、页码和上下文去重
        unique_matches = []
        seen = set()

        for match in matches:
            key = (
                match["keyword"],
                match["source"],
                match["page"],
                match["context"]
            )

            if key not in seen:
                seen.add(key)
                unique_matches.append(match)

        linked_questions.append({
            "question_id": question["id"],
            "question_source": question["source"],
            "question_page": question["page"],
            "question": question["question"],
            "difficulty": question["difficulty"],
            "status": "pending_review",
            "matches": unique_matches
        })

        print(
            f"{question['id']}: "
            f"找到 {len(unique_matches)} 条候选关联"
        )

    with open(OUTPUT_PATH, "w", encoding="utf-8") as file:
        json.dump(
            linked_questions,
            file,
            ensure_ascii=False,
            indent=4
        )

    print("\n真题候选关联完成！")
    print(f"结果已保存：{OUTPUT_PATH}")


if __name__ == "__main__":
    main()
