from flask import redirect, url_for, request, session
from flask_login import LoginManager, UserMixin, current_user, login_url
from flask_allows import Allows

from . import models

allows = Allows(identity_loader=lambda: current_user)


def is_admin(ident, request):
    return 'admin' in ident.roles


def is_developer(ident, request):
    return 'developer' in ident.roles


def is_staff(ident, request):
    return 'staff' in ident.roles




def init_acl(app):
    # initial login manager
    login_manager = LoginManager(app)

    @login_manager.user_loader
    def load_user(user_id):
        user = models.User.objects.with_id(user_id)
        return user

    @login_manager.unauthorized_handler
    def unauthorized_callback():
        if request.method == 'GET':
            response = redirect(login_url('accounts.login',
                                           request.url))
            return response

        return redirect(url_for('accounts.login'))
