from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email
from flask_wtf.file import FileField, FileAllowed


class EditUserForm(FlaskForm):
    name = StringField('Имя пользователя', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    old_password = PasswordField('Старый пароль', validators=[DataRequired()])
    user_picture = FileField('Аватарка', validators=[FileAllowed(['jpg', 'png'], 'Images only!')])
    submit = SubmitField('Сохранить')
