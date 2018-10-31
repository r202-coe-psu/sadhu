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


@module.route('/<assignment_id>/add-questions', methods=['GET', 'POST'])
@acl.allows.requires(acl.is_lecturer)
def add_question(assignment_id):
    assignment = models.Assignment.objects.get(id=assignment_id)
    
    questions = models.Question.objects()
    choices = [(str(q.id), q.name) for q in questions]
    form = forms.assignments.QuestionAddingForm()
    form.questions.choices = choices

    if not form.validate_on_submit():
        return render_template('/administration/assignments/view.html',
                               assignment=assignment,
                               form=form)
    question_ids = form.questions.data.copy()

    print('\n\nqids', question_ids)
    for question_id in question_ids:
        print('\n\nqid', question_id)
        question = models.Question.objects.get(id=question_id)
        assignment.questions.append(question)

    assignment.save()
    return redirect(url_for('administration.assignments.view',
                            assignment_id=assignment.id))

@module.route('/<assignment_id>')
@acl.allows.requires(acl.is_lecturer)
def view(assignment_id):
    questions = models.Question.objects()
    choices = [(str(q.id), q.name) for q in questions]
    form = forms.assignments.QuestionAddingForm()
    form.questions.choices = choices

    assignment = models.Assignment.objects.get(id=assignment_id)

    return render_template('/administration/assignments/view.html',
                           assignment=assignment,
                           form=form)

