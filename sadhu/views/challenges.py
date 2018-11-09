from flask import (Blueprint,
                   render_template,
                   request,
                   redirect,
                   url_for)
from flask_login import current_user

from sadhu import acl
from sadhu import forms
from sadhu import models

module = Blueprint('challenges',
                   __name__,
                   url_prefix='/challenges',
                   )


@module.route('/')
@acl.allows.requires(acl.is_lecturer)
def index():
    challenges = models.Challenge.objects(
            owner=current_user._get_current_object())
    # print('q', challenges)
    return render_template('/challenges/index.html',
                           challenges=challenges)


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
def view(challenge_id):
    class_ = models.Class.objects.get(id=request.args.get('class_id', None))
    challenge = models.Challenge.objects.get(id=challenge_id)

    solutions = models.Solution.objects(
            user=current_user._get_current_object(),
            enrolled_class=class_,
            challenge=challenge)

    print('sol', solutions)
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
                               challenge=challenge
                               )
    solution.code.put(form.code.data,
                      filename=form.code.data.filename)
    solution.save()
    return redirect(url_for('challenges.view',
                            challenge_id=challenge.id,
                            class_id=class_.id))
