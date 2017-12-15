from flask import Blueprint

from principal import acl

module = Blueprint('dashboard.admin', __name__, url_prefix='/admin')



@module.route('/')
@acl.allows.requires(acl.is_admin)
def index():
    return 'admin'
