from flask import Blueprint, render_template

from sadhu import acl
from sadhu import forms

from . import questions

subviews = [questions]

module = Blueprint('courses',
                   __name__,
                   url_prefix='/courses',
                   )



@module.route('/')
@acl.allows.requires(acl.is_lecturer)
def index():
    return render_template('/courses/index.html')


@module.route('/create')
@acl.allows.requires(acl.is_lecturer)
def create():
    form = forms.assignments.AssignmentForm()
    return render_template('/courses/create.html',
                           form=form)
