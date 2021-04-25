from flask_restful import Resource
from flask import jsonify, make_response, request

from data import db_session
from models.categories import Category
from .auth import auth


class CategoriesResource(Resource):
    @auth.login_required
    def post(self):
        if not auth.current_user().is_admin or\
                auth.current_user().is_banned:
            return make_response(jsonify({"error": "permission denied"}), 403)

        try:
            db_sess = db_session.create_session()
            category = Category(title=request.json["title"])
            db_sess.add(category)
            db_sess.commit()
        except Exception:
            return make_response(jsonify({"error": "bad request"}), 400)

        return make_response(jsonify({"title": category.title}), 201)
