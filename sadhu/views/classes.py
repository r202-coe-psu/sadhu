from flask import (Blueprint,
                   render_template,
                   url_for,
                   redirect
                   )
from flask_login import current_user, login_required

from sadhu import acl
from sadhu import forms
from sadhu import models

module = Blueprint('classes',
                   __name__,
                   url_prefix='/classes',
                   )


@module.route('/')
@login_required
def index():
    classes = models.Class.objects(owner=current_user._get_current_object())
    return render_template('/classes/index.html',
                           classes=classes)

@module.route('/<class_id>')
@login_required
def view(class_id):
    class_ = models.Class.objects.get(id=class_id)
    enrollment = models.Enrollment.objects(
            user=current_user._get_current_object(),
            enrolled_class=class_).first()
    return render_template('/classes/view.html',
                           enrollment=enrollment,
                           class_=class_)

@module.route('/<class_id>/enroll')
@login_required
def enroll(class_id):
    class_ = models.Class.objects.get(id=class_id)
    enrollment = models.Enrollment.objects(enrolled_class=class_).first()
    if not enrollment:
        enrollment = models.Enrollment(
                user=current_user._get_current_object(),
                enrolled_class=class_)
        enrollment.save()
    return redirect(url_for('classes.view', class_id=class_.id))

