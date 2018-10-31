from flask import (Blueprint,
                   render_template,
                   request,
                   redirect,
                   url_for)
from flask_login import current_user

from sadhu import acl
from sadhu import forms
from sadhu import models

module = Blueprint('administration.questions',
                   __name__,
                   url_prefix='/questions',
                   )


@module.route('/')
@acl.allows.requires(acl.is_lecturer)
def index():
    questions = models.Question.objects(
            owner=current_user._get_current_object())
    # print('q', questions)
    return render_template('/administration/questions/index.html',
                           questions=questions)


@module.route('/create', methods=['GET', 'POST'])
def create():
    form = forms.questions.QuestionForm(request.form)
    print(form.data)
    if not form.validate_on_submit():
        print(form.data)
        return render_template('/administration/questions/create.html',
                               form=form)
    data = form.data.copy()
    data.pop('csrf_token')
    question = models.Question(**data)
    question.owner = current_user._get_current_object()
    question.save()

    return redirect(url_for('administration.questions.view',
                            question_id=question.id))

@module.route('/<question_id>/add-testcase', methods=['GET', 'POST'])
def add_testcase():
    question = models.Question.objects.get(id=question_id)
    form = forms.questions.TestCaseForm(request.form)

    if not form.validate_on_submit():
        return redirect(url_for('administration.questions.add_testcase',
                                question_id=question.id))

    return redirect(url_for('administration.questions.view',
                            question_id=question.id))


@module.route('/<question_id>/view')
def view(question_id):
    question = models.Question.objects.get(id=question_id)
    return render_template('/administration/questions/view.html',
                           question=question)
