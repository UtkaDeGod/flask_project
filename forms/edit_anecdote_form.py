from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, TextAreaField, SelectField, SubmitField
from wtforms.widgets import TextArea
from wtforms.validators import DataRequired


class EditAnecdoteForm(FlaskForm):
    anecdote_id = HiddenField(validators=[DataRequired()])
    name = StringField('Название анекдота', validators=[DataRequired()])
    text = StringField('Текст анекдота', validators=[DataRequired()], widget=TextArea())
    category_id = SelectField('Категория анекдота', coerce=int)
    submit = SubmitField('Добавить')
