from models.users import User
from forms.edit_anecdote_form import EditAnecdoteForm
from forms.delete_category_form import DeleteCategoryForm
from forms.admin_user_edit_form import AdminUserEditForm
from forms.like_form import LikeForm
from forms.accept_form import AcceptForm
from forms.reject_form import RejectForm
from models.anecdotes import Anecdote
from models.categories import Category


def search_users(db_sess, line=''):
    users = db_sess.query(User).filter(User.name.like(f'%{line}%')).all()
    for i, user in enumerate(users):
        form = AdminUserEditForm(prefix=f'user_edit_form{user.id}')
        form.id.data = user.id
        users[i] = (user.id, (user, form))
    return dict(users)


def search_categories(db_sess, line=''):
    categories = db_sess.query(Category).filter(Category.title.like(f'%{line}%')).all()
    for i, category in enumerate(categories):
        form = DeleteCategoryForm(prefix=f'delete_category_form{category.id}')
        form.id.data = category.id
        categories[i] = (category.id, (category, form))
    return dict(categories)


def search_anecdotes(db_sess, user_id):
    anecdotes = db_sess.query(Anecdote).filter(User.id == user_id).all()
    categories = db_sess.query(Category).all()
    for i, anecdote in enumerate(anecdotes):
        like_form = LikeForm(prefix=f'like_form{anecdote.id}')
        dislike_form = LikeForm(prefix=f'dislike_form{anecdote.id}')

        edit_form = EditAnecdoteForm(prefix=f'edit_form{anecdote.id}')
        edit_form.category_id.choices = [(category.id, category.title) for category in categories]

        dislike_form.anecdote_id.data = like_form.anecdote_id.data = edit_form.anecdote_id.data = anecdote.id
        like_form.value.data = 1
        dislike_form.value.data = -1

        anecdotes[i] = (anecdote.id, (anecdote, like_form, dislike_form, edit_form))
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


def create_list_anecdotes_for_moderation(db_sess):
    anecdotes = db_sess.query(Anecdote).filter(Anecdote.is_published == 0).all()
    for i, anecdote in enumerate(anecdotes):
        accept_form = AcceptForm(prefix=f'accept_form{anecdote.id}')
        reject_form = RejectForm(prefix=f'reject_form{anecdote.id}')
        accept_form.anecdote_id.data = reject_form.anecdote_id.data = str(anecdote.id)
        print(accept_form.anecdote_id.data, reject_form.anecdote_id.data)
        anecdotes[i] = (anecdote.id, (anecdote, accept_form, reject_form))
    return dict(anecdotes)


def create_buttons_of_pagination(page, pages_count):
    if pages_count >= 7:
        pagination = [str(page)]
        if page != 1:
            pagination = (['1', '...'] if page != 2 else []) + [str(page - 1)] + pagination
        if page != pages_count:
            pagination = pagination + ([str(page + 1), '...'] if page != pages_count - 1 else []) + [str(pages_count)]
        pagination = ['Previous'] + pagination + ['Next']
    else:
        pagination = ['Previous'] + list(map(str, range(1, pages_count + 1))) + ['Next']
    return pagination