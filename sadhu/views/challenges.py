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
    return render_template('/administration/challenges/index.html',
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

@module.route('/<challenge_id>/add-testcase', methods=['GET', 'POST'])
def add_testcase():
    challenge = models.Challenge.objects.get(id=challenge_id)
    form = forms.challenges.TestCaseForm(request.form)

    if not form.validate_on_submit():
        return redirect(url_for('administration.challenges.add_testcase',
                                challenge_id=challenge.id))

    return redirect(url_for('administration.challenges.view',
                            challenge_id=challenge.id))


@module.route('/<challenge_id>')
def view(challenge_id):
    challenge = models.Challenge.objects.get(id=challenge_id)
    return render_template('/administration/challenges/view.html',
                           challenge=challenge)
