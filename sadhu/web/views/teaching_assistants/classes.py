from flask import Blueprint, render_template, url_for, redirect
from flask_login import current_user, login_required
from werkzeug.exceptions import Forbidden

from sadhu.web import acl
from sadhu.web import forms
from sadhu import models

import mongoengine as me

import datetime

module = Blueprint(
    "classes",
    __name__,
    url_prefix="/classes",
)


def get_assisted_class(class_id):
    """Return the class only if the current user is one of its TAs."""
    class_ = models.Class.objects(
        id=class_id, teaching_assistants__user=current_user._get_current_object()
    ).first()
    if not class_:
        raise Forbidden()
    return class_


@module.route("/")
@acl.teaching_assistant_required
def index():
    classes = models.Class.objects(
        teaching_assistants__user=current_user._get_current_object()
    )

    return render_template("/teaching-assistants/index.html.j2", classes=classes)


@module.route("/<class_id>")
@acl.teaching_assistant_required
def view(class_id):
    class_ = get_assisted_class(class_id)
    return render_template("/administration/classes/view.html.j2", class_=class_)


@module.route("/<class_id>/list_students")
@acl.teaching_assistant_required
def list_students(class_id):
    class_ = get_assisted_class(class_id)

    enrollments = class_.get_enrollments()
    enrollments = sorted(enrollments, key=lambda e: e.user.first_name)
    users = [e.user for e in enrollments]
    scores = class_.get_bulk_assignment_scores(users)

    return render_template(
        "/administration/classes/list-users.html.j2",
        enrollments=enrollments,
        class_=class_,
        scores=scores,
    )


@module.route("/<class_id>/students/<user_id>")
@acl.teaching_assistant_required
@login_required
def show_user_score(class_id, user_id):
    class_ = get_assisted_class(class_id)
    user = models.User.objects.get(id=user_id)
    assignments = class_.course.assignments
    scores = {a.id: a.get_class_scores(class_, [user])[user.id] for a in assignments}

    return render_template(
        "/administration/classes/show-user-score.html.j2",
        class_=class_,
        user=user,
        assignments=assignments,
        scores=scores,
    )


@module.route("/<class_id>/students/<user_id>/assignments/<assignment_id>")
@acl.teaching_assistant_required
def show_user_assignment(class_id, user_id, assignment_id):
    class_ = get_assisted_class(class_id)
    user = models.User.objects.get(id=user_id)
    assignment = models.Assignment.objects.get(id=assignment_id)

    return render_template(
        "/administration/classes/show-user-assignment.html.j2",
        class_=class_,
        user=user,
        assignment=assignment,
    )


@module.route("/<class_id>/assignments/<assignment_id>/students")
@acl.teaching_assistant_required
def list_assignment_users(class_id, assignment_id):
    class_ = get_assisted_class(class_id)
    assignment = models.Assignment.objects.get(id=assignment_id)
    enrollments = class_.get_enrollments()
    users = [e.user for e in enrollments]
    users.sort(key=lambda u: u.first_name)
    scores = assignment.get_class_scores(class_, users)

    return render_template(
        "/administration/classes/list-assignment-users.html.j2",
        class_=class_,
        users=users,
        assignment=assignment,
        scores=scores,
    )


@module.route("/<class_id>/solutions")
@acl.teaching_assistant_required
def list_class_solutions(class_id):
    class_ = get_assisted_class(class_id)
    solutions = models.Solution.objects(enrolled_class=class_).order_by("-id").limit(50)
    return render_template(
        "/administration/classes/solutions.html.j2", solutions=solutions, class_=class_
    )
