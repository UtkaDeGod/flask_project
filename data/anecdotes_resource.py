from flask_restful import Resource
from flask import jsonify, make_response, request
import datetime
import json
import random

from . import db_session
from .anecdotes import Anecdote


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
