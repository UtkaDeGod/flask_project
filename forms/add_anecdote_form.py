from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired


class AddAnecdoteForm(FlaskForm):
    name = StringField('Название анекдота', validators=[DataRequired()])
    text = TextAreaField('Текст анекдота', validators=[DataRequired()])
    category = SelectField('Категория анекдота', coerce=int)
    submit = SubmitField('Добавить')
