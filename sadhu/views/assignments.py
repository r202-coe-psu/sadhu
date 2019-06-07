from flask import (Blueprint,
                   render_template,
                   redirect,
                   request,
                   url_for)

from flask_login import current_user, login_required

from sadhu import acl
from sadhu import forms
from sadhu import models

subviews = []

module = Blueprint('assignments',
                   __name__,
                   url_prefix='/assignments',
                   )


@module.route('/')
@login_required
def index():
    assignment_schedule = models.assignments.get_assignment_schedule(
            current_user._get_current_object())
    print(assignment_schedule)
    return render_template('/assignments/index.html',
                           assignment_schedule=assignment_schedule)


@module.route('/<assignment_id>')
@login_required
def view(assignment_id):
    assignment = models.Assignment.objects.get(id=assignment_id)

    return render_template('/assignments/view.html',
                           assignment=assignment,
                           )


@module.route('/<assignment_id>/practice')
@login_required
def practice(assignment_id):
    class_ = None
    if request.args.get('class_id', None):
        class_ = models.Class.objects(
                id=request.args.get('class_id')).first()

    assignment = models.Assignment.objects.get(id=assignment_id)

    return render_template('/assignments/practice.html',
                           assignment=assignment,
                           class_=class_
                           )

