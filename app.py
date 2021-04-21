from flask import Flask, redirect, render_template, request, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from data.db_session import *
from data.users import User
from forms.login_form import LoginForm
from forms.register_form import RegisterForm
from forms.add_anecdote_form import AddAnecdoteForm
from forms.add_category_form import AddCategoryForm
from forms.delete_category_form import DeleteCategoryForm
from forms.search_user_form import SearchUserForm
from forms.search_category_form import SearchCategoryForm
from forms.admin_user_edit_form import AdminUserEditForm
from forms.user_data_form import UserDataForm
from forms.like_form import LikeForm
from forms.dislike_form import DislikeForm
from data import anecdotes_resource
from flask_restful import Api
from data.anecdotes import Anecdote
from data.categories import Category
from datetime import datetime
from math import ceil

app = Flask(__name__)
app.config['SECRET_KEY'] = 'aleksey_lox))))_228'

api = Api(app)
login_manager = LoginManager()
login_manager.init_app(app)


def search_users(db_sess, line=''):
    users = db_sess.query(User).filter(User.name.like(f'%{line}%')).all()
    for i, user in enumerate(users):
        form = AdminUserEditForm()
        for key in ['id', 'is_admin', 'is_banned']:
            setattr(getattr(form, key), 'data', getattr(user, key))
        users[i] = (user.id, (user, form))
    return dict(users)


def search_categories(db_sess, line=''):
    categories = db_sess.query(Category).filter(Category.title.like(f'%{line}%')).all()
    for i, category in enumerate(categories):
        form = DeleteCategoryForm()
        form.id.data = category.id
        categories[i] = (category.id, (category, form))
    return dict(categories)


def search_anecdotes(db_sess, user_id):
    anecdotes = db_sess.query(Anecdote).filter(User.id == user_id).all()
    categories = db_sess.query(Category).all()
    for i, anecdote in enumerate(anecdotes):
        like_form = LikeForm()
        dislike_form = DislikeForm()
        edit_form = AddAnecdoteForm()
        edit_form.category.choices = [(category.id, category.title) for category in categories]
        edit_form.category.data = (anecdote.category.id, anecdote.category.title)
        edit_form.name.data = anecdote.name
        edit_form.text.data = anecdote.text
        anecdotes[i] = (anecdote.id, (anecdote, like_form, dislike_form, edit_form))
    return dict(anecdotes)


@login_manager.user_loader
def load_user(user_id):
    db_sess = create_session()
    user = db_sess.query(User).get(user_id)
    if user is None or not user.is_banned:
        return user
    return None


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


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


@app.route('/', methods=['GET', 'POST'])
def index():
    return redirect('/1')


@app.route('/<int:page>', methods=['GET', 'POST'])
def index_with_pagination(page):
    db_sess = create_session()
    ON_PAGE_COUNT = 20
    pages_count = ceil(len(db_sess.query(Anecdote).all()) / ON_PAGE_COUNT)
    if pages_count >= 7:
        pagination = [str(page)]
        if page != 1:
            pagination = (['1', '...'] if page != 2 else []) + [str(page - 1)] + pagination
        if page != pages_count:
            pagination = pagination + ([str(page + 1), '...'] if page != pages_count - 1 else []) + [str(pages_count)]
        pagination = ['Previous'] + pagination + ['Next']
    else:
        pagination = ['Previous'] + list(map(str, range(1, pages_count + 1))) + ['Next']
    anecdotes = db_sess.query(Anecdote).order_by(Anecdote.created_date.desc()). \
        offset((page - 1) * ON_PAGE_COUNT).limit(ON_PAGE_COUNT).all()
    return render_template('index.html', pagination=pagination, anecdotes=anecdotes, page=page, pages_count=pages_count)


@app.route('/add_anecdote', methods=['GET', 'POST'])
@login_required
def add_anecdote():
    db_sess = create_session()
    form = AddAnecdoteForm()
    form.category.choices = [(category.id, category.title) for category in db_sess.query(Category).all()]
    if form.validate_on_submit():
        anecdote = Anecdote(category_id=form.category.data, created_date=datetime.now(),
                            name=form.name.data, text=form.text.data, user_id=current_user.id)
        db_sess.add(anecdote)
        db_sess.commit()
        return redirect('/')
    return render_template('add_anecdote.html', form=form)


@app.route('/admin/edit_users', methods=['GET', 'POST'])
@login_required
def admin_edit_users():
    if not current_user.is_admin:
        abort(401)
    search_user_form = SearchUserForm()
    db_sess = create_session()
    users = search_users(db_sess)

    if search_user_form.validate_on_submit():
        users = search_users(db_sess, search_user_form.search_user.data)

    if request.method == 'POST':
        user_id = request.form.get('id', None)
        user_id = int(user_id) if isinstance(user_id, str) else user_id
        is_admin = request.form.get('is_admin', None) == 'y'
        is_banned = request.form.get('is_banned', None) == 'y'
        if isinstance(user_id, int):
            user = db_sess.query(User).get(user_id)
            user.is_admin, user.is_banned = is_admin, is_banned
            db_sess.commit()
            return redirect(f'/admin/edit_users#{user.id}')
    context = {'search_user_form': search_user_form, 'users': users}
    return render_template('admin_edit_users.html', **context)


@app.route('/admin/edit_categories', methods=['GET', 'POST'])
@login_required
def admin_edit_categories():
    if not current_user.is_admin:
        abort(401)
    search_category_form = SearchCategoryForm()
    delete_category_form = DeleteCategoryForm()
    add_category_form = AddCategoryForm()
    db_sess = create_session()
    categories = search_categories(db_sess)

    if search_category_form.validate_on_submit():
        categories = search_categories(db_sess, search_category_form.search_category.data)

    if request.method == 'POST' and request.form.get('action', None) == 'delete_category':
        category_id = request.form.get('id', None)
        category_id = int(category_id) if isinstance(category_id, str) else category_id
        if isinstance(category_id, int):
            category = db_sess.query(User).get(category_id)
            if all([anecdote.category != category for anecdote in db_sess.query(Anecdote).all()]):
                db_sess.delete(category)
                db_sess.commit()
            return redirect('/admin/edit_categories')

    if request.method == 'POST' and request.form.get('action', None) == 'add_category':
        title = request.form.get('title')
        if isinstance(title, str) and title != '':
            category = Category(title=title)
            db_sess.add(category)
            db_sess.commit()
            return redirect(f'/admin/edit_categories#{category.id}')
    context = {'search_category_form': search_category_form, 'delete_category_form': delete_category_form,
               'add_category_form': add_category_form, 'categories': categories}
    return render_template('admin_edit_categories.html', **context)


@app.route('/user_profile', methods=['GET', 'POST'])
@login_required
def user_profile():
    db_sess = create_session()
    anecdotes = search_anecdotes(db_sess, current_user.id)
    user_data_form = UserDataForm()
    return render_template('user_profile.html', user_data=user_data_form, anecdotes=anecdotes)


api.add_resource(anecdotes_resource.AnecdotesResource, "/anecdote")
api.add_resource(anecdotes_resource.AnecdotesListResource, "/anecdotes/page")
api.add_resource(anecdotes_resource.AnecdotesTopResource, "/anecdotes/top")

if __name__ == '__main__':
    global_init('db/anecdotes.db')
    app.run(port=5000, host='127.0.0.2')
