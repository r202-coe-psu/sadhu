from flask import (Blueprint,
                   render_template,
                   request,
                   redirect,
                   url_for)
from flask_login import current_user, login_required

from sadhu import acl
from sadhu import forms
from sadhu import models

module = Blueprint('challenges',
                   __name__,
                   url_prefix='/challenges',
                   )


@module.route('/')
@login_required
def index():
    class_ = None
    if request.args.get('class_id', None):
        class_ = models.Class.objects(
                id=request.args.get('class_id')).first()

    challenges = []
    for assignment in class_.course.assignments:
        challenges.extend(assignment.challenges)
    return render_template('/challenges/index.html',
                           challenges=challenges,
                           class_=class_)


# @module.route('/create', methods=['GET', 'POST'])
# def create():
#     form = forms.challenges.ChallengeForm(request.form)
#     print(form.data)
#     if not form.validate_on_submit():
#         print(form.data)
#         return render_template('/administration/challenges/create.html',
#                                form=form)
#     data = form.data.copy()
#     data.pop('csrf_token')
#     challenge = models.Challenge(**data)
#     challenge.owner = current_user._get_current_object()
#     challenge.save()

#     return redirect(url_for('administration.challenges.view',
#                             challenge_id=challenge.id))

# @module.route('/<challenge_id>/add-testcase', methods=['GET', 'POST'])
# def add_testcase():
#     challenge = models.Challenge.objects.get(id=challenge_id)
#     form = forms.challenges.TestCaseForm(request.form)

#     if not form.validate_on_submit():
#         return redirect(url_for('administration.challenges.add_testcase',
#                                 challenge_id=challenge.id))

#     return redirect(url_for('administration.challenges.view',
#                             challenge_id=challenge.id))


@module.route('/<challenge_id>')
@login_required
def view(challenge_id):
    class_ = None
    if request.args.get('class_id', None):
        class_ = models.Class.objects(
                id=request.args.get('class_id')).first()
    challenge = models.Challenge.objects.get(id=challenge_id)

    solutions = models.Solution.objects(
            user=current_user._get_current_object(),
            enrolled_class=class_,
            challenge=challenge)

    form = forms.challenges.Solution()
    return render_template('/challenges/view.html',
                           challenge=challenge,
                           solutions=solutions,
                           form=form)


@module.route('/<challenge_id>/submit-solution', methods=['GET', 'POST'])
def submit_solution(challenge_id):
    class_ = models.Class.objects.get(id=request.args.get('class_id', None))
    challenge = models.Challenge.objects.get(id=challenge_id)
    form = forms.challenges.Solution()
    if not form.validate_on_submit():
        return render_template('/challenges/view.html',
                               challenge=challenge,
                               form=form)

    solution = models.Solution(user=current_user._get_current_object(),
                               enrolled_class=class_,
                               challenge=challenge,
                               language=class_.course.languages[0]
                               )
    solution.code.put(form.code.data,
                      filename=form.code.data.filename,
                      content_type=form.code.data.content_type)
    solution.save()
    return redirect(url_for('challenges.view',
                            challenge_id=challenge.id,
                            class_id=class_.id))
