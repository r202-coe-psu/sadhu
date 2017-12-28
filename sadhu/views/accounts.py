import datetime
from flask import (Blueprint,
                   render_template,
                   url_for,
                   redirect,
                   session,
                   request)
from flask_login import login_user, logout_user, login_required, current_user

from sadhu import models
from sadhu import oauth2

module = Blueprint('accounts', __name__)

cache = dict()


def get_user_and_remember():
    client = oauth2.oauth2_client
    result = client.principal.get('me')
    print('got: ', result.json())
    data = result.json()

    user = models.User.objects(
            username=data.get('username', '')).first()
    if not user:
        user = models.User(id=data.get('id'),
                           first_name=data.get('first_name'),
                           last_name=data.get('last_name'),
                           email=data.get('email'),
                           username=data.get('username'),
                           status='active')
        roles = []
        for role in ['student', 'lecturer', 'staff']:
            if role in data.get('roles', []):
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
    client = oauth2.oauth2_client
    callback = url_for('accounts.authorized_principal',
                       _external=True)
    response = client.principal.authorize_redirect(callback)

    cache[session['_principal_state_']] = dict(session)
    return response


@module.route('/authorized-principal')
def authorized_principal():
    if request.args.get('state') in cache:
        sdata = cache.pop(request.args.get('state'))
        session.update(sdata)

    client = oauth2.oauth2_client

    token = client.principal.authorize_access_token()
    get_user_and_remember()
    oauth2token = models.OAuth2Token(
            name=client.principal.name,
            user=current_user._get_current_object(),
            access_token=token.get('access_token'),
            token_type=token.get('token_type'),
            refresh_token=token.get('refresh_token', None),
            expires=datetime.datetime.utcfromtimestamp(
                token.get('expires_at'))
            )
    oauth2token.save()

    return redirect(url_for('accounts.login'))


@module.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('site.index'))
