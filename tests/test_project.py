
import json
import unittest
from pathlib import Path

from precise_search import normalize_with_positions, search


BASE_DIR = Path(__file__).resolve().parents[1]

KNOWLEDGE_PATH = BASE_DIR / "output" / "knowledge_base.json"
CONCEPTS_PATH = BASE_DIR / "knowledge" / "concepts.json"
QUESTIONS_PATH = BASE_DIR / "exams" / "questions.json"
QUIZ_PATH = BASE_DIR / "knowledge" / "quiz_bank.json"
LINKS_PATH = BASE_DIR / "output" / "reviewed_links.json"


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


class TestBDDExamAssistant(unittest.TestCase):

    def test_required_files(self):
        paths = [
            KNOWLEDGE_PATH,
            CONCEPTS_PATH,
            QUESTIONS_PATH,
            QUIZ_PATH,
            LINKS_PATH
        ]

        for path in paths:
            with self.subTest(path=path):
                self.assertTrue(path.is_file())

    def test_knowledge_base(self):
        pages = load_json(KNOWLEDGE_PATH)

        self.assertIsInstance(pages, list)
        self.assertGreater(len(pages), 0)

        for page in pages:
            self.assertIsInstance(page["source"], str)
            self.assertIsInstance(page["page"], int)
            self.assertGreater(page["page"], 0)
            self.assertIsInstance(page["text"], str)

    def test_concepts(self):
        concepts = load_json(CONCEPTS_PATH)

        self.assertIsInstance(concepts, list)

        ids = [item["id"] for item in concepts]

        self.assertEqual(len(ids), len(set(ids)))

        for concept in concepts:
            self.assertIn(
                concept["difficulty"],
                ["easy", "medium", "hard", None]
            )

    def test_questions(self):
        questions = load_json(QUESTIONS_PATH)

        self.assertIsInstance(questions, list)

        for question in questions:
            self.assertIn("id", question)
            self.assertIn("question", question)
            self.assertIsInstance(
                question["keywords"], list
            )

    def test_quiz_bank(self):
        quiz = load_json(QUIZ_PATH)

        self.assertIsInstance(quiz, list)

        ids = [item["id"] for item in quiz]
        self.assertEqual(len(ids), len(set(ids)))

        concepts = load_json(CONCEPTS_PATH)
        concept_ids = {item["id"] for item in concepts}

        for question in quiz:
            self.assertIn(
                question["type"],
                ["multiple_choice", "open"]
            )

            for concept_id in question["concept_ids"]:
                self.assertIn(concept_id, concept_ids)

    def test_reviewed_links(self):
        links = load_json(LINKS_PATH)
        self.assertIsInstance(links, list)

        for question in links:
            self.assertIn("question_id", question)
            self.assertIsInstance(
                question["concepts"], list
            )

            for concept in question["concepts"]:
                self.assertIn(
                    concept["status"],
                    [
                        "confirmed",
                        "rejected",
                        "pending_review"
                    ]
                )

    def test_normalization(self):
        text, positions = normalize_with_positions(
            "Clé Primaire"
        )

        self.assertEqual(text, "cle primaire")
        self.assertEqual(len(text), len(positions))

    def test_search(self):
        sample = [
            {
                "source": "test.pdf",
                "page": 3,
                "text": "La clé primaire est importante."
            }
        ]

        results = search("cle primaire", sample)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["page"], 3)
        self.assertEqual(
            results[0]["source"], "test.pdf"
        )


if __name__ == "__main__":
    unittest.main()
