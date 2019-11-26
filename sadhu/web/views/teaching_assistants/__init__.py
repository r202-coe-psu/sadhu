from flask import (Blueprint,
                   render_template,
                   url_for,
                   redirect
                   )
from flask_login import current_user, login_required


from sadhu import models

from . import classes
from . import solutions

subviews = [classes,
            solutions
            ]


module = Blueprint('teaching_assistants',
                   __name__,
                   url_prefix='/teaching-assistants',
                   )



@module.route('/')
@login_required
def index():
    classes = models.Class.objects(
            teaching_assistants__user=current_user._get_current_object())

    
    return render_template('/teaching-assistants/index.html',
                           classes=classes)


