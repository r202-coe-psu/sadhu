from flask import Blueprint, render_template

from sadhu import acl

from . import questions

subviews = []

module = Blueprint('assignments',
                   __name__,
                   url_prefix='/assignments',
                   )



@module.route('/')
@acl.allows.requires(acl.is_lecturer)
def index():
    return render_template('/assignments/index.html')
