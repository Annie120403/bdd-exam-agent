
from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parent

LINKS_PATH = BASE_DIR / "output" / "question_links.json"
CONCEPTS_PATH = BASE_DIR / "knowledge" / "concepts.json"
REVIEWS_PATH = BASE_DIR / "knowledge" / "reviews.json"
OUTPUT_PATH = BASE_DIR / "output" / "reviewed_links.json"


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def main():
    questions = load_json(LINKS_PATH)
    concepts = load_json(CONCEPTS_PATH)
    reviews = load_json(REVIEWS_PATH)

    concept_map = {
        concept["id"]: concept
        for concept in concepts
    }

    # 校验人工审核记录
    review_map = {}

    for review in reviews:
        key = (
            review["question_id"],
            review["concept_id"]
        )

        if key in review_map:
            raise ValueError(f"重复审核记录：{key}")

        if review["concept_id"] not in concept_map:
            raise ValueError(f"未知知识点：{key}")

        if review["decision"] not in ("confirmed", "rejected"):
            raise ValueError(f"无效审核决定：{key}")

        review_map[key] = review

    output = []
    question_ids = set()

    for question in questions:
        question_id = question["question_id"]
        question_ids.add(question_id)

        candidate_concepts = []

        for concept in concepts:
            evidence = []

            for match in question["matches"]:
                if match["keyword"].casefold() in [
                    word.casefold()
                    for word in concept["keywords"]
                ]:
                    evidence.append(match)

            review = review_map.get(
                (question_id, concept["id"])
            )

            if not evidence and review is None:
                continue

            status = "pending_review"

            if review is not None:
                status = review["decision"]

            if status == "confirmed" and not evidence:
                raise ValueError(
                    f"{question_id} / {concept['id']} "
                    "没有可验证的候选证据"
                )

            candidate_concepts.append({
                "concept_id": concept["id"],
                "name": concept["name"],
                "category": concept["category"],
                "difficulty": concept["difficulty"],
                "difficulty_rank": concept["difficulty_rank"],
                "status": status,
                "evidence": evidence
            })

        # 已知难度的知识点由易到难排列
        # 未分级的知识点放在最后
        candidate_concepts.sort(
            key=lambda item: (
                item["difficulty_rank"] is None,
                item["difficulty_rank"]
                if item["difficulty_rank"] is not None
                else float("inf"),
                item["concept_id"]
            )
        )

        output.append({
            "question_id": question_id,
            "question": question["question"],
            "question_source": question["question_source"],
            "question_page": question["question_page"],
            "concepts": candidate_concepts
        })

        print(
            f"{question_id}: "
            f"{len(candidate_concepts)} 个候选知识点"
        )

    # 确保审核记录对应真实题目
    for question_id, concept_id in review_map:
        if question_id not in question_ids:
            raise ValueError(
                f"审核记录引用了未知题目：{question_id}"
            )

    save_json(OUTPUT_PATH, output)

    print("\n知识点关联整理完成！")
    print(f"结果保存至：{OUTPUT_PATH}")


if __name__ == "__main__":
    main()
