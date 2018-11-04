from flask import (Blueprint,
                   render_template,
                   url_for,
                   redirect
                   )
from flask_login import current_user

from sadhu import acl
from sadhu import forms
from sadhu import models

module = Blueprint('administration.courses',
                   __name__,
                   url_prefix='/courses',
                   )



@module.route('/')
@acl.allows.requires(acl.is_lecturer)
def index():
    courses = models.Course.objects(owner=current_user._get_current_object())
    return render_template('/administration/courses/index.html',
                           courses=courses)


@module.route('/create', methods=['GET', 'POST'])
@acl.allows.requires(acl.is_lecturer)
def create():
    form = forms.courses.CourseForm()
    if not form.validate_on_submit():
        return render_template('/administration/courses/create.html',
                               form=form)
    data = form.data.copy()
    data.pop('csrf_token')
    course = models.Course(**data)
    course.owner = current_user._get_current_object()
    course.save()
    return redirect(url_for('administration.courses.index'))

@module.route('/<course_id>')
@acl.allows.requires(acl.is_lecturer)
def view(course_id):
    course = models.Course.objects.get(id=course_id)
    return render_template('/administration/courses/view.html',
                           course=course)

