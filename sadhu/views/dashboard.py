from flask import Blueprint, render_template
from flask_login import login_required, current_user

module = Blueprint('dashboard', __name__, url_prefix='/dashboard')
subviews = []

def index_admin():
    return render_template('/dashboard/index-admin.html')

def index_user():
    return render_template('/dashboard/index.html')

@module.route('/')
@login_required
def index():
    user = current_user._get_current_object()
    if 'lecturer' in user.roles:
        return index_admin()
    
    return index_user()
