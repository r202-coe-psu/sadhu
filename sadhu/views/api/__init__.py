from flask import Blueprint, render_template, g
from flask_login import login_required

from principal.oauth import oauth2
module = Blueprint('api', __name__, url_prefix='/api')


@module.route('/me')
@oauth2.require_oauth('email')
def me():
    user = request.oauth.user
    return jsonify(email=user.email, username=user.username)

@module.route('/user/<username>')
@oauth2.require_oauth('email')
def user(username):
    user = User.query.filter_by(username=username).first()
    return jsonify(email=user.email, username=user.username)
