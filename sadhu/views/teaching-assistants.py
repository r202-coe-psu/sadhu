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

