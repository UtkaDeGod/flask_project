from flask_wtf import FlaskForm
from flask import url_for
from markupsafe import Markup
from wtforms import SubmitField, HiddenField


class LikeForm(FlaskForm):
    anecdote_id = HiddenField()
    value = HiddenField()

    submit = SubmitField()