from flask_restful import Resource
from flask import jsonify, make_response, request
import datetime
import random

from data import db_session
from models.anecdotes import Anecdote
from models.categories import Category
from .auth import auth

DELTAS = {
    "day": datetime.timedelta(days=1),
    "week": datetime.timedelta(days=7),
    "month": datetime.timedelta(days=30),
    "year": datetime.timedelta(days=365)
}


class AnecdotesResource(Resource):
    def get(self):
        db_sess = db_session.create_session()

        ids = db_sess.query(Anecdote.id).filter(Anecdote.is_published == 1).all()
        if not ids:
            return make_response(jsonify({"error": "anecdote not found"}), 404)

        rand_id = random.choice(ids)
        anecdote = db_sess.query(Anecdote).get(rand_id)
        return make_response(jsonify({"anecdote": {"text": anecdote.text,
                                                   "id": rand_id,
                                                   "rating": anecdote.rating,
                                                   "name": anecdote.name,
                                                   "category": anecdote.category.title,
                                                   "created_date": anecdote.created_date,
                                                   "user_name": anecdote.user.name}}), 200)

    @auth.login_required
    def post(self):
        if auth.current_user().is_banned:
            return make_response(jsonify({"error": "permission denied"}), 403)
        data = request.json

        if not data:
            return make_response(jsonify({"error": "parameters are required"}), 400)

        keys = ["name", "text", "category"]
        if any(i not in keys for i in data.keys()):
            return make_response(jsonify({"error": "unexpected parameters"}), 400)

        db_sess = db_session.create_session()

        try:
            category = db_sess.query(Category) \
                .filter(Category.title == data["category"]).first()

            if not category:
                return make_response(jsonify({"error": "category not found"}), 404)

            anecdote = Anecdote(name=data["name"],
                                text=data["text"],
                                user_id=auth.current_user().id,
                                created_date=datetime.datetime.now(),
                                category_id=category.id)
            db_sess.add(anecdote)
            db_sess.commit()
        except Exception:
            return make_response(jsonify({"error": "bad request"}), 400)

        return make_response(jsonify({"id": anecdote.id}), 201)


class AnecdotesListResource(Resource):
    def get(self):
        db_sess = db_session.create_session()

        if not request.json.get("page", None):
            anecdotes = db_sess.query(Anecdote).limit(20).all()
            return make_response(jsonify({"anecdotes": anecdotes}), 200)

        try:
            page = request.json["page"]
            anecdotes = db_sess.query(Anecdote).offset((page - 1) * 20).limit(20).all()
            return make_response(jsonify({"anecdotes": anecdotes}), 200)
        except Exception:
            return make_response(jsonify({"error": "validation error"}), 400)

    @auth.login_required
    def post(self):
        if auth.current_user().is_banned:
            return make_response(jsonify({"error": "permission denied"}), 403)

        if not request.json:
            return make_response(jsonify({"error": "parameters are required"}), 400)
        elif not request.json.get("data", None):
            return make_response(jsonify({"error": "parameters are required"}), 400)

        keys = ["name", "text", "category"]
        json_data = request.json["data"]
        invalid = []
        valid = []

        db_sess = db_session.create_session()
        for data in json_data:
            if any(i not in keys for i in data.keys()):
                invalid.append({**data})
                continue

            try:
                category = db_sess.query(Category) \
                    .filter(Category.title == data["category"]).first()

                if not category:
                    invalid.append({**data})
                    continue

                anecdote = Anecdote(name=data["name"],
                                    text=data["text"],
                                    user_id=auth.current_user().id,
                                    created_date=datetime.datetime.now(),
                                    category_id=category.id)
                db_sess.add(anecdote)
                valid.append({"name": anecdote.name})
            except Exception:
                invalid.append({**data})

            if invalid:
                return make_response(jsonify({
                    "validation_error": {
                        "bad_params": invalid
                    }
                }), 400)

        db_sess.commit()
        return make_response(jsonify({"anecdotes": valid}), 201)


class AnecdotesTopResource(Resource):
    def get(self):
        db_sess = db_session.create_session()

        if not request.json:
            anecdotes = db_sess.query(Anecdote). \
                order_by(Anecdote.rating.desc()).filter(Anecdote.is_published == 1).limit(10).all()
            res = [{"name": i.name, "text": i.text, "id": i.id,
                    "rating": i.rating} for i in anecdotes]
            return make_response(jsonify({"anecdotes": res}),
                                 200)

        size = request.json.get("size", 10)
        if not isinstance(size, int):
            return make_response(jsonify({"error": "size is incorrect"}),
                                 400)

        period = request.json.get("period", None)
        if not period:
            anecdotes = db_sess.query(Anecdote). \
                order_by(Anecdote.rating.desc()).filter(Anecdote.is_published == 1).limit(size).all()
            res = [{"name": i.name, "text": i.text, "id": i.id,
                    "rating": i.rating} for i in anecdotes]
            return make_response(jsonify({"anecdotes": res}),
                                 200)

        try:
            delta = DELTAS[period]
        except Exception:
            return make_response(jsonify({"error": "wrong period parameter"}),
                                 400)

        anecdotes = db_sess.query(Anecdote). \
            filter(Anecdote.created_date >= datetime.datetime.now() - delta, Anecdote.is_published == 1) \
            .order_by(Anecdote.rating.desc()).limit(size).all()

        res = [{"name": i.name, "text": i.text, "id": i.id,
                "rating": i.rating} for i in anecdotes]

        return make_response(jsonify({"anecdotes": res}), 200)


class AnecdotesModerateResource(Resource):
    @auth.login_required
    def patch(self):
        if not auth.current_user().is_admin or\
                auth.current_user().is_banned:
            return make_response(jsonify({"error": "permission denied"}), 403)

        try:
            db_sess = db_session.create_session()
            anecdote = db_sess.query(Anecdote).get(request.json["anecdote_id"])

            if not anecdote:
                return make_response(jsonify({"error": "anecdote not found"}), 404)

            anecdote.is_published = request.json["is_published"]
            db_sess.commit()
        except Exception:
            return make_response(jsonify({"error": "bad request"}), 400)

        return make_response(jsonify({"id": anecdote.id}), 200)

    @auth.login_required
    def get(self):
        if not auth.current_user().is_admin or\
                auth.current_user().is_banned:
            return make_response(jsonify({"error": "permission denied"}), 403)

        db_sess = db_session.create_session()
        anecdotes = db_sess.query(Anecdote).filter(Anecdote.is_published == 0)

        resp = []
        for anecdote in anecdotes:
            resp.append({anecdote.id, anecdote.text})

        return make_response(jsonify({"anecdotes": resp}), 200)
