from flask import redirect, render_template, request, Blueprint
from flask_login import login_required, current_user
from data.db_session import *
from forms.add_anecdote_form import AddAnecdoteForm
from models.anecdotes import Anecdote
from models.categories import Category
from models.likes import Like
from datetime import datetime
from math import ceil
from data.system_functions import create_buttons_of_pagination, create_list_anecdotes_for_index

blueprint = Blueprint(
    'anecdotes',
    __name__,
    template_folder='templates'
)


@blueprint.route('/', methods=['GET', 'POST'])
def index():
    return redirect('/1')


@blueprint.route('/<int:page>', methods=['GET', 'POST'])
def index_with_pagination(page):
    db_sess = create_session()
    ON_PAGE_COUNT = 20
    pages_count = ceil(len(db_sess.query(Anecdote).all()) / ON_PAGE_COUNT)
    pagination = create_buttons_of_pagination(page, pages_count)
    anecdotes = db_sess.query(Anecdote).order_by(Anecdote.created_date.desc()). \
        offset((page - 1) * ON_PAGE_COUNT).limit(ON_PAGE_COUNT).all()
    anecdotes = create_list_anecdotes_for_index(anecdotes)

    if request.method == 'POST':
        anecdote_id = int(request.form[[key for key in request.form if 'anecdote_id' in key][0]])
        anecdote = anecdotes[anecdote_id]

        if anecdote[1].validate_on_submit() or anecdote[2].validate_on_submit():
            value = anecdote[1].value.data if anecdote[1].validate_on_submit() else anecdote[2].value.data
            like = db_sess.query(Like).filter(Like.user_id == current_user.id, Like.anecdote_id == anecdote_id).first()
            if like is None:
                like = Like(user_id=current_user.id, anecdote_id=anecdote_id)
            elif like is not None and like.value != int(value):
                anecdote[0].rating += int(value)
            like.value = value
            db_sess.add(like)
            db_sess.commit()

    return render_template('index.html', pagination=pagination, anecdotes=anecdotes, page=page, pages_count=pages_count)


@blueprint.route('/add_anecdote', methods=['GET', 'POST'])
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