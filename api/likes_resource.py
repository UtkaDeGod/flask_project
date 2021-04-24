from flask_restful import Resource
from flask import jsonify, make_response, request

from data import db_session
from models.anecdotes import Anecdote
from models.likes import Like
from .auth import auth


class LikesResource(Resource):
    @auth.login_required
    def get(self):
        db_sess = db_session.create_session()
        likes = db_sess.query(Like).filter(Like.user_id == auth.current_user().id).all()

        resp = []
        for like in likes:
            resp.append({"id": like.anecdote_id, "val": like.value})

        return make_response(jsonify({"liked_anecdotes": resp}), 200)

    @auth.login_required
    def post(self):
        db_sess = db_session.create_session()
        data = request.json

        try:
            if not db_sess.query(Anecdote).get(data["anecdote_id"]).first():
                return make_response(jsonify({"error": "anecdote not found"}), 404)

            like = db_sess.query(Like).filter(Like.anecdote_id == data["anecdote_id"],
                                              Like.user_id == auth.current_user().id).first()

            if like:
                like.value = data["value"]
            else:
                like = Like(anecdote_id=data["anecdote_id"],
                            user_id=auth.current_user().id,
                            value=data["value"])
                db_sess.add(like)
        except Exception:
            return make_response(jsonify({"error": "bad request"}), 400)

        db_sess.commit()
        return make_response(jsonify({"like_id": like.id}), 201)
