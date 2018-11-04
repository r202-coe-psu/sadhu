from flask import (Blueprint,
                   render_template,
                   url_for,
                   redirect
                   )
from flask_login import current_user

from sadhu import acl
from sadhu import forms
from sadhu import models

import datetime

module = Blueprint('administration.classes',
                   __name__,
                   url_prefix='/classes',
                   )


@module.route('/')
@acl.allows.requires(acl.is_lecturer)
def index():
    classes = models.Class.objects(owner=current_user._get_current_object())
    return render_template('/administration/classes/index.html',
                           classes=classes)


@module.route('/create', methods=['GET', 'POST'])
@acl.allows.requires(acl.is_lecturer)
def create():
    form = forms.classes.ClassForm()
    courses = models.Course.objects()

    course_choices = [(str(c.id), c.name) for c in courses]
    form.course.choices = course_choices
    method_choices = [('email', 'Email'), ('student_id', 'Student ID')]
    form.limited_enrollment.method.choices = method_choices

    if not form.validate_on_submit():
        return render_template('/administration/classes/create.html',
                               form=form)
    data = form.data.copy()
    data.pop('csrf_token')
    data.pop('limited_enrollment')

    class_ = models.Class(**data)
    class_.owner = current_user._get_current_object()
    if class_.limited:
        if class_.limited_enrollment is None:
            class_.limited_enrollment = models.LimitedEnrollment()
        class_.limited_enrollment.method = form.limited_enrollment.method.data
        for grantee in form.limited_enrollment.grantees.data.split('\n'):
            class_.limited_enrollment.grantees.append(grantee.strip())
    class_.save()
    return redirect(url_for('administration.classes.index'))


@module.route('/<class_id>')
@acl.allows.requires(acl.is_lecturer)
def view(class_id):
    class_ = models.Class.objects.get(id=class_id)
    return render_template('/administration/classes/view.html',
                           class_=class_)

@module.route('/<class_id>/set-assignment-time/<assignment_id>',
              methods=['GET', 'POST'])
@acl.allows.requires(acl.is_lecturer)
def set_assignment_time(class_id, assignment_id):
    class_ = models.Class.objects.get(id=class_id)
    assignment = models.Assignment.objects.get(id=assignment_id)

    ass_time = class_.get_assignment_schedule(assignment)
    data = dict()
    if ass_time:
        data = dict(started_date=ass_time.started_date.date(),
                    started_time=ass_time.started_date.time(),
                    ended_date=ass_time.ended_date.date(),
                    ended_time=ass_time.ended_date.time())
    
    form = forms.assignments.AssignmentTimeForm(data=data)

    if not form.validate_on_submit():
        return  render_template(
            '/administration/classes/set-assignment-time.html',
            form=form)
    if not ass_time:
        ass_time = models.AssignmentTime(assignment=assignment)

    ass_time.started_date = datetime.datetime.combine(
            form.started_date.data,
            form.started_time.data)

    ass_time.ended_date = datetime.datetime.combine(
            form.ended_date.data,
            form.ended_time.data)

    if ass_time not in class_.assignment_schedule:
        class_.assignment_schedule.append(ass_time)
    class_.save()

    return redirect(url_for('administration.classes.view', class_id=class_id))
