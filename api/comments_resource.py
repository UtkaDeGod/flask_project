from flask_restful import Resource
from flask import jsonify, make_response, request
import datetime

from data import db_session
from models.comments import Comment
from models.anecdotes import Anecdote
from .auth import auth


class CommentsResource(Resource):
    @auth.login_required
    def post(self):
        if auth.current_user().is_banned:
            return make_response(jsonify({"error": "permission denied"}), 403)

        data = request.json
        if not data:
            return make_response(jsonify({"error": "parameters are required"}), 400)

        db_sess = db_session.create_session()

        try:
            anecdote = db_sess.query(Anecdote).get(data["anecdote_id"])
            if not anecdote:
                return make_response(jsonify({"error": "anecdote not found"}), 404)
            if anecdote.is_published != 1:
                return make_response(jsonify({"error": "anecdote haven't been published"}),
                                     400)

            comment = Comment(text=data["text"],
                              user_id=auth.current_user().id,
                              anecdote_id=anecdote.id,
                              created_date=datetime.datetime.now())
            db_sess.add(comment)
            db_sess.commit()
        except Exception:
            return make_response(jsonify({"error": "bad request"}), 400)

        return make_response(jsonify({"comment_id": comment.id}), 201)

    @auth.login_required
    def delete(self):
        db_sess = db_session.create_session()

        try:
            comment = db_sess.query(Comment).get(request.json["comment_id"])
        except Exception:
            return make_response(jsonify({"error": "bad request"}), 400)

        if not comment:
            return make_response(jsonify({"error": "comment not found"}), 404)

        if not auth.current_user().is_admin and auth.current_user().id != comment.user.id or\
                auth.current_user().is_banned:
            return make_response(jsonify({"error": "permission denied"}), 403)

        db_sess.delete(comment)
        db_sess.commit()
