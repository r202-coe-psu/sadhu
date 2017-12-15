from flask import Blueprint, render_template
from flask_login import login_required

from . import admin


module = Blueprint('dashboard', __name__, url_prefix='/dashboard')
subviews = [admin]


@module.route('/')
@login_required
def index():
    return render_template('/dashboard/index.html')
