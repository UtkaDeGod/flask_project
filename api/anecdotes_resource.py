from flask_restful import Resource
from flask import jsonify, make_response, request
import datetime
import random

from data import db_session
from data.anecdotes import Anecdote
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

        ids = db_sess.query(Anecdote.id).all()
        if not ids:
            return make_response(jsonify({"error": "anecdote not found"}), 404)

        rand_id = random.choice(ids)
        anecdote = db_sess.query(Anecdote).get(rand_id)
        return make_response(jsonify({"anecdote": anecdote.to_dict(only=(
            "text", "rating", "name", "category", "created_date", "user.name"
        ))}), 200)


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
        except Exception as e:
            return make_response(jsonify({"error": "validation error"}), 400)


class AnecdotesTopResource(Resource):
    def get(self):
        db_sess = db_session.create_session()

        if not request.json:
            anecdotes = db_sess.query(Anecdote). \
                order_by(Anecdote.rating.desc()).limit(10).all()
            return make_response(jsonify({"anecdotes": anecdotes}),
                                 200)

        size = request.json.get("size", 10)
        if not isinstance(size, int):
            return make_response(jsonify({"error": "size is incorrect"}),
                                 400)

        period = request.json.get("period", None)
        if not period:
            anecdotes = db_sess.query(Anecdote). \
                order_by(Anecdote.rating.desc()).limit(size).all()
            return make_response(jsonify({"anecdotes": anecdotes}),
                                 200)

        try:
            delta = DELTAS[period]
        except Exception:
            return make_response(jsonify({"error": "wrong period parameter"}),
                                 400)

        anecdotes = db_sess.query(Anecdote).\
            filter(Anecdote.created_date >= datetime.datetime.now() - delta)\
            .order_by(Anecdote.rating.desc()).limit(size).all()

        return make_response(jsonify({"anecdotes": anecdotes}), 200)
