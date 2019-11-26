from flask import (Blueprint,
                   render_template,
                   url_for,
                   redirect
                   )
from flask_login import current_user, login_required

from sadhu.web import acl
from sadhu.web import forms
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
@acl.allows.requires(acl.is_teaching_assistant)
def view(class_id):
    class_ = models.Class.objects.get(id=class_id)
    return render_template('/administration/classes/view.html',
                           class_=class_)


@module.route('/<class_id>/list_students')
@acl.allows.requires(acl.is_teaching_assistant)
def list_students(class_id):

    class_ = models.Class.objects.get(
            id=class_id,
            teaching_assistants__user=current_user._get_current_object())
    
    enrollments = class_.enrollments
    enrollments = sorted(enrollments, key=lambda e: e.user.first_name)

    return render_template('/administration/classes/list-users.html',
                           enrollments=enrollments,
                           class_=class_)

@module.route('/<class_id>/students/<user_id>')
@acl.allows.requires(acl.is_teaching_assistant)
def show_user_score(class_id, user_id):
    class_ = models.Class.objects.get(id=class_id)
    user = models.User.objects.get(id=user_id)
    assignments = class_.course.assignments

    return render_template('/administration/classes/show-user-score.html',
                           class_=class_,
                           user=user,
                           assignments=assignments)


@module.route('/<class_id>/students/<user_id>/assignments/<assignment_id>')
@acl.allows.requires(acl.is_teaching_assistant)
def show_user_assignment(class_id, user_id, assignment_id):
    class_ = models.Class.objects.get(id=class_id)
    user = models.User.objects.get(id=user_id)
    assignment = models.Assignment.objects.get(id=assignment_id)

    return render_template('/administration/classes/show-user-assignment.html',
                           class_=class_,
                           user=user,
                           assignment=assignment)


