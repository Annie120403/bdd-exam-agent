
from pathlib import Path
from datetime import datetime
import json
import random


BASE_DIR = Path(__file__).resolve().parent

QUIZ_PATH = BASE_DIR / "knowledge" / "quiz_bank.json"
CONCEPTS_PATH = BASE_DIR / "knowledge" / "concepts.json"

RESULTS_PATH = BASE_DIR / "output" / "quiz_results.json"
REPORT_PATH = BASE_DIR / "output" / "quiz_report.json"


def load_json(path, default=None):
    if not path.exists():
        if default is not None:
            return default
        raise FileNotFoundError(path)

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_json(path, data):
    path.parent.mkdir(exist_ok=True)

    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def choose_difficulty():
    print("\n请选择难度：")
    print("1. Easy")
    print("2. Medium")
    print("3. Hard")
    print("4. All")

    choices = {
        "1": "easy",
        "2": "medium",
        "3": "hard",
        "4": "all"
    }

    while True:
        choice = input("请选择 1-4：").strip()

        if choice in choices:
            return choices[choice]

        print("输入无效，请重新选择。")


def choose_concept(concepts):
    print("\n请选择知识点：")
    print("0. 全部知识点")

    for index, concept in enumerate(concepts, start=1):
        print(
            f"{index}. {concept['id']} - {concept['name']}"
        )

    while True:
        choice = input("请输入编号：").strip()

        if choice == "0":
            return None

        if choice.isdigit():
            index = int(choice) - 1

            if 0 <= index < len(concepts):
                return concepts[index]["id"]

        print("编号无效，请重新输入。")


def select_questions(questions, difficulty, concept_id):
    selected = []

    for question in questions:
        if difficulty != "all":
            if question["difficulty"] != difficulty:
                continue

        if concept_id is not None:
            if concept_id not in question["concept_ids"]:
                continue

        selected.append(question)

    random.shuffle(selected)

    return selected


def ask_question(question, number):
    print("\n" + "=" * 60)
    print(f"第 {number} 题 | {question['difficulty']}")
    print(question["question"])

    if question["type"] == "multiple_choice":
        for key, value in question["options"].items():
            print(f"{key}. {value}")

        valid_options = set(question["options"])

        while True:
            answer = input("你的答案：").strip().upper()

            if answer in valid_options:
                break

            print("请输入有效选项。")

        if (
            question.get("verified") is True
            and question.get("answer") in valid_options
        ):
            correct = answer == question["answer"]

            if correct:
                print("回答正确！")
            else:
                print("回答错误。")

            print(f"标准答案：{question['answer']}")
            return answer, correct

        print("此题答案尚未核验，不自动评分。")
        return answer, None

    if question["type"] == "open":
        answer = input("请输入你的回答：").strip()

        reference = question.get("answer")

        if question.get("verified") and reference:
            print(f"\n参考答案：{reference}")
        else:
            print("\n参考答案尚未核验。")

        print("开放题保留人工评分。")
        return answer, None

    raise ValueError(
        f"不支持的题型：{question['type']}"
    )


def generate_report(results):
    total = len(results)

    graded = [
        item for item in results
        if item["correct"] is not None
    ]

    correct_count = sum(
        item["correct"] is True
        for item in graded
    )

    by_concept = {}

    for item in results:
        for concept_id in item["concept_ids"]:
            if concept_id not in by_concept:
                by_concept[concept_id] = {
                    "attempted": 0,
                    "graded": 0,
                    "correct": 0
                }

            stats = by_concept[concept_id]
            stats["attempted"] += 1

            if item["correct"] is not None:
                stats["graded"] += 1

                if item["correct"]:
                    stats["correct"] += 1

    for stats in by_concept.values():
        if stats["graded"] > 0:
            stats["accuracy"] = round(
                stats["correct"] / stats["graded"] * 100,
                2
            )
        else:
            stats["accuracy"] = None

    return {
        "timestamp": datetime.now().isoformat(),
        "total_questions": total,
        "graded_questions": len(graded),
        "correct_answers": correct_count,
        "accuracy": (
            round(correct_count / len(graded) * 100, 2)
            if graded else None
        ),
        "by_concept": by_concept
    }


def main():
    questions = load_json(QUIZ_PATH)
    concepts = load_json(CONCEPTS_PATH)

    # 仅使用明确标记为已核验的客观题
    # 未核验题仍可用于练习，但不会自动评分
    difficulty = choose_difficulty()
    concept_id = choose_concept(concepts)

    selected = select_questions(
        questions,
        difficulty,
        concept_id
    )

    if not selected:
        print("\n没有符合条件的测试题。")
        return

    print(f"\n找到 {len(selected)} 道题。")

    while True:
        value = input(
            "请输入测试题数（输入 all 使用全部）："
        ).strip().lower()

        if value == "all":
            count = len(selected)
            break

        if value.isdigit() and 1 <= int(value) <= len(selected):
            count = int(value)
            break

        print("题数无效，请重新输入。")

    selected = selected[:count]

    results = []

    for index, question in enumerate(selected, start=1):
        answer, correct = ask_question(question, index)

        results.append({
            "question_id": question["id"],
            "concept_ids": question["concept_ids"],
            "difficulty": question["difficulty"],
            "type": question["type"],
            "user_answer": answer,
            "correct": correct
        })

    history = load_json(RESULTS_PATH, default=[])
    history.append({
        "timestamp": datetime.now().isoformat(),
        "results": results
    })

    save_json(RESULTS_PATH, history)

    report = generate_report(results)
    save_json(REPORT_PATH, report)

    print("\n测试完成！")
    print(f"总题数：{report['total_questions']}")
    print(f"已评分题数：{report['graded_questions']}")

    if report["accuracy"] is not None:
        print(f"正确率：{report['accuracy']}%")
    else:
        print("本次测试没有可自动评分的题目。")

    print(f"答题记录：{RESULTS_PATH}")
    print(f"复习报告：{REPORT_PATH}")


if __name__ == "__main__":
    main()
