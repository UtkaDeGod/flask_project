from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField


class SearchUserForm(FlaskForm):
    search_user = StringField()
    submit = SubmitField('Поиск')