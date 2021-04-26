from flask_restful import Resource
from flask import jsonify, make_response, request

from data import db_session
from models.anecdotes import Anecdote
from models.likes import Like
from .auth import auth


class LikesResource(Resource):
    @auth.login_required
    def get(self):
        if auth.current_user().is_banned:
            return make_response(jsonify({"error": "permission denied"}), 403)

        db_sess = db_session.create_session()
        likes = db_sess.query(Like).filter(Like.user_id == auth.current_user().id).all()

        resp = []
        for like in likes:
            resp.append({"id": like.anecdote_id, "val": like.value})

        return make_response(jsonify({"liked_anecdotes": resp}), 200)

    @auth.login_required
    def post(self):
        if auth.current_user().is_banned:
            return make_response(jsonify({"error": "permission denied"}), 403)

        db_sess = db_session.create_session()
        data = request.json

        try:
            anecdote = db_sess.query(Anecdote).get(data["anecdote_id"])
            if not anecdote:
                return make_response(jsonify({"error": "anecdote not found"}), 404)
            if anecdote.is_published != 1:
                return make_response(jsonify({"error": "anecdote haven't been published"}),
                                     400)

            like = db_sess.query(Like).filter(Like.anecdote_id == anecdote.id,
                                              Like.user_id == auth.current_user().id).first()

            if like:
                anecdote.rating += like.value * -1
                like.value = data["value"]
                anecdote.rating += data["value"]
            else:
                like = Like(anecdote_id=anecdote.id,
                            user_id=auth.current_user().id,
                            value=data["value"])
                db_sess.add(like)
                anecdote.rating += data["value"]
        except Exception:
            return make_response(jsonify({"error": "bad request"}), 400)

        db_sess.commit()
        return make_response(jsonify({"like_id": like.id}), 201)
