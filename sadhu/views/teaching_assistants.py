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

module = Blueprint('teaching_assistants',
                   __name__,
                   url_prefix='/teaching-assistants',
                   )



@module.route('/')
@login_required
def index():
    classes = models.Class.objects(
            teaching_assistants__user=current_user._get_current_objects())

    courses = [class_.course for class_ in classes]
    
    return render_template('/teaching-assistants/index.html',
                           courses=courses)

