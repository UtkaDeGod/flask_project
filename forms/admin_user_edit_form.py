from flask_wtf import FlaskForm
from wtforms import SubmitField, BooleanField, HiddenField


class AdminUserEditForm(FlaskForm):
    id = HiddenField()
    is_admin = BooleanField('админ')
    is_banned = BooleanField('забанен')
    submit = SubmitField('Подтвердить')
