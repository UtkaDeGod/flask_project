from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired


class AddAnecdoteForm(FlaskForm):
    name = StringField('Название анекдота', validators=[DataRequired()])
    text = TextAreaField('Текст анекдота', validators=[DataRequired()])
    category_black = BooleanField('Чёрный юмор', validators=[DataRequired()])
    category_tuolet = BooleanField('Туолетный юмор', validators=[DataRequired()])
    category_censure = BooleanField('Матерный юмор', validators=[DataRequired()])
    submit = SubmitField('Добавить')