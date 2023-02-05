import os
from os import environ
import unittest
import json
from unittest.mock import patch

from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def question_factory(self):
        new_question = Question(**self.new_question)
        new_question.insert()

        return new_question

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app(test_config=True)
        self.client = self.app.test_client
        database_name = environ.get("DATABASE_NAME", "trivia_test")
        database_host = environ.get("DATABASE_HOST", "localhost")
        database_port = environ.get("DATABASE_PORT", "5432")

        self.database_path = "postgresql://{}:{}/{}".format(
            database_host,
            database_port,
            database_name,
        )
        setup_db(self.app, self.database_path)

        self.categories = {
            "1": "Science",
            "2": "Art",
            "3": "Geography",
            "4": "History",
            "5": "Entertainment",
            "6": "Sports",
        }
        self.category_type = self.categories["1"]
        # Based on trivia.psql
        self.total_categories = len(self.categories)

        self.new_question = {
            "question": "Test question",
            "answer": "Test answer",
            "difficulty": 5,
            "category": 1,
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)

    def tearDown(self):
        # Remove any questions created by our question factory
        questions = Question.query.filter(
            Question.question == self.new_question["question"]
        )
        for question in questions:
            question.delete()

    def test_get_categories_200(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["categories"], self.categories)
        self.assertEqual(data["total_categories"], self.total_categories)

    def test_get_questions_200(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(
            data["questions"][0],
            {
                "answer": "Apollo 13",
                "category": 5,
                "difficulty": 4,
                "id": 2,
                "question": "What movie earned Tom Hanks his third straight Oscar nomination, "
                "in 1996?",
            },
        )
        total_questions = Question.query.count()
        self.assertEqual(data["total_questions"], total_questions)
        self.assertEqual(data["categories"], self.categories)
        self.assertEqual(data["current_category"], self.category_type)

    def test_delete_question_200(self):
        question = self.question_factory()
        res = self.client().delete(f"/questions/{question.id}")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["deleted"], question.id)
        self.assertEqual(data["message"], "Question was successfully deleted.")

    def test_delete_question_404(self):
        res = self.client().delete("/questions/1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    @patch("models.Question.delete")
    def test_delete_question_422(self, mock_insert):
        # Mocking question insert to simulate a database error
        mock_insert.side_effect = Exception()
        question = self.question_factory()
        res = self.client().delete(f"/questions/{question.id}")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")

    def test_create_question_200(self):
        res = self.client().post("/questions", json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    @patch("models.Question.insert")
    def test_create_question_422(self, mock_insert):
        # Mocking question insert to simulate a database error
        mock_insert.side_effect = Exception()
        res = self.client().post("/questions", json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")

    def test_create_question_400(self):
        res = self.client().post("/questions", json={})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "bad request")

    def test_search_questions_200(self):
        question = self.question_factory()
        res = self.client().post("/questions/search", json={"searchTerm": "test"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["questions"][0], question.format())
        self.assertEqual(data["total_questions"], 1)
        self.assertEqual(data["current_category"], str(self.category_type))

    def test_search_questions_no_data_200(self):
        res = self.client().post("/questions/search", json={"searchTerm": "test"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["questions"], [])
        self.assertEqual(data["total_questions"], 0)
        self.assertEqual(data["current_category"], None)

    def test_search_questions_400(self):
        res = self.client().post("/questions/search", json={})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "bad request")

    def test_get_questions_by_category_200(self):
        res = self.client().get(f"/categories/1/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(
            data["questions"][0],
            {
                "answer": "The Liver",
                "category": 1,
                "difficulty": 4,
                "id": 20,
                "question": "What is the heaviest organ in the human body?",
            },
        )
        total_questions = Question.query.count()
        self.assertEqual(data["total_questions"], total_questions)

    def test_get_questions_by_category_no_data_200(self):
        res = self.client().get(f"/categories/99999/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["questions"], [])
        total_questions = Question.query.count()
        self.assertEqual(data["total_questions"], total_questions)

    def test_retrieve_question_to_play_200(self):
        res = self.client().post(
            "/quizzes",
            json={
                "previous_questions": None,
                "quiz_category": {"id": 1},
            },
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(
            data["question"],
            {
                "answer": "The Liver",
                "category": 1,
                "difficulty": 4,
                "id": 20,
                "question": "What is the heaviest organ in the human body?",
            },
        )

    def test_retrieve_question_to_play_no_question_200(self):
        ids_question = [i for i in range(1, 24)]
        res = self.client().post(
            "/quizzes",
            json={
                "previous_questions": ids_question,
                "quiz_category": {"id": 1},
            },
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["question"], None)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
