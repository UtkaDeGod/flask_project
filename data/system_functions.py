from math import ceil
from flask import request
from flask_login import current_user
from forms.delete_category_form import DeleteCategoryForm
from forms.admin_user_edit_form import AdminUserEditForm
from forms.like_form import LikeForm
from forms.accept_form import AcceptForm
from forms.reject_form import RejectForm
from models.likes import Like


def search_users(users):
    res = {}
    for i, user in enumerate(users):
        form = AdminUserEditForm()
        form.id.data = user.id
        res[user.id] = (user, form)
    return res


def search_categories(categories):
    res = {}
    for i, category in enumerate(categories):
        form = DeleteCategoryForm()
        form.id.data = category.id
        res[category.id] = (category, form)
    return res


def search_anecdotes(anecdotes):
    res = {}
    for i, anecdote in enumerate(anecdotes):
        like_form = LikeForm()
        dislike_form = LikeForm()

        dislike_form.anecdote_id.data = like_form.anecdote_id.data = anecdote.id
        like_form.value.data = 1
        dislike_form.value.data = -1

        res[anecdote.id] = (anecdote, like_form, dislike_form)
    return res


def create_list_anecdotes_for_moderation(anecdotes):
    res = {}
    for i, anecdote in enumerate(anecdotes):
        accept_form = AcceptForm()
        reject_form = RejectForm()
        accept_form.anecdote_id.data = reject_form.anecdote_id.data = str(anecdote.id)

        res[anecdote.id] = (anecdote, accept_form, reject_form)
    return res


def create_buttons_of_pagination(page, array):
    ON_PAGE_COUNT = 20
    pages_count = ceil(len(array.all()) / ON_PAGE_COUNT)
    array = array.offset((page - 1) * ON_PAGE_COUNT).limit(ON_PAGE_COUNT).all()
    if pages_count >= 7:
        pagination = [str(page)]
        if page != 1:
            pagination = (['1', '...'] if page != 2 else []) + [str(page - 1)] + pagination
        if page != pages_count:
            pagination = pagination + ([str(page + 1), '...'] if page != pages_count - 1 else []) + [str(pages_count)]
        pagination = ['Previous'] + pagination + ['Next']
    else:
        pagination = ['Previous'] + list(map(str, range(1, pages_count + 1))) + ['Next']
    return pages_count, array, pagination


def check_like(db_sess, anecdote):
    if anecdote is not None:
        anecdote_id = anecdote[0].id
        if anecdote[1].validate_on_submit() or anecdote[2].validate_on_submit():
            value = int(request.form.get('value'))
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
