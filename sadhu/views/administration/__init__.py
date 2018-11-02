from flask import Blueprint, render_template
from flask_login import login_required

from . import assignments
from . import challenges
from . import courses
from . import classes

module = Blueprint('administration',
                   __name__,
                   url_prefix='/administration')
subviews = [assignments,
            challenges,
            courses,
            classes
            ]

@module.route('/')
@login_required
def index():
    return render_template('/dashboard/index.html')
