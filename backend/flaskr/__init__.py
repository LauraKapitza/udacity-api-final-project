import os
from operator import and_

from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request_queries, questions):
    page = request_queries.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    formatted_questions = [question.format() for question in questions]
    sliced_questions = formatted_questions[start:end]

    return sliced_questions


def create_category_dictionary(categories):
    formatted_categories = [category.format() for category in categories]
    dict_categories = dict((category['id'], category['type']) for category in formatted_categories)
    return dict_categories


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response

    @app.route("/categories")
    def get_categories():
        categories = Category.query.order_by(Category.id).all()

        dict_categories = {}
        if categories:
            dict_categories = create_category_dictionary(categories)

        return jsonify(
            {
                "success": True,
                "categories": dict_categories,
                "total_categories": len(categories),
            }
        )

    @app.route("/questions")
    def get_questions():
        categories = Category.query.order_by(Category.id).all()
        questions = Question.query.order_by(Question.id).all()

        dict_categories = create_category_dictionary(categories)
        paginated_questions = paginate_questions(request.args, questions)
        current_category = dict_categories[1] if dict_categories else None

        return jsonify(
            {
                "success": True,
                "questions": paginated_questions,
                "total_questions": len(questions),
                "categories": dict_categories,
                "current_category": current_category
            }
        )

    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        question = Question.query.filter_by(id=question_id).first_or_404()
        try:
            question.delete()
        except:
            abort(422)

        return jsonify(
            {
                "success": True,
                "deleted": question_id,
                "message": "Question was successfully deleted."
            }
        )

    @app.route("/questions", methods=["POST"])
    def create_question():
        body = request.get_json()

        question = body.get("question", None)
        answer = body.get("answer", None)
        difficulty = body.get("difficulty", None)
        category = body.get("category", None)

        if not question or not answer or not difficulty or not category:
            abort(400)

        try:
            new_question = Question(question, answer, difficulty, category)
            new_question.insert()

            return jsonify(
                {
                    "success": True
                }
            )

        except:
            abort(422)

    @app.route("/questions/search", methods=["POST"])
    def search_questions():
        body = request.get_json()

        search = body.get("searchTerm", None)

        if search is None:
            abort(400)

        questions = Question.query.filter(Question.question.ilike('%{}%'.format(search))).order_by(Question.id).all()
        paginated_questions = paginate_questions(request.args, questions)
        current_category = paginated_questions[0]['category'] if paginated_questions else None;

        return jsonify(
            {
                "success": True,
                "questions": paginated_questions,
                "total_questions": len(questions),
                "current_category": current_category
            }
        )

    @app.route("/categories/<int:category_id>/questions")
    def get_questions_by_category(category_id):
        # converts category id into string since the schema expects a string
        questions = Question.query.filter(Question.category == str(category_id)).order_by(Question.id)
        paginated_questions = paginate_questions(request.args, questions)

        return jsonify(
            {
                "success": True,
                "questions": paginated_questions,
                "total_questions": len(Question.query.all()),
            }
        )

    @app.route("/quizzes", methods=["POST"])
    def retrieve_question_to_play():
        body = request.get_json()
        previous_questions = body.get("previous_questions", None)
        quiz_category = body.get("quiz_category", None)

        filters = []

        if quiz_category and "id" in quiz_category and quiz_category["id"] != 0:
            # converts category id into string since the schema expects a string
            filters.append(Question.category == str(quiz_category["id"]))

        if previous_questions:
            filters.append(~Question.id.in_(previous_questions))

        if filters:
            question = Question.query.filter(*filters).first_or_404()
        else:
            question = Question.query.first()

        return jsonify(
            {
                "success": True,
                "question": question.format()
            }
        )

    @app.errorhandler(400)
    def bad_request(error):
        return (
            jsonify({"success": False, "error": 400, "message": "bad request"}),
            400
        )

    @app.errorhandler(401)
    def bad_request(error):
        return (
            jsonify({"success": False, "error": 401, "message": "not authorized"}),
            401
        )

    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "resource not found"}),
            404,
        )

    @app.errorhandler(405)
    def not_allowed(error):
        return (
            jsonify({"success": False, "error": 405, "message": "method not allowed"}),
            405,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "unprocessable"}),
            422,
        )

    @app.errorhandler(500)
    def internal_server_error(error):
        return (
            jsonify({"success": False, "error": 500, "message": "internal server error"}),
            500,
        )

    return app
