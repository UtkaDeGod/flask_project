from flask_restful import Resource
from flask import jsonify, make_response, request
import datetime
import random

from . import db_session
from .anecdotes import Anecdote

DELTAS = {
    "day": datetime.timedelta(days=1),
    "week": datetime.timedelta(days=7),
    "month": datetime.timedelta(days=30),
    "year": datetime.timedelta(days=365)
}


class AnecdotesResource(Resource):
    def get(self):
        db_sess = db_session.create_session()
        rand_id = random.choice(db_sess.query(Anecdote.id))
        if not rand_id:
            return make_response(jsonify({"error": "anecdote not found"}), 404)
        anecdote = db_sess.query(Anecdote).get(rand_id)
        return make_response(jsonify({"anecdote_text": anecdote.text,
                                      "rating": anecdote.rating,
                                      "anecdote_name": anecdote.name,
                                      "category": anecdote.category.title,
                                      "date": str(anecdote.created_date),
                                      "creator_name": anecdote.creator.name}), 200)


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
            return make_response(jsonify({"error": "validation error"}, 400))


class AnecdotesTopResource(Resource):
    def get(self):
        db_sess = db_session.create_session()

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
