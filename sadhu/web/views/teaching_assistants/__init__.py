from flask import Blueprint, render_template, url_for, redirect
from flask_login import current_user, login_required


from sadhu import models
from sadhu.web import acl


module = Blueprint(
    "teaching_assistants",
    __name__,
    url_prefix="/teaching-assistants",
)


@module.route("/")
@acl.roles_required("teaching_assistant")
def index():
    classes = models.Class.objects(
        teaching_assistants__user=current_user._get_current_object()
    )

    return render_template("/teaching-assistants/index.html.j2", classes=classes)
