from flask import Blueprint, render_template
from flask_login import login_required

from sadhu.web import acl

module = Blueprint("administration", __name__, url_prefix="/administration")


@module.route("/")
@login_required
@acl.roles_required("admin")
def index():
    return render_template("/dashboard/index.html")
