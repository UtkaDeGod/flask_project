from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField
from wtforms.validators import DataRequired


class AddCategoryForm(FlaskForm):
    title = StringField('Название категории', validators=[DataRequired()])
    action = HiddenField(default='add_category')
    submit = SubmitField('Добавить')