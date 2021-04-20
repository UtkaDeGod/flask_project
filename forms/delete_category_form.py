from flask_wtf import FlaskForm
from wtforms import SubmitField, HiddenField


class DeleteCategoryForm(FlaskForm):
    id = HiddenField()
    action = HiddenField(default='delete_category')
    submit = SubmitField('Удалить')