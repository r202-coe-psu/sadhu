from flask import Blueprint, render_template

from sadhu import acl

module = Blueprint('assignments',
                   __name__,
                   url_prefix='/assignments',
                   )



@module.route('/')
@acl.allows.requires(acl.is_admin)
def index():
    return render_template('/assignments/index.html')
