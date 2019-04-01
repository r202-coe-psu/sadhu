from flask import (Blueprint,
                   render_template,
                   request,
                   redirect,
                   url_for)
from flask_login import current_user


import markdown
from pygments.formatters import HtmlFormatter


from sadhu import acl
from sadhu import forms
from sadhu import models


module = Blueprint('administration.challenges',
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


@module.route('/create', methods=['GET', 'POST'])
@acl.allows.requires(acl.is_lecturer)
def create():
    form = forms.challenges.ChallengeForm(request.form)
    print(form.data)
    if not form.validate_on_submit():
        return render_template('/administration/challenges/create-edit.html',
                               form=form)
    data = form.data.copy()
    data.pop('csrf_token')
    challenge = models.Challenge(**data)
    challenge.owner = current_user._get_current_object()
    challenge.save()

    return redirect(url_for('administration.challenges.view',
                            challenge_id=challenge.id))


@module.route('/<challenge_id>/edit', methods=['GET', 'POST'])
@acl.allows.requires(acl.is_lecturer)
def edit(challenge_id):
    challenge = models.Challenge.objects.get(id=challenge_id)

    form = forms.challenges.ChallengeForm(obj=challenge)
    if not form.validate_on_submit():
        return render_template('/administration/challenges/create-edit.html',
                               form=form)
    data = form.data.copy()
    data.pop('csrf_token')
    form.populate_obj(challenge)
    challenge.save()

    return redirect(url_for('administration.challenges.view',
                            challenge_id=challenge.id))




@module.route('/<challenge_id>/add-testcase', methods=['GET', 'POST'])
@acl.allows.requires(acl.is_lecturer)
def add_testcase(challenge_id):
    challenge = models.Challenge.objects.get(id=challenge_id)
    form = forms.challenges.TestCaseForm()

    if not form.validate_on_submit():
        return render_template('/administration/challenges/add-testcase.html',
                               form=form,
                               challenge=challenge)
        
    test_case = models.TestCase(public=form.public.data,
                                owner=current_user._get_current_object(),
                                challenge=challenge)

        
    if form.input_file.data:
        if form.is_inputfile.data:
            test_case.input_file.put(form.input_file.data,
                    filename=form.input_file.data.filename,
                    content_type=form.input_file.data.content_type)
        else:
            data = form.input_file.data.read()
            test_case.input_string = data.replace('\r', '')

    if form.output_file.data:
        if form.is_outputfile.data:
            test_case.output_file.put(form.output_file.data,
                    filename=form.output_file.data.filename,
                    content_type=form.output_file.data.content_type)
        else:
            test_case.output_string = form.output_file.data.read()

    if (not test_case.input_string) or len(test_case.input_string) == 0:
        test_case.input_string = form.input_string.data.replace('\r', '')

    if (not test_case.output_string) or len(test_case.output_string) == 0:
        test_case.output_string = form.output_string.data

    test_case.is_inputfile = form.is_inputfile.data
    test_case.is_outputfile = form.is_outputfile.data
    
    test_case.save()

    challenge.test_cases.append(test_case)
    challenge.save()

    return redirect(url_for('administration.challenges.view',
                            challenge_id=challenge.id))


@module.route('/<challenge_id>/testcases/<testcase_id>/edit', methods=['GET', 'POST'])
@acl.allows.requires(acl.is_lecturer)
def edit_testcase(challenge_id, testcase_id):
    challenge = models.Challenge.objects.get(id=challenge_id)
    test_case = models.TestCase.objects.get(id=testcase_id)
    form = forms.challenges.TestCaseForm(obj=test_case)

    if not form.validate_on_submit():
        return render_template('/administration/challenges/add-testcase.html',
                               form=form,
                               challenge=challenge)
    
    data = form.data.copy()
    data.pop('input_file')
    data.pop('output_file')
    data.pop('csrf_token')

    test_case.update(**data)
    test_case.input_string = test_case.input_string.replace('\r', '')

    if form.input_file.data:

        if form.is_inputfile.data:
            test_case.input_file.put(form.input_file.data,
                    filename=form.input_file.data.filename,
                    content_type=form.input_file.data.content_type)
        else:
            data = form.input_file.data.read()
            test_case.input_string = data.replace('\r', '')

    if form.output_file.data:
        if form.is_outputfile.data:
            test_case.output_file.put(form.output_file.data,
                    filename=form.output_file.data.filename,
                    content_type=form.output_file.data.content_type)
        else:
            test_case.output_string = form.output_file.data.read()

    if (not test_case.input_string) or len(test_case.input_string) == 0:
        test_case.input_string = form.input_string.data

    if (not test_case.output_string) or len(test_case.output_string) == 0:
        test_case.output_string = form.output_string.data

    test_case.is_inputfile = form.is_inputfile.data
    test_case.is_outputfile = form.is_outputfile.data
    
    test_case.save()


    return redirect(url_for('administration.challenges.view',
                            challenge_id=challenge.id))



@module.route('/<challenge_id>')
@acl.allows.requires(acl.is_lecturer)
def view(challenge_id):
    challenge = models.Challenge.objects.get(id=challenge_id)
    md = markdown.markdown(challenge.problem_statement,
            extensions=['fenced_code', 'codehilite'])

    formatter = HtmlFormatter(linenos=True)
    style = formatter.get_style_defs('.codehilite')

    return render_template('/administration/challenges/view.html',
                           markdown=markdown.markdown,
                           style=style,
                           challenge=challenge)
