from flask import Blueprint, render_template

from sadhu import acl
from sadhu import forms


subviews = []

module = Blueprint('administration.assignments',
                   __name__,
                   url_prefix='/assignments',
                   )



@module.route('/')
@acl.allows.requires(acl.is_lecturer)
def index():
    return render_template('/administration/assignments/index.html')


@module.route('/create')
@acl.allows.requires(acl.is_lecturer)
def create():
    form = forms.assignments.AssignmentForm()
    return render_template('/administration/assignments/create.html',
                           form=form)
