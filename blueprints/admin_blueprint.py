from flask import render_template, request, abort, Blueprint
from flask_login import login_required, current_user
from data.db_session import *
from forms.add_category_form import AddCategoryForm
from forms.search_user_form import SearchUserForm
from forms.search_category_form import SearchCategoryForm
from models.anecdotes import Anecdote
from models.categories import Category
from data.system_functions import search_categories, search_users, create_list_anecdotes_for_moderation


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
    search_user_form = SearchUserForm()
    db_sess = create_session()
    users = search_users(db_sess)

    if search_user_form.validate_on_submit():
        users = search_users(db_sess, search_user_form.search_user.data)

    elif request.method == 'POST':
        user_id = int(request.form[[key for key in request.form if 'id' in key][0]])
        user = users[user_id]
        if user[1].validate_on_submit():
            user[0].is_admin, user[0].is_banned = user[1].is_admin.data, user[1].is_banned.data
            db_sess.commit()
    context = {'search_user_form': search_user_form, 'users': users}
    return render_template('admin_edit_users.html', **context)


@blueprint.route('/admin/edit/categories', methods=['GET', 'POST'])
@login_required
def admin_edit_categories():
    if not current_user.is_admin:
        abort(401)
    search_category_form = SearchCategoryForm(prefix='search_category_form')
    add_category_form = AddCategoryForm(prefix='add_category_form')
    db_sess = create_session()
    categories = search_categories(db_sess)

    if search_category_form.validate_on_submit():
        categories = search_categories(db_sess, search_category_form.search_category.data)

    elif request.method == 'POST' and add_category_form.validate_on_submit():
        db_sess.add(Category(title=add_category_form.title.data))
        db_sess.commit()
        categories = search_categories(db_sess)

    elif request.method == 'POST':
        category_id = int(request.form[[key for key in request.form if 'id' in key][0]])
        category = categories[category_id]
        if category[1].validate_on_submit():
            if all([anecdote.category != category[0] for anecdote in db_sess.query(Anecdote).all()]):
                db_sess.delete(category[0])
                db_sess.commit()
                categories = search_categories(db_sess)
    context = {'search_category_form': search_category_form, 'categories': categories,
               'add_category_form': add_category_form}
    return render_template('admin_edit_categories.html', **context)


@blueprint.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_moderation():
    if not current_user.is_admin:
        abort(401)
    db_sess = create_session()
    anecdotes = create_list_anecdotes_for_moderation(db_sess)
    if request.method == 'POST':
        anecdote_id = int(request.form[[key for key in request.form if 'anecdote_id' in key][0]])
        anecdote = anecdotes[anecdote_id]
        if anecdote[1].validate_on_submit():
            anecdote[0].is_published = int(anecdote[1].value.data)
        if anecdote[2].validate_on_submit():
            anecdote[0].is_published = int(anecdote[2].value.data)
        db_sess.commit()
    anecdotes = create_list_anecdotes_for_moderation(db_sess)
    return render_template('moderation.html', anecdotes=anecdotes)
