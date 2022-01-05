from flask import Blueprint

from sadhu.web import acl

module = Blueprint("admin", __name__, url_prefix="/admin")


@module.route("/")
# @acl.allows.requires(acl.is_admin)
@acl.roles_required("admin")
def index():
    return "admin"
