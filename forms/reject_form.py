from flask_wtf import FlaskForm
from wtforms import SubmitField, HiddenField


class RejectForm(FlaskForm):
    anecdote_id = HiddenField()
    value = HiddenField(default=2)
    submit = SubmitField('Отказать')
