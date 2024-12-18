from flask import Blueprint, render_template, redirect, url_for, request

from flask_login import current_user, login_required

from sadhu.web import acl, forms
from sadhu import models
import random

subviews = []

module = Blueprint(
    "assignments",
    __name__,
    url_prefix="/assignments",
)


@module.route("/")
# @acl.allows.requires(acl.is_lecturer)
@login_required
def index():
    assignments = models.Assignment.objects(owner=current_user._get_current_object())
    assignments = list(assignments)
    assignments.sort(key=lambda a: a.course.name)

    other_assignments = models.Assignment.objects(
        owner__ne=current_user._get_current_object()
    )
    other_assignments = list(other_assignments)
    other_assignments.sort(key=lambda a: a.course.name)
    return render_template(
        "/administration/assignments/index.html",
        assignments=assignments,
        other_assignments=other_assignments,
    )


@module.route("/create", methods=["GET", "POST"], defaults={"assignment_id": None})
@module.route("/<assignment_id>/edit", methods=["GET", "POST"])
# @acl.allows.requires(acl.is_lecturer)
@login_required
def create_or_edit(assignment_id):
    form = forms.assignments.AssignmentForm()
    courses = models.Course.objects()
    assignment = None
    if assignment_id:
        assignment = models.Assignment.objects.get(id=assignment_id)

    if assignment and request.method == "GET":
        form = forms.assignments.AssignmentForm(obj=assignment)
        form.course.data = str(assignment.course.id)

    form.course.choices = [(str(course.id), course.name) for course in courses]

    if not form.validate_on_submit():
        return render_template(
            "/administration/assignments/create-edit.html", form=form
        )

    data = form.data.copy()
    data.pop("course")
    data.pop("csrf_token")

    course = models.Course.objects.get(id=form.course.data)

    if not assignment:
        assignment = models.Assignment()
        assignment.owner = current_user._get_current_object()

    # remove
    if assignment.course and assignment.course != course:
        assignment.course.assignments.remove(assignment)

    form.populate_obj(assignment)
    assignment.course = course
    assignment.save()

    if assignment not in course.assignments:
        course.assignments.append(assignment)
    course.save()

    return redirect(
        url_for("administration.assignments.view", assignment_id=assignment.id)
    )


@module.route("/<assignment_id>/delete")
# @acl.allows.requires(acl.is_lecturer)
@login_required
def delete(assignment_id):
    assignment = models.Assignment.objects.get(id=assignment_id)
    course = assignment.course
    course.assignments.remove(assignment)
    course.save()

    assignment.delete()

    return redirect(url_for("administration.courses.view", course_id=course.id))


@module.route("/<assignment_id>/add-challenges", methods=["GET", "POST"])
@acl.roles_required("admin")
def add_challenge(assignment_id):
    assignment = models.Assignment.objects.get(id=assignment_id)

    challenges = models.Challenge.objects()
    choices = [
        (str(q.id), q.name) for q in challenges if q not in assignment.challenges
    ]
    form = forms.assignments.ChallengeAddingForm()
    form.challenges.choices = choices

    if not form.validate_on_submit():
        return render_template(
            "/administration/assignments/view.html", assignment=assignment, form=form
        )
    challenge_ids = form.challenges.data.copy()

    for challenge_id in challenge_ids:
        challenge = models.Challenge.objects.get(id=challenge_id)
        if challenge in assignment.challenges:
            continue

        assignment.challenges.append(challenge)

    assignment.save()
    return redirect(
        url_for("administration.assignments.view", assignment_id=assignment.id)
    )


@module.route("/<assignment_id>/", methods=["GET", "POST"])
@acl.roles_required("admin")
def random_challenges(assignment_id):
    assignment = models.Assignment.objects.get(id=assignment_id)
    random_count = int(request.form.get("random_count"))
    selected_level = request.form.get("randomLevel")

    if selected_level == "None":
        challenges = models.Challenge.objects()
    else:
        challenges = models.Challenge.objects(level=selected_level)

    for i in range(random_count):
        random_challenge = random.choice(challenges)
        form = forms.assignments.ChallengeAddingForm()
        if not form.validate_on_submit():
            return render_template(
                "/administration/assignments/view.html",
                assignment=assignment,
                form=form,
            )

        assignment.challenges.append(random_challenge)
        assignment.save()
    return redirect(
        url_for("administration.assignments.view", assignment_id=assignment.id)
    )


@module.route("/<assignment_id>/challenges/<challenge_id>/delete")
@acl.roles_required("admin")
def delete_challenge(assignment_id, challenge_id):
    assignment = models.Assignment.objects.get(id=assignment_id)
    challenge = models.Challenge.objects.get(id=challenge_id)

    if challenge in assignment.challenges:
        assignment.challenges.remove(challenge)
        assignment.save()

    return redirect(
        url_for("administration.assignments.view", assignment_id=assignment.id)
    )


@module.route("/<assignment_id>")
# @acl.allows.requires(acl.is_lecturer)
@login_required
def view(assignment_id):
    assignment = models.Assignment.objects.get(id=assignment_id)
    challenges = models.Challenge.objects()

    choices = [
        (str(q.id), q.name) for q in challenges if q not in assignment.challenges
    ]

    form = forms.assignments.ChallengeAddingForm()
    form.challenges.choices = choices

    return render_template(
        "/administration/assignments/view.html", assignment=assignment, form=form
    )
