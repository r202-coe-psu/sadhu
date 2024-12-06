from flask import (
    Blueprint,
    render_template,
    url_for,
    redirect,
    request,
)
import mongoengine as me
from flask_login import current_user, login_required

from sadhu.web import acl, forms
from sadhu import models

module = Blueprint(
    "courses",
    __name__,
    url_prefix="/courses",
)


@module.route("/")
# @acl.allows.requires(acl.is_lecturer)
@login_required
def index():
    user = current_user._get_current_object()
    owner_courses = models.Course.objects(owner=user).order_by("-id")
    contributed_courses = models.Course.objects(owner__ne=user).order_by("-id")

    return render_template(
        "/administration/courses/index.html",
        owner_courses=owner_courses,
        contributed_courses=contributed_courses,
    )


@module.route("/create", defaults={"course_id": None}, methods=["GET", "POST"])
@module.route("/<course_id>/edit", methods=["GET", "POST"])
# @acl.allows.requires(acl.is_lecturer)
@login_required
def create_or_edit(course_id):
    form = forms.courses.CourseForm()
    course = None
    if course_id:
        course = models.Course.objects.get(id=course_id)
        form = forms.courses.CourseForm(obj=course)

        if request.method == "GET":
            form.contributors.data = [str(u.id) for u in course.contributors]

    form.languages.choices = models.LANGUAGE_CHOICES.copy()

    users = models.User.objects(status="active")
    form.contributors.choices = [
        (str(u.id), f"{u.first_name} {u.last_name} ({u.email})") for u in users
    ]
    if not form.validate_on_submit():
        # if not form.languages.data:
        #     form.languages.choices.insert(0, ('', 'Select Language'))
        #     form.languages.data = ['']
        # print('++++', form.languages.choices)
        return render_template("/administration/courses/create-edit.html", form=form)
    data = form.data.copy()
    data.pop("csrf_token")
    if not course:
        course = models.Course(**data)
        course.owner = current_user._get_current_object()

    contributors = [models.User.objects.get(id=c_id) for c_id in form.contributors.data]
    course.contributors = contributors
    course.save()

    return redirect(url_for("administration.courses.index"))


@module.route("/<course_id>")
# @acl.allows.requires(acl.is_lecturer)
@login_required
def view(course_id):
    course = models.Course.objects.get(id=course_id)
    return render_template("/administration/courses/view.html", course=course)
