from flask import (Blueprint,
                   render_template,
                   url_for,
                   redirect
                   )
from flask_login import current_user, login_required

from sadhu import acl
from sadhu import forms
from sadhu import models

import mongoengine as me

import datetime

module = Blueprint('teaching_assistants.classes',
                   __name__,
                   url_prefix='/classes',
                   )



@module.route('/')
@login_required
def index():
    classes = models.Class.objects(
            teaching_assistants__user=current_user._get_current_object())

    
    return render_template('/teaching-assistants/index.html',
                           classes=classes)


@module.route('/<class_id>')
@login_required
#@acl.allows.requires(acl.is_lecturer)
def view(class_id):
    class_ = models.Class.objects.get(id=class_id)
    return render_template('/administration/classes/view.html',
                           class_=class_)


@module.route('/<class_id>/list_students')
@login_required
def list_students(class_id):

    class_ = models.Class.objects.get(
            id=class_id,
            teaching_assistants__user=current_user._get_current_object())
    
    enrollments = class_.enrollments
    enrollments = sorted(enrollments, key=lambda e: e.user.first_name)

    return render_template('/administration/classes/list-students.html',
                           enrollments=enrollments,
                           class_=class_)

@module.route('/<class_id>/students/<student_id>')
# @acl.allows.requires(acl.is_lecturer)
@login_required
def show_student_score(class_id, student_id):
    class_ = models.Class.objects.get(id=class_id)
    student = models.User.objects.get(id=student_id)
    assignments = class_.course.assignments

    return render_template('/administration/classes/show-student-score.html',
                           class_=class_,
                           student=student,
                           assignments=assignments)


@module.route('/<class_id>/students/<student_id>/assignments/<assignment_id>')
# @acl.allows.requires(acl.is_lecturer)
@login_required
def show_student_assignment(class_id, student_id, assignment_id):
    class_ = models.Class.objects.get(id=class_id)
    student = models.User.objects.get(id=student_id)
    assignment = models.Assignment.objects.get(id=assignment_id)

    return render_template('/administration/classes/show-student-assignment.html',
                           class_=class_,
                           student=student,
                           assignment=assignment)


