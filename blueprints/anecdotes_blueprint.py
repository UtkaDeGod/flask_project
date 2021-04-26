from flask import redirect, render_template, request, Blueprint, abort
from flask_login import login_required, current_user
from data.db_session import create_session
from forms.add_anecdote_form import AddAnecdoteForm
from forms.comment_form import CommentForm
from forms.like_form import LikeForm
from models.anecdotes import Anecdote
from models.categories import Category
from models.comments import Comment
from datetime import datetime
from data.system_functions import create_buttons_of_pagination, search_anecdotes, check_like
import bleach

blueprint = Blueprint(
    'anecdotes',
    __name__,
    template_folder='templates'
)


@blueprint.route('/', methods=['GET', 'POST'])
def index():
    page = int(request.args.get('page', '1'))
    db_sess = create_session()

    anecdotes = db_sess.query(Anecdote).filter(Anecdote.is_published == 1).order_by(Anecdote.created_date.desc())
    pages_count, anecdotes, pagination = create_buttons_of_pagination(page, anecdotes)

    anecdotes = search_anecdotes(anecdotes)
    categories = db_sess.query(Category).all()

    if request.method == 'POST':
        anecdote_id = request.form.get('anecdote_id', None)
        anecdote = anecdotes[int(anecdote_id)] if anecdote_id is not None else None
        check_like(db_sess, anecdote)

        return redirect(f'#{anecdote_id}')
    return render_template('index.html', pagination=pagination, anecdotes=anecdotes, page=page, pages_count=pages_count,
                           categories=categories)


@blueprint.route('/<int:category_id>', methods=['GET', 'POST'])
def index_with_category_id(category_id):
    page = int(request.args.get('page', '1'))
    db_sess = create_session()
    select_category = db_sess.query(Category).get(category_id)

    anecdotes = db_sess.query(Anecdote).filter(Anecdote.is_published == 1, Anecdote.category_id == category_id).\
        order_by(Anecdote.created_date.desc())
    pages_count, anecdotes, pagination = create_buttons_of_pagination(page, anecdotes)

    anecdotes = search_anecdotes(anecdotes)
    categories = db_sess.query(Category).all()

    if request.method == 'POST':
        anecdote_id = request.form.get('anecdote_id', None)
        anecdote = anecdotes[int(anecdote_id)] if anecdote_id is not None else None
        check_like(db_sess, anecdote)

        return redirect(f'#{anecdote_id}')
    return render_template('index.html', pagination=pagination, anecdotes=anecdotes, page=page, pages_count=pages_count,
                           categories=categories, select_category=select_category)


@blueprint.route('/anecdote/add', methods=['GET', 'POST'])
@login_required
def add_anecdote():
    db_sess = create_session()
    form = AddAnecdoteForm()
    form.category.choices = [(category.id, category.title) for category in db_sess.query(Category).all()]
    if form.validate_on_submit():
        anecdote_text = bleach.clean(form.text.data).replace(chr(13), '').replace('\n', '<br>')
        anecdote = Anecdote(category_id=form.category.data, created_date=datetime.now(),
                            name=form.name.data, text=anecdote_text, user_id=current_user.id)
        db_sess.add(anecdote)
        db_sess.commit()
        return redirect('/')
    return render_template('add_anecdote.html', form=form)


@blueprint.route('/anecdote/<int:anecdote_id>', methods=['GET', 'POST'])
def anecdote_page(anecdote_id):
    db_sess = create_session()
    comment_id = int(request.args.get('comment_id', '-1'))

    anecdote = db_sess.query(Anecdote).get(anecdote_id)
    context = {}
    if anecdote is not None:
        like_form = LikeForm()
        dislike_form = LikeForm()
        comment_form = CommentForm(prefix='comment')
        like_form.value.data = 1
        dislike_form.value.data = -1
        check_like(db_sess, [anecdote, like_form, dislike_form])

        if comment_form.validate_on_submit():
            text = bleach.clean(comment_form.text.data).replace(chr(13), '').replace('\n', '<br>')
            comment = Comment(text=text, user_id=current_user.id, anecdote_id=anecdote_id, created_date=datetime.now())
            db_sess.add(comment)
            db_sess.commit()
        if comment_id != -1:
            comment = db_sess.query(Comment).get(comment_id)
            if comment is not None:
                db_sess.delete(comment)
                db_sess.commit()
                return redirect('')

        comments = db_sess.query(Comment).filter(Comment.anecdote == anecdote).all()
        context = {'like_form': like_form, 'dislike_form': dislike_form, 'comment_form': comment_form,
                   'comments': comments, 'anecdote': anecdote}
    return render_template('anecdote_page.html', **context)


@blueprint.route('/anecdote/edit/<int:anecdote_id>', methods=['GET', 'POST'])
@login_required
def edit_anecdote(anecdote_id):
    db_sess = create_session()
    anecdote = db_sess.query(Anecdote).get(anecdote_id)
    categories = db_sess.query(Category).all()
    if anecdote.user != current_user and not current_user.is_admin:
        abort(401)

    edit_anecdote_form = AddAnecdoteForm()
    edit_anecdote_form.category.choices = [(category.id, category.title) for category in categories]
    text_anecdote = anecdote.text.replace('<br>', chr(13))

    if edit_anecdote_form.validate_on_submit():
        anecdote.name = edit_anecdote_form.name.data
        anecdote.text = bleach.clean(edit_anecdote_form.text.data).replace(chr(13), '').replace('\n', '<br>')
        anecdote.category_id = edit_anecdote_form.category.data
        text_anecdote = anecdote.text.replace('<br>', chr(13))
        anecdote.is_published = 0
        db_sess.commit()
        return redirect('/user/anecdotes')
    return render_template('edit_anecdote.html', form=edit_anecdote_form, anecdote=anecdote,
                           text_anecdote=text_anecdote)
