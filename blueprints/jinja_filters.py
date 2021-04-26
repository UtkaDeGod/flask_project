from models.likes import Like
from flask_login.mixins import AnonymousUserMixin
import jinja2
import flask


blueprint = flask.Blueprint('filters', __name__)


@jinja2.contextfilter
@blueprint.app_template_filter()
def like_class(context, value):
    dct = {0: ('outline-', 'outline-'), 1: ('', 'outline-'), -1: ('outline-', '')}
    user = dict(context).get('current_user', None)
    if isinstance(user, AnonymousUserMixin) or not all(isinstance(like, Like) for like in value):
        return dct[0]
    for like in value:
        if like.user == user:
            return dct[like.value]
    return dct[0]


blueprint.add_app_template_filter(like_class)
