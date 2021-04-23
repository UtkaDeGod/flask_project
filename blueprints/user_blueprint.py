from flask import redirect, render_template, request, Blueprint
from flask_login import login_user, logout_user, login_required, current_user
from data.db_session import *
from models.anecdotes import Anecdote
from models.users import User
from forms.login_form import LoginForm
from forms.register_form import RegisterForm
from forms.edit_user_form import EditUserForm
from models.likes import Like
from PIL import Image
from data.system_functions import search_anecdotes, create_buttons_of_pagination
from math import ceil

blueprint = Blueprint(
    'user',
    __name__,
    template_folder='templates'
)


@blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    context = {'form': form, 'title': 'Авторизация'}
    if form.validate_on_submit():
        db_sess = create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data) and not user.is_banned:
            login_user(user, remember=form.remember_me.data)
            return redirect('/')
        elif user and user.is_banned:
            return render_template('login.html', message='Вы заблокированны', **context)
        elif user and not user.check_password(form.password.data):
            return render_template('login.html', message='Неправильный логин или пароль', **context)
    return render_template('login.html', **context)


@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    context = {'form': form, 'title': 'Регистрация'}
    if form.validate_on_submit():
        db_sess = create_session()
        if form.repeat_password.data != form.hashed_password.data:
            return render_template('register.html', message='Пароли не совпадают', **context)
        if form.email.data in [user.email for user in db_sess.query(User).all()]:
            return render_template('register.html', message='Email уже занят', **context)
        if len(form.hashed_password.data) < 8:
            return render_template('register.html', message='Длина пароля должна быть не менее 8 символов', **context)
        if not form.hashed_password.data.isalnum():
            return render_template('register.html', message='Пароль должен состоять из букв и цифр', **context)
        user = User(name=form.name.data, email=form.email.data)
        user.set_password(form.hashed_password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', **context)


@blueprint.route('/user/anecdotes', methods=['GET', 'POST'])
@login_required
def user_anecdotes():
    page = int(request.args.get('page', '1'))
    search_line = request.args.get('search_line', '')
    db_sess = create_session()

    anecdotes = db_sess.query(Anecdote).filter(Anecdote.user == current_user, Anecdote.name.like(f'%{search_line}%')). \
        order_by(Anecdote.created_date.desc())
    pages_count, anecdotes, pagination = create_buttons_of_pagination(page, anecdotes)

    anecdotes = search_anecdotes(anecdotes)

    if request.method == 'POST':
        anecdote_id = int(request.form[[key for key in request.form if 'anecdote_id' in key][0]])
        anecdote = anecdotes[anecdote_id]

        if anecdote[1].validate_on_submit() or anecdote[2].validate_on_submit():
            value = anecdote[1].value.data if anecdote[1].validate_on_submit() else anecdote[2].value.data
            like = db_sess.query(Like).filter(Like.user_id == current_user.id, Like.anecdote_id == anecdote_id).first()
            if like is None:
                like = Like(user_id=current_user.id, anecdote_id=anecdote_id, value=0)
            if like is not None and like.value == 0:
                anecdote[0].rating += int(value)
            elif like is not None and like.value != int(value):
                anecdote[0].rating += int(value) * 2
            elif like is not None and like.value == int(value):
                anecdote[0].rating -= int(value)
            like.value = value if like.value != int(value) else 0
            db_sess.add(like)
            db_sess.commit()
        if anecdote[3].validate_on_submit():
            for key in ['name', 'text', 'category_id']:
                setattr(anecdote[0], key, getattr(anecdote[3], key).data)
            anecdote[0].is_published = 0
            db_sess.commit()
        return redirect(f'#{anecdote_id}')
    return render_template('user_anecdotes.html', anecdotes=anecdotes, pagination=pagination,
                           page=page, pages_count=pages_count, search_line=search_line)


@blueprint.route('/user/profile', methods=['GET', 'POST'])
@login_required
def user_profile():
    form = EditUserForm()
    db_sess = create_session()
    if request.method == 'POST' and form.validate_on_submit():
        if current_user.check_password(form.old_password.data):
            user = db_sess.query(User).get(current_user.id)
            if form.user_picture.data is not None:
                im = Image.open(form.user_picture.data)
                width, height = im.size
                if width > height:
                    corr = (width - height) // 2
                    im = im.crop((corr, 0, corr + height, height))
                elif width < height:
                    corr = (height - width) // 2
                    im = im.crop((0, corr, width, corr + width))
                im.save(f'./static/img/avatars/{user.id}.png')
                user.picture_path = f'./img/avatars/{user.id}.png'
            user.name = form.name.data
            user.email = form.email.data
            db_sess.commit()
        else:
            return render_template('user_profile.html', form=form,
                                   message='Введённый пароль не совпадает со старым паролем')
    elif request.method == 'POST' and not form.validate_on_submit():
        return render_template('user_profile.html', form=form,
                               message='Введите правильный email')
    return render_template('user_profile.html', form=form)


@blueprint.route('/user/likes', methods=['GET', 'POST'])
@login_required
def likes_anecdotes():
    page = int(request.args.get('page', '1'))
    search_line = request.args.get('search_line', '')
    db_sess = create_session()

    likes = db_sess.query(Like).join(Anecdote).filter(Like.user == current_user, Like.value == 1,
                                                      Anecdote.name.like(f'%{search_line}%')). \
        order_by(Anecdote.created_date.desc())
    print(likes.all())
    pages_count, anecdotes, pagination = create_buttons_of_pagination(page, likes)
    anecdotes = [like.anecdote for like in likes]
    anecdotes = search_anecdotes(anecdotes)

    if request.method == 'POST':
        anecdote_id = int(request.form[[key for key in request.form if 'anecdote_id' in key][0]])
        anecdote = anecdotes[anecdote_id]

        if anecdote[1].validate_on_submit() or anecdote[2].validate_on_submit():
            value = anecdote[1].value.data if anecdote[1].validate_on_submit() else anecdote[2].value.data
            like = db_sess.query(Like).filter(Like.user_id == current_user.id, Like.anecdote_id == anecdote_id).first()
            if like is None:
                like = Like(user_id=current_user.id, anecdote_id=anecdote_id, value=0)
            if like is not None and like.value == 0:
                anecdote[0].rating += int(value)
            elif like is not None and like.value != int(value):
                anecdote[0].rating += int(value) * 2
            elif like is not None and like.value == int(value):
                anecdote[0].rating -= int(value)
            like.value = value if like.value != int(value) else 0
            db_sess.add(like)
            db_sess.commit()
        return redirect(f'#{anecdote_id}')
    return render_template('user_like_anecdotes.html', anecdotes=anecdotes, pagination=pagination,
                           page=page, pages_count=pages_count, search_line=search_line)
