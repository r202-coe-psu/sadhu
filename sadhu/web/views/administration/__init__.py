from flask import Blueprint, render_template
from flask_login import login_required

module = Blueprint("administration", __name__, url_prefix="/administration")


@module.route("/")
@login_required
def index():
    return render_template("/dashboard/index.html")
