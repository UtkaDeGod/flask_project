from flask import Flask, redirect, render_template
from flask_login import LoginManager, login_user
from data.db_session import *
from data.users import User
from forms.login_form import LoginForm
from forms.register_form import RegisterForm


app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    context = {'form': form, 'title': 'Авторизация'}
    if form.validate_on_submit():
        db_sess = create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect('/')
        return render_template('login.html', message='Неправильный логин или пароль', **context)
    return render_template('login.html', **context)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    context = {'form': form, 'title': 'Регистрация'}
    if form.validate_on_submit():
        db_sess = create_session()
        if form.repeat_password.data != form.hashed_password.data:
            return render_template('register.html', message='Пароли не совпадают', **context)
        if form.email.data in [user.email for user in db_sess.query(User).all()]:
            return render_template('register.html', message='Email уже занят', **context)
        if len(form.hashed_password.data) >= 8 and form.hashed_password.data.isalnum():
            return render_template('register.html', message='Пароль должен состоять из букв и цифр', **context)

        user = User(name=form.name.data, email=form.email.data)
        user.set_password(form.hashed_password.data)
        db_sess.add(user)
        db_sess.commit()
        redirect('/')
    return render_template('register.html', **context)
