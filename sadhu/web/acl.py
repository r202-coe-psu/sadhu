from flask import redirect, url_for, request
from flask_login import current_user, LoginManager, login_url
from werkzeug.exceptions import Forbidden
from . import models

from functools import wraps

login_manager = LoginManager()


def init_acl(app):
    login_manager.init_app(app)

    @app.errorhandler(403)
    def page_not_found(e):
        return unauthorized_callback()


def roles_required(*roles):
    def wrapper(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                raise Forbidden()

            for role in roles:
                if role in current_user.roles:
                    return func(*args, **kwargs)
            raise Forbidden()

        return wrapped

    return wrapper


def teaching_assistant_required(func):
    """Allow users holding the `teaching_assistant` role, or listed as a TA
    on any class. Class membership alone is enough, so TAs added before the
    role was granted automatically are not locked out."""

    @wraps(func)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            raise Forbidden()

        if "teaching_assistant" in current_user.roles:
            return func(*args, **kwargs)

        if models.Class.objects(
            teaching_assistants__user=current_user._get_current_object()
        ).first():
            return func(*args, **kwargs)

        raise Forbidden()

    return wrapped


@login_manager.user_loader
def load_user(user_id):
    user = models.User.objects.with_id(user_id)
    return user


@login_manager.unauthorized_handler
def unauthorized_callback():
    if request.method == "GET":
        response = redirect(login_url("accounts.login", request.url))
        return response

    return redirect(url_for("accounts.login"))
