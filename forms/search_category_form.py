from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField


class SearchCategoryForm(FlaskForm):
    search_category = StringField()
    submit = SubmitField('Поиск')