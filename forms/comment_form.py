from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea


class CommentForm(FlaskForm):
    text = StringField(validators=[DataRequired()], widget=TextArea())
    submit = SubmitField('Оставить комментарий')
