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
        login_user(user, remember=True)


@module.route('/login', methods=('GET', 'POST'))
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    return render_template('/accounts/login.html')


@module.route('/login-principal')
def login_principal():
    client = oauth2.oauth2_client
    redirect_uri = url_for('accounts.authorized_principal',
                       _external=True)
    response = client.principal.authorize_redirect(redirect_uri)

    return response

@module.route('/login-engpsu')
def login_engpsu():
    client = oauth2.oauth2_client
    redirect_uri = url_for('accounts.authorized_engpsu',
                       _external=True)
    response = client.engpsu.authorize_redirect(redirect_uri)
    return response

@module.route('/authorized-principal')
def authorized_principal():
    client = oauth2.oauth2_client

    try:
        token = client.principal.authorize_access_token()
    except Exception as e:
        print(e)
        return redirect(url_for('accounts.login'))

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

    return redirect(url_for('dashboard.index'))

@module.route('/authorized-engpsu')
def authorized_engpsu():
    client = oauth2.oauth2_client
    try:
        token = client.engpsu.authorize_access_token()
    except Exception as e:
        print(e)
        return redirect(url_for('accounts.login'))

    userinfo_response = client.engpsu.get('userinfo')
    userinfo = userinfo_response.json()
 
    user = models.User.objects(username=userinfo.get('username')).first()

    if not user:
        user = models.User(
                username=userinfo.get('username'),
                email=userinfo.get('email'),
                first_name=userinfo.get('first_name'),
                last_name=userinfo.get('last_name'),
                status='active')
        user.resources[client.engpsu.name] = userinfo
        # if 'staff_id' in userinfo.keys():
        #     user.roles.append('staff')
        # elif 'student_id' in userinfo.keys():
        #     user.roles.append('student')
        if userinfo['username'].isdigit():
            user.roles.append('student')
        else:
            user.roles.append('staff')

        user.save()

    login_user(user)

    oauth2token = models.OAuth2Token(
            name=client.engpsu.name,
            user=user,
            access_token=token.get('access_token'),
            token_type=token.get('token_type'),
            refresh_token=token.get('refresh_token', None),
            expires=datetime.datetime.utcfromtimestamp(
                token.get('expires_in'))
            )
    oauth2token.save()

    return redirect(url_for('dashboard.index'))


@module.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('site.index'))
