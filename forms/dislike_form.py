from flask_wtf import FlaskForm
from flask import url_for
from markupsafe import Markup
from wtforms import SubmitField, HiddenField


class DislikeForm(FlaskForm):
    value = HiddenField(default=-1)

    submit = SubmitField(Markup(f'<img src="static/img/dislike.png" width="20" height="20">'))