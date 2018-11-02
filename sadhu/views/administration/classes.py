from flask import (Blueprint,
                   render_template,
                   url_for,
                   redirect
                   )
from flask_login import current_user

from sadhu import acl
from sadhu import forms
from sadhu import models

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


@module.route('/view/<class_id>')
@acl.allows.requires(acl.is_lecturer)
def view(class_id):
    class_ = models.Class.objects.get(id=class_id)
    return render_template('/administration/classes/view.html',
                           class_=class_)

