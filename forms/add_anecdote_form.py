from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class AddAnecdoteForm(FlaskForm):
    text = StringField('Текст анекдота', validators=[DataRequired()])
    category = StringField('Категория анекдота', validators=[DataRequired()])
    submit = SubmitField('Добавить')