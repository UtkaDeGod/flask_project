from flask import render_template, request, abort, Blueprint, make_response, redirect
from flask_login import login_required, current_user
from data.db_session import create_session
from forms.add_category_form import AddCategoryForm
from models.anecdotes import Anecdote
from models.categories import Category
from data.system_functions import search_categories, search_users, create_list_anecdotes_for_moderation
from data.system_functions import create_buttons_of_pagination
from models.users import User

blueprint = Blueprint(
    'adamin',
    __name__,
    template_folder='templates'
)


@blueprint.route('/admin/edit/users', methods=['GET', 'POST'])
@login_required
def admin_edit_users():
    if not current_user.is_admin:
        abort(401)
    page = int(request.args.get('page', '1'))
    search_line = request.args.get('search_line', '')
    db_sess = create_session()

    users = db_sess.query(User).filter(User.name.like(f'%{search_line}%'))
    pages_count, users, pagination = create_buttons_of_pagination(page, users)

    users = search_users(users)

    if request.method == 'POST':
        user_id = request.form.get('id', None)
        user = users[int(user_id)] if user_id is not None else None
        if user is not None and user[1].validate_on_submit():
            user[0].is_admin, user[0].is_banned = user[1].is_admin.data, user[1].is_banned.data
            db_sess.commit()
            return redirect(f'#{user[0].id}')
    context = {'users': users, 'search_line': search_line, 'pages_count': pages_count, 'pagination': pagination,
               'page': page}
    return render_template('admin_edit_users.html', **context)


@blueprint.route('/admin/edit/categories', methods=['GET', 'POST'])
@login_required
def admin_edit_categories():
    if not current_user.is_admin:
        abort(401)
    search_line = request.args.get('search_line', '')
    page = int(request.args.get('page', '1'))
    add_category_form = AddCategoryForm(prefix='add_category_form')
    db_sess = create_session()

    categories = db_sess.query(Category).filter(Category.title.like(f'%{search_line}%'))
    pages_count, categories, pagination = create_buttons_of_pagination(page, categories)
    categories = search_categories(categories)
    message = ''

    if request.method == 'POST' and add_category_form.validate_on_submit():
        title = add_category_form.title.data
        if title in [category.title for category in db_sess.query(Category).all()]:
            message = 'Категория с таким именем уже есть'
        else:
            db_sess.add(Category(title=add_category_form.title.data))
            db_sess.commit()

    elif request.method == 'POST':
        category_id = request.form.get('id', None)
        category = categories[int(category_id)] if category_id is not None else None
        if category is not None and category[1].validate_on_submit():
            if any([anecdote.category == category[0] for anecdote in db_sess.query(Anecdote).all()]):
                message = 'К этой категории привязаны анекдоты'
            else:
                db_sess.delete(category[0])
                db_sess.commit()

    categories = db_sess.query(Category).filter(Category.title.like(f'%{search_line}%'))
    pages_count, categories, pagination = create_buttons_of_pagination(page, categories)
    categories = search_categories(categories)
    context = {'edit_categories': categories, 'add_category_form': add_category_form, 'search_line': search_line,
               'pagination': pagination, 'page_count': pages_count, 'page': page, 'message': message}
    return make_response(render_template('admin_edit_categories.html', **context))


@blueprint.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_moderation():
    if not current_user.is_admin:
        abort(401)
    db_sess = create_session()
    page = int(request.args.get('page', '1'))

    anecdotes = db_sess.query(Anecdote).filter(Anecdote.is_published == 0).order_by(Anecdote.created_date.desc())
    pages_count, anecdotes, pagination = create_buttons_of_pagination(page, anecdotes)
    anecdotes = create_list_anecdotes_for_moderation(anecdotes)

    if request.method == 'POST':
        anecdote_id = request.form.get('anecdote_id', None)
        anecdote = anecdotes[int(anecdote_id)] if anecdote_id is not None else None
        value = int(request.form.get('value'))
        anecdote[0].is_published = value
        db_sess.commit()
    anecdotes = db_sess.query(Anecdote).filter(Anecdote.is_published == 0).order_by(Anecdote.created_date.desc())
    pages_count, anecdotes, pagination = create_buttons_of_pagination(page, anecdotes)
    anecdotes = create_list_anecdotes_for_moderation(anecdotes)

    return render_template('moderation.html', anecdotes=anecdotes, pages_count=pages_count, page=page,
                           pagination=pagination)
