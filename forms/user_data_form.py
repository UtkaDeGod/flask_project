from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileAllowed, FileRequired


class UserDataForm(FlaskForm):
    name = StringField('Имя пользователя', validators=[DataRequired()])
    email = StringField('Мыло', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    avatar = FileField('image', validators=[FileRequired(), FileAllowed(['jpg', 'png'], 'Images only!')])
    submit = SubmitField('Сохранить')
