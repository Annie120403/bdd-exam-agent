
from pathlib import Path
import json
from collections import Counter


BASE_DIR = Path(__file__).resolve().parent

CONCEPTS_PATH = BASE_DIR / "knowledge" / "concepts.json"
LINKS_PATH = BASE_DIR / "output" / "reviewed_links.json"
OUTPUT_PATH = BASE_DIR / "output" / "difficulty_report.json"

VALID_LEVELS = {
    "easy": 1,
    "medium": 2,
    "hard": 3
}


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def validate_concepts(concepts):
    for concept in concepts:
        level = concept["difficulty"]
        rank = concept["difficulty_rank"]

        if level is None and rank is None:
            continue

        if level not in VALID_LEVELS:
            raise ValueError(
                f"{concept['id']} 的难度等级无效"
            )

        if rank != VALID_LEVELS[level]:
            raise ValueError(
                f"{concept['id']} 的等级与排序值不一致"
            )


def sort_key(concept):
    rank = concept["difficulty_rank"]

    return (
        rank is None,
        rank if rank is not None else 999,
        concept["concept_id"]
    )


def main():
    concepts = load_json(CONCEPTS_PATH)
    questions = load_json(LINKS_PATH)

    validate_concepts(concepts)

    concept_map = {
        concept["id"]: concept
        for concept in concepts
    }

    report = {
        "difficulty_scale": VALID_LEVELS,
        "concepts": [],
        "questions": [],
        "unlinked_concepts": []
    }

    linked_concept_ids = set()
    confirmed_counts = Counter()

    for question in questions:
        sorted_concepts = []

        for item in question["concepts"]:
            concept_id = item["concept_id"]

            if concept_id not in concept_map:
                raise ValueError(
                    f"未知知识点：{concept_id}"
                )

            concept = concept_map[concept_id]
            status = item["status"]

            if status == "rejected":
                continue

            if status == "confirmed":
                linked_concept_ids.add(concept_id)
                confirmed_counts[concept_id] += 1

            sorted_concepts.append({
                "concept_id": concept_id,
                "name": concept["name"],
                "category": concept["category"],
                "difficulty": concept["difficulty"],
                "difficulty_rank": concept["difficulty_rank"],
                "status": status,
                "evidence": item["evidence"]
            })

        sorted_concepts.sort(key=sort_key)

        report["questions"].append({
            "question_id": question["question_id"],
            "question": question["question"],
            "source": question["question_source"],
            "page": question["question_page"],
            "sorted_concepts": sorted_concepts
        })

    for concept in concepts:
        concept_id = concept["id"]

        record = {
            "concept_id": concept_id,
            "name": concept["name"],
            "category": concept["category"],
            "difficulty": concept["difficulty"],
            "difficulty_rank": concept["difficulty_rank"],
            "confirmed_question_count": confirmed_counts[
                concept_id
            ]
        }

        report["concepts"].append(record)

        if concept_id not in linked_concept_ids:
            report["unlinked_concepts"].append(record)

    report["concepts"].sort(
        key=lambda item: (
            item["difficulty_rank"] is None,
            item["difficulty_rank"]
            if item["difficulty_rank"] is not None
            else 999,
            item["concept_id"]
        )
    )

    save_json(OUTPUT_PATH, report)

    print("\n知识点难度排序完成！")
    print(f"知识点总数：{len(report['concepts'])}")
    print(f"真题总数：{len(report['questions'])}")
    print(
        "尚无已确认真题关联的知识点："
        f"{len(report['unlinked_concepts'])}"
    )

    for question in report["questions"]:
        print(f"\n{question['question_id']}")

        for concept in question["sorted_concepts"]:
            level = concept["difficulty"] or "unclassified"

            print(
                f"  {concept['concept_id']} "
                f"| {level} "
                f"| {concept['status']}"
            )

    print(f"\n报告保存至：{OUTPUT_PATH}")


if __name__ == "__main__":
    main()
