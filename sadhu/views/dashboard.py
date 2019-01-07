from flask import Blueprint, render_template
from flask_login import login_required, current_user

from sadhu import models
import mongoengine as me

import datetime

module = Blueprint('dashboard', __name__, url_prefix='/dashboard')
subviews = []

def index_admin():
    return render_template('/dashboard/index-admin.html')

def index_user():

    user = current_user
    now = datetime.datetime.now()

    available_classes = models.Class.objects(
            (me.Q(limited_enrollment__grantees=user.email) | 
                 me.Q(limited_enrollment__grantees=user.username)) &
            (me.Q(started_date__lte=now) |
                 me.Q(ended_date__gt=now))
            )

    assignment_schedule = []
    for class_ in available_classes:
        for ass_t in class_.assignment_schedule:
            if now < ass_t.ended_date:
                assignment_schedule.append(ass_t)

    return render_template('/dashboard/index.html',
                           available_classes=available_classes,
                           assignment_schedule=assignment_schedule
                           )

@module.route('/')
@login_required
def index():
    user = current_user._get_current_object()
    if 'lecturer' in user.roles:
        return index_admin()
    
    return index_user()
