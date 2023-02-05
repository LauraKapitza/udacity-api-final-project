import os
import unittest
import json

from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def categories_fixtures(self):
        with self.app.app_context():
            self.db.engine.execute(f"insert into public.categories (id, type) "
                                   f"values({self.category_id},'{self.category_type}')")

    def questions_fixtures(self):
        with self.app.app_context():
            self.db.engine.execute(f"insert into public.questions (id, question, answer, difficulty, category) "
                                   f"values("
                                   f"'{self.question_id}',"
                                   f"'{self.question['question']}',"
                                   f"'{self.question['answer']}',"
                                   f"'{self.question['difficulty']}',"
                                   f"'{self.question['category']}'"
                                   f")")

    def clean_fixtures(self):
        with self.app.app_context():
            self.db.engine.execute('DELETE FROM public.categories')
            self.db.engine.execute('DELETE FROM public.questions')

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.category_id = 1
        self.category_type = "Science"
        self.question_id = 1
        self.question = {"id": self.question_id,
                         "question": "Test question",
                         "answer": "Test answer",
                         "difficulty": 5,
                         "category": self.category_id}

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
            # clean tables in case previous tests have miserably failed in blood and tears.
            self.clean_fixtures()

    def tearDown(self):
        self.clean_fixtures()

    def test_get_categories_200(self):
        self.categories_fixtures()

        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["categories"], {str(self.category_id): self.category_type})
        self.assertEqual(data["total_categories"], 1)

    def test_get_categories_no_data_200(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["categories"], {})
        self.assertEqual(data["total_categories"], 0)

    def test_get_questions_200(self):
        self.categories_fixtures()
        self.questions_fixtures()
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["questions"][0], self.question)
        self.assertEqual(data["total_questions"], 1)
        self.assertEqual(data["categories"], {str(self.category_id): self.category_type})
        self.assertEqual(data["current_category"], self.category_type)

    def test_get_questions_no_data_200(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["questions"], [])
        self.assertEqual(data["total_questions"], 0)
        self.assertEqual(data["categories"], {})
        self.assertEqual(data["current_category"], None)

    def test_delete_question_200(self):
        self.questions_fixtures()
        res = self.client().delete(f"/questions/{self.question_id}")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["deleted"], self.question_id)
        self.assertEqual(data["message"], "Question was successfully deleted.")

    def test_delete_question_404(self):
        res = self.client().delete("/questions/1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    def test_create_question_200(self):
        res = self.client().post("/questions", json=self.question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_create_question_400(self):
        res = self.client().post("/questions", json={})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "bad request")

    def test_search_questions_200(self):
        self.categories_fixtures()
        self.questions_fixtures()
        res = self.client().post("/questions/search", json={"searchTerm": "test"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["questions"][0], self.question)
        self.assertEqual(data["total_questions"], 1)
        self.assertEqual(data["current_category"], str(self.category_type))

    def test_search_questions_404(self):
        self.questions_fixtures()
        res = self.client().post("/questions/search", json={"searchTerm": "test"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

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
        self.questions_fixtures()
        res = self.client().get(f"/categories/{self.category_id}/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["questions"][0], self.question)
        self.assertEqual(data["total_questions"], 1)

    def test_get_questions_by_category_no_data_200(self):
        res = self.client().get(f"/categories/{self.category_id}/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["questions"], [])
        self.assertEqual(data["total_questions"], 0)

    def test_retrieve_question_to_play_200(self):
        self.questions_fixtures()
        res = self.client().post("/quizzes",
                                 json={"previous_questions": None, "quiz_category": {"id": self.category_id}})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["question"], self.question)

    def test_retrieve_question_to_play_no_question_200(self):
        self.questions_fixtures()
        res = self.client().post("/quizzes", json={"previous_questions": [self.question_id],
                                                   "quiz_category": {"id": self.category_id}})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["question"], None)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
