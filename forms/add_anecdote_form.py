from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class AddAnecdoteForm(FlaskForm):
    name = StringField('Название анекдота', validators=[DataRequired()])
    text = StringField('Текст анекдота', validators=[DataRequired()])
    category = StringField('Категория анекдота', validators=[DataRequired()])
    submit = SubmitField('Добавить')