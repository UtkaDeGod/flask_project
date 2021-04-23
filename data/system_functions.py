from math import ceil
from forms.delete_category_form import DeleteCategoryForm
from forms.admin_user_edit_form import AdminUserEditForm
from forms.like_form import LikeForm
from forms.accept_form import AcceptForm
from forms.reject_form import RejectForm
from models.categories import Category


def search_users(users):
    for i, user in enumerate(users):
        form = AdminUserEditForm(prefix=f'user_edit_form{user.id}')
        form.id.data = user.id
        users[i] = (user.id, (user, form))
    return dict(users)


def search_categories(categories):
    for i, category in enumerate(categories):
        form = DeleteCategoryForm(prefix=f'delete_category_form{category.id}')
        form.id.data = category.id
        categories[i] = (category.id, (category, form))
    return dict(categories)


def search_anecdotes(anecdotes):
    for i, anecdote in enumerate(anecdotes):
        like_form = LikeForm(prefix=f'like_form{anecdote.id}')
        dislike_form = LikeForm(prefix=f'dislike_form{anecdote.id}')

        dislike_form.anecdote_id.data = like_form.anecdote_id.data = anecdote.id
        like_form.value.data = 1
        dislike_form.value.data = -1

        anecdotes[i] = (anecdote.id, (anecdote, like_form, dislike_form))
    return dict(anecdotes)


def create_list_anecdotes_for_index(anecdotes):
    for i, anecdote in enumerate(anecdotes):
        like_form = LikeForm(prefix=f'like_form{anecdote.id}')
        dislike_form = LikeForm(prefix=f'dislike_form{anecdote.id}')
        dislike_form.anecdote_id.data = like_form.anecdote_id.data = anecdote.id
        like_form.value.data = 1
        dislike_form.value.data = -1
        anecdotes[i] = (anecdote.id, (anecdote, like_form, dislike_form))
    return dict(anecdotes)


def create_list_anecdotes_for_moderation(anecdotes):
    for i, anecdote in enumerate(anecdotes):
        accept_form = AcceptForm(prefix=f'accept_form{anecdote.id}')
        reject_form = RejectForm(prefix=f'reject_form{anecdote.id}')
        accept_form.anecdote_id.data = reject_form.anecdote_id.data = str(anecdote.id)
        print(accept_form.anecdote_id.data, reject_form.anecdote_id.data)
        anecdotes[i] = (anecdote.id, (anecdote, accept_form, reject_form))
    return dict(anecdotes)


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