from flask import (Blueprint,
                   render_template,
                   redirect,
                   url_for)

from flask_login import current_user

from sadhu import acl
from sadhu import forms
from sadhu import models

subviews = []

module = Blueprint('administration.assignments',
                   __name__,
                   url_prefix='/assignments',
                   )


@module.route('/')
@acl.allows.requires(acl.is_lecturer)
def index():
    assignments = models.Assignment.objects(
            owner=current_user._get_current_object())
    return render_template('/administration/assignments/index.html',
                           assignments=assignments)


@module.route('/create', methods=['GET', 'POST'])
@acl.allows.requires(acl.is_lecturer)
def create():
    form = forms.assignments.AssignmentForm()
    courses = models.Course.objects()
    form.course.choices = [(str(course.id), course.name) for course in courses]
    if not form.validate_on_submit():
        return render_template('/administration/assignments/create.html',
                               form=form)

    data = form.data.copy()
    data.pop('course')
    data.pop('csrf_token')

    course = models.Course.objects.get(id=form.course.data)

    assignment = models.Assignment(**data)
    assignment.owner = current_user._get_current_object()
    assignment.course = course
    assignment.save()

    course.assignments.append(assignment)
    course.save()

    return redirect(url_for('administration.assignments.view',
                            assignment_id=assignment.id))


@module.route('/<assignment_id>/add-challenges', methods=['GET', 'POST'])
@acl.allows.requires(acl.is_lecturer)
def add_challenge(assignment_id):
    assignment = models.Assignment.objects.get(id=assignment_id)
    
    challenges = models.Challenge.objects()
    choices = [(str(q.id), q.name) for q in challenges \
            if q not in assignment.challenges]
    form = forms.assignments.ChallengeAddingForm()
    form.challenges.choices = choices

    if not form.validate_on_submit():
        return render_template('/administration/assignments/view.html',
                               assignment=assignment,
                               form=form)
    challenge_ids = form.challenges.data.copy()

    for challenge_id in challenge_ids:
        challenge = models.Challenge.objects.get(id=challenge_id)
        if challenge in assignment.challenges:
            continue

        assignment.challenges.append(challenge)

    assignment.save()
    return redirect(url_for('administration.assignments.view',
                            assignment_id=assignment.id))

@module.route('/<assignment_id>')
@acl.allows.requires(acl.is_lecturer)
def view(assignment_id):
    assignment = models.Assignment.objects.get(id=assignment_id)
    challenges = models.Challenge.objects()

    choices = [(str(q.id), q.name) for q in challenges \
            if q not in assignment.challenges]

    form = forms.assignments.ChallengeAddingForm()
    form.challenges.choices = choices

    return render_template('/administration/assignments/view.html',
                           assignment=assignment,
                           form=form)

