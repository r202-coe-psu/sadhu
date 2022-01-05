from flask import redirect, url_for, request, session
from flask_login import LoginManager, UserMixin, current_user, login_url
from functools import wraps

from . import models


login_manager = LoginManager()


def roles_required(*roles):
    def wrapper(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            for role in roles:
                if role in current_user.roles:
                    return func(*args, **kwargs)
            raise Forbidden()

        return wrapped

    return wrapper


def is_admin(ident, request):
    return "admin" in ident.roles


def is_developer(ident, request):
    return "developer" in ident.roles


def is_staff(ident, request):
    return "staff" in ident.roles


def is_lecturer(ident, request):
    return "lecturer" in ident.roles


def is_admin_or_lecturer(ident, request):
    return "admin" in ident.roles or "lecturer" in ident.roles


def is_teaching_assistant(ident, request):
    class_id = request.view_args.get("class_id", None)
    solution_id = request.view_args.get("solution_id", None)

    if class_id:
        try:
            class_ = models.Class.objects.get(
                id=class_id, teaching_assistants__user=ident._get_current_object()
            )
            if class_:
                return True
        except Exception as e:
            return False
    elif solution_id:
        try:
            solution = models.Solution.objects.get(id=solution_id)

            if solution.enrolled_class.is_teaching_assistant(
                ident._get_current_object()
            ):
                return True
        except Exception as e:
            return False

    return False


def is_solution_owner(ident, request):
    try:
        solution = models.Solution.objects.get(
            id=request.view_args.get("solution_id"), owner=ident._get_current_object()
        )
        if solution:
            return True
    except Exception as e:
        return False

    return False


def is_class_owner(ident, request):

    try:
        class_ = models.Class.objects.get(
            id=request.view_args.get("class_id"), owner=ident._get_current_object()
        )
        if class_:
            return True
    except Exception as e:
        return False

    return False


def init_acl(app):
    # initial login manager
    login_manager.init_app(app)


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
