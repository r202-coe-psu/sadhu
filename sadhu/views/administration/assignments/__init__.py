from flask import Blueprint, render_template

from sadhu import acl
from sadhu import forms

from . import questions

subviews = [questions]

module = Blueprint('assignments',
                   __name__,
                   url_prefix='/assignments',
                   )



@module.route('/')
@acl.allows.requires(acl.is_lecturer)
def index():
    return render_template('/assignments/index.html')


@module.route('/create')
@acl.allows.requires(acl.is_lecturer)
def create():
    form = forms.assignments.AssignmentForm()
    return render_template('/assignments/create.html',
                           form=form)
