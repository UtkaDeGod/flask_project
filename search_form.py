from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired


class SearchForm(FlaskForm):
    search_user = StringField('Название анекдота', validators=[DataRequired()])
    search_content = StringField('Название анекдота', validators=[DataRequired()])
    search_category = StringField('Название анекдота', validators=[DataRequired()])
    submit = SubmitField('Добавить')