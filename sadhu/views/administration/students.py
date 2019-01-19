from flask import (Blueprint,
                   render_template,
                   url_for,
                   redirect
                   )
from flask_login import current_user

from sadhu import acl
from sadhu import forms
from sadhu import models

module = Blueprint('administration.students',
                   __name__,
                   url_prefix='/students',
                   )



@module.route('/list-in-class/<class_id>')
@acl.allows.requires(acl.is_lecturer)
def list_in_class(class_id):
    class_ = models.Class.objects.get(id=class_id)
    enrollments = models.Enrollment.objects(enrolled_class=class_)
    return render_template('/administration/students/list-in-class.html',
                           class_=class_,
                           enrollments=enrollments)


