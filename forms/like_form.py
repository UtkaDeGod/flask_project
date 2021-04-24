from flask_wtf import FlaskForm
from wtforms import SubmitField, HiddenField


class LikeForm(FlaskForm):
    anecdote_id = HiddenField()
    value = HiddenField()

    submit = SubmitField()
