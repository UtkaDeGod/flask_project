from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password_password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')