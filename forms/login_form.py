from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired('Заполните поле'), Email('Введите адрес электронной почты')])
    password = PasswordField('Пароль', validators=[DataRequired('Заполните поле')])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')
