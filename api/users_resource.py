from flask_restful import Resource
from flask import jsonify, make_response, request

from data import db_session
from models.users import User
from .auth import auth


class UsersListResource(Resource):
    @auth.login_required
    def post(self):
        if not auth.current_user().is_admin or auth.current_user().is_banned:
            return make_response(jsonify({"error": "permission denied"}), 403)

        if not request.json:
            return make_response(jsonify({"error": "parameters are required"}), 400)
        elif not request.json.get("data", None):
            return make_response(jsonify({"error": "parameters are required"}), 400)

        keys = ["name", "email", "password"]
        json_data = request.json["data"]
        invalid = []
        valid = []
        db_sess = db_session.create_session()

        for data in json_data:
            if any(i not in keys for i in data.keys()):
                invalid.append({**data})
                continue

            try:
                if db_sess.query(User).filter(User.email == data["email"]).first():
                    invalid.append({**data})
                    continue

                user = User(name=data["name"],
                            email=data["email"])
                user.set_password(data["password"])
                db_sess.add(user)
                valid.append({"email": user.email})
            except Exception:
                invalid.append({**data})

        if invalid:
            return make_response(jsonify({
                "validation_error": {
                    "bad_params": invalid
                }
            }), 400)

        db_sess.commit()
        return make_response(jsonify({"users": valid}), 201)


class UsersResource(Resource):
    @auth.login_required
    def get(self, user_id):
        if not auth.current_user().is_admin and auth.current_user().id != user_id or \
                auth.current_user().is_banned:
            return make_response(jsonify({"error": "permission denied"}), 403)

        db_sess = db_session.create_session()
        user = db_sess.query(User).get(user_id)

        if not user:
            return make_response(jsonify({"error": "user not found"}), 404)

        return make_response(jsonify({"user_info": user.to_dict(
            only=("id", "name", "email")),
            "comments_writen": len(user.comments),
            "anecdotes_created": len(user.anecdotes)}),
            200)

    @auth.login_required
    def delete(self, user_id):
        if not auth.current_user().is_admin or\
                auth.current_user().is_banned:
            return make_response(jsonify({"error": "permission denied"}), 403)

        db_sess = db_session.create_session()
        user = db_sess.query(User).get(user_id)

        if not user:
            return make_response(jsonify({"error": "user not found"}), 404)

        user.is_banned = True
        db_sess.commit()

        return make_response(jsonify({"banned_id": user.id}), 200)

    @auth.login_required
    def patch(self, user_id):
        if not auth.current_user().is_admin and auth.current_user().id != user_id or\
                auth.current_user().is_banned:
            return make_response(jsonify({"error": "permission denied"}), 403)

        db_sess = db_session.create_session()
        user = db_sess.query(User).get(user_id)

        if not user:
            return make_response(jsonify({"error": "user not found"}), 404)

        if not request.json:
            return make_response(jsonify({"user": user.
                                         to_dict(only=("id", "name", "email"))}),
                                 200)

        keys = ["name"]
        if any(i not in keys for i in request.json.keys()):
            return make_response(jsonify({"error": "unexpected parameters"}), 400)

        try:
            for i in request.json.keys():
                setattr(user, i, request.json[i])
        except Exception:
            return make_response(jsonify({"error": "validation error"}), 400)

        db_sess.commit()

        return make_response(jsonify({"user": user.
                                     to_dict(only=("id", "name", "email"))}),
                             200)


class UsersRegistrationResource(Resource):
    def post(self):
        if not request.json:
            return make_response(jsonify({"error": "parameters are required"}), 400)

        keys = ["name", "email", "password"]
        if any(i not in keys for i in request.json.keys()):
            return make_response(jsonify({"error": "unexpected parameters"}), 400)

        db_sess = db_session.create_session()
        data = request.json

        if db_sess.query(User).filter(User.email == data["email"]).first():
            return make_response(jsonify({"error": "email have been used"}), 400)

        try:
            user = User(name=data["name"],
                        email=data["email"])
            user.set_password(data["password"])
            db_sess.add(user)
        except Exception:
            return make_response(jsonify({"error": "bad request"}), 400)

        db_sess.commit()
        return make_response(jsonify({"email": user.email}), 201)
