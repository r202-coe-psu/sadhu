from flask import (Blueprint,
                   render_template,
                   url_for,
                   redirect,
                   session,
                   request)
from flask_login import login_user, logout_user, login_required, current_user

from sadhu import models
from sadhu import oauth

module = Blueprint('accounts', __name__)


def get_user_and_remember():
    remote = oauth.get_remote()
    ret = remote.get('me')

    user = models.User.objects(username=ret.data.get('userna', None)).first()
    if not user:
        user = models.User(id=ret.data.get('id'),
                           first_name=ret.data.get('first_name'),
                           last_name=ret.data.get('last_name'),
                           email=ret.data.get('email'),
                           username=ret.data.get('username'),
                           status='active')
        print('\n\ndata', ret.data)
        roles = []
        for role in ['student', 'lecturer', 'staff']:
            if role in ret.data.get('roles'):
                roles.append(role)

        user.save()
    if user:
        login_user(user)


@module.route('/login', methods=('GET', 'POST'))
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    return render_template('/accounts/login.html')


@module.route('/login-principal')
def login_principal():
    remote = oauth.get_remote()
    return remote.authorize(callback=url_for('accounts.authorized_principal',
                                             _external=True))


@module.route('/authorized-principal')
def authorized_principal():
    remote = oauth.get_remote()
    remote.authorize(callback=url_for('accounts.authorized_principal',
                                      _external=True))

    resp = remote.authorized_response()
    if resp is None:
        return 'Access denied: error=%s' % (
            request.args['error']
        )
    if isinstance(resp, dict) and 'access_token' in resp:
        session['principal-tokens'] = resp
        get_user_and_remember()

        return redirect(url_for('dashboard.index'))

    return redirect(url_for('accounts.login'))


@module.route('/logout')
@login_required
def logout():
    session.pop('principal-tokens', None)
    logout_user()
    return redirect(url_for('site.index'))
