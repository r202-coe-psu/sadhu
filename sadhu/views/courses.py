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

module = Blueprint('courses',
                   __name__,
                   url_prefix='/courses',
                   )



@module.route('/')
@login_required
def index():
    classes = models.Class.objects(
            me.Q(limited_enrollment__grantees=current_user.username) |
            me.Q(limited_enrollment__grantees=current_user.email) )

    courses = [class_.course for class_ in classes]
    
    return render_template('/courses/index.html',
                           courses=courses)

@module.route('/<course_id>')
@login_required
def view(course_id):
    course = models.Course.objects.get(id=course_id)
    classes = models.Class.objects(me.Q(course=course) &
            (me.Q(limited_enrollment__grantees=current_user.username) |
             me.Q(limited_enrollment__grantees=current_user.email))
            )
    enrolled_classes = []
    for class_ in classes:
        enrollment = models.Enrollment.objects(
                user=current_user._get_current_object(),
                enrolled_class=class_).first()
        if enrollment:
            enrolled_classes.append(enrollment.enrolled_class)
    return render_template('/courses/view.html',
                           course=course,
                           enrolled_classes=enrolled_classes,
                           classes=classes)

