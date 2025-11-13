from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import current_user, login_required

from .. import forms
from sadhu import models

module = Blueprint("scoreboards", __name__, url_prefix="/scoreboards")


@module.route("/classes/<class_id>/assignments/<assignment_id>")
def show_assignment_scores(class_id, assignment_id):
    class_ = models.Class.objects.get(id=class_id)
    assignment = models.Assignment.objects.get(id=assignment_id)

    return render_template(
        "scoreboards/show_assignment_scores.html.j2", class_=class_, assignment=assignment
    )


@module.route("/classes/<class_id>/assignments/<assignment_id>/scores")
def list_assignment_scores(class_id, assignment_id):
    class_ = models.Class.objects.get(id=class_id)
    assignment = models.Assignment.objects.get(id=assignment_id)
    if not assignment:
        return

    challenge_count = len(assignment.challenges)

    data = dict()
    for e in class_.get_enrollments():
        data[str(e.user.id)] = dict(
            name=e.user.first_name,
            score=assignment.get_score(class_, e.user),
            max_score=assignment.score,
            complete=assignment.count_done_challenges(class_, e.user),
            challenges=challenge_count,
        )

    return jsonify(data)
