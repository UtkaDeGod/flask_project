from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class AddAnecdoteForm(FlaskForm):
    title = StringField('Текст анекдота', validators=[DataRequired()])
    submit = SubmitField('Добавить')