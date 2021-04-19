from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired


class AddAnecdoteForm(FlaskForm):
    name = StringField('Название анекдота', validators=[DataRequired()])
    text = TextAreaField('Текст анекдота', validators=[DataRequired()])
    add_category = StringField('Название анекдота', validators=[DataRequired()])
    submit = SubmitField('Добавить')