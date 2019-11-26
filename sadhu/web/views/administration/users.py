from flask import (Blueprint,
                   render_template,
                   url_for,
                   redirect
                   )
from flask_login import current_user

from sadhu.web import acl, forms
from sadhu import models

module = Blueprint('administration.users',
                   __name__,
                   url_prefix='/users',
                   )


@module.route('/')
@acl.allows.requires(acl.is_admin)
def index():
    users = models.User.objects().order_by('-id')
    return render_template('/administration/users/index.html',
                           users=users)
