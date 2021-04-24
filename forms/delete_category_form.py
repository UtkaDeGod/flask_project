from flask_wtf import FlaskForm
from wtforms import SubmitField, HiddenField


class DeleteCategoryForm(FlaskForm):
    id = HiddenField()
    submit = SubmitField('Удалить')
