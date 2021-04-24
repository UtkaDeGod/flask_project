from flask_wtf import FlaskForm
from wtforms import SubmitField, HiddenField


class AcceptForm(FlaskForm):
    anecdote_id = HiddenField()
    value = HiddenField(default=1)
    submit = SubmitField('Принять')
