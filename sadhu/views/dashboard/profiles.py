from flask import Blueprint

module = Blueprint('dashboard.profiles', __name__, url_prefix='')

module.route('/<user_id>')
def view(user_id):
    return None
