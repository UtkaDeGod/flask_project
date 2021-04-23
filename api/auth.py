from flask_httpauth import HTTPBasicAuth
from models.users import User
from data import db_session


auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(email, password):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.email == email).first()
    if user and user.check_password(password):
        return user
