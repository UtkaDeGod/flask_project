from flask import render_template, request, abort, Blueprint, make_response, session, redirect
from flask_login import login_required, current_user
from data.db_session import *
from forms.add_category_form import AddCategoryForm
from models.anecdotes import Anecdote
from models.categories import Category
from data.system_functions import search_categories, search_users, create_list_anecdotes_for_moderation, create_buttons_of_pagination
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
        user_id = int(request.form[[key for key in request.form if 'id' in key][0]])
        user = users[user_id]
        if user[1].validate_on_submit():
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

    if request.method == 'POST' and add_category_form.validate_on_submit():
        db_sess.add(Category(title=add_category_form.title.data))
        db_sess.commit()

    elif request.method == 'POST':
        category_id = int(request.form[[key for key in request.form if 'id' in key][0]])
        category = categories[category_id]
        if category[1].validate_on_submit():
            if all([anecdote.category != category[0] for anecdote in db_sess.query(Anecdote).all()]):
                db_sess.delete(category[0])
                db_sess.commit()

    categories = db_sess.query(Category).filter(Category.title.like(f'%{search_line}%'))
    pages_count, categories, pagination = create_buttons_of_pagination(page, categories)
    categories = search_categories(categories)
    context = {'categories': categories, 'add_category_form': add_category_form, 'search_line': search_line,
               'pagination': pagination, 'page_count': pages_count, 'page': page}
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
        anecdote_id = int(request.form[[key for key in request.form if 'anecdote_id' in key][0]])
        anecdote = anecdotes[anecdote_id]
        if anecdote[1].validate_on_submit():
            anecdote[0].is_published = int(anecdote[1].value.data)
        if anecdote[2].validate_on_submit():
            anecdote[0].is_published = int(anecdote[2].value.data)
        db_sess.commit()
    anecdotes = db_sess.query(Anecdote).filter(Anecdote.is_published == 0).order_by(Anecdote.created_date.desc())
    pages_count, anecdotes, pagination = create_buttons_of_pagination(page, anecdotes)
    anecdotes = create_list_anecdotes_for_moderation(anecdotes)

    return render_template('moderation.html', anecdotes=anecdotes, pages_count=pages_count, page=page,
                           pagination=pagination)
