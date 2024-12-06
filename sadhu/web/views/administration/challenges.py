from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import current_user, login_required

import datetime
import markdown
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_for_filename, get_lexer_by_name
from pygments import highlight

from sadhu.web import acl, forms
from sadhu import models


module = Blueprint(
    "challenges",
    __name__,
    url_prefix="/challenges",
)


@module.route("/")
# @acl.allows.requires(acl.is_lecturer)
@login_required
def index():
    challenges = models.Challenge.objects(
        owner=current_user._get_current_object()
    ).order_by("name")

    other_challenges = models.Challenge.objects(
        owner__ne=current_user._get_current_object()
    ).order_by("name")

    # print('q', challenges)
    return render_template(
        "/administration/challenges/index.html",
        challenges=challenges,
        other_challenges=other_challenges,
    )


@module.route("/create", methods=["GET", "POST"])
# @acl.allows.requires(acl.is_lecturer)
@login_required
def create():
    form = forms.challenges.ChallengeForm(request.form)
    print(form.data)
    if not form.validate_on_submit():
        return render_template("/administration/challenges/create-edit.html", form=form)
    data = form.data.copy()
    data.pop("csrf_token")
    challenge = models.Challenge(**data)
    challenge.owner = current_user._get_current_object()
    challenge.save()

    return redirect(
        url_for("administration.challenges.view", challenge_id=challenge.id)
    )


@module.route("/<challenge_id>/edit", methods=["GET", "POST"])
# @acl.allows.requires(acl.is_lecturer)
@login_required
def edit(challenge_id):
    challenge = models.Challenge.objects.get(id=challenge_id)

    form = forms.challenges.ChallengeForm(obj=challenge)
    if not form.validate_on_submit():
        return render_template("/administration/challenges/create-edit.html", form=form)
    data = form.data.copy()
    data.pop("csrf_token")
    form.populate_obj(challenge)
    challenge.save()

    return redirect(
        url_for("administration.challenges.view", challenge_id=challenge.id)
    )


@module.route("/<challenge_id>")
# @acl.allows.requires(acl.is_lecturer)
@login_required
def view(challenge_id):
    challenge = models.Challenge.objects.get(id=challenge_id)
    formatter = HtmlFormatter(linenos=True)
    console_formatter = HtmlFormatter(
        style="monokai", prestyles="white-space: pre-wrap;"
    )
    console_lexer = get_lexer_by_name("console")
    style = formatter.get_style_defs(".codehilite")

    code_for_testcase = models.Solution.objects(
        challenge=challenge,
        type="challenge",
    ).first()
    return render_template(
        "/administration/challenges/view.html",
        markdown=markdown.markdown,
        style=style,
        formatter=formatter,
        console_formatter=console_formatter,
        challenge=challenge,
        console_lexer=console_lexer,
        highlight=highlight,
        code_for_testcase=code_for_testcase,
    )


@module.route("/<challenge_id>/add-testcase", methods=["GET", "POST"])
# @acl.allows.requires(acl.is_lecturer)
@login_required
def add_testcase(challenge_id):
    challenge = models.Challenge.objects.get(id=challenge_id)
    form = forms.challenges.TestCaseForm()

    if not form.validate_on_submit():
        return render_template(
            "/administration/challenges/add-testcase.html",
            form=form,
            challenge=challenge,
        )

    test_case = models.TestCase(
        public=form.public.data,
        owner=current_user._get_current_object(),
        challenge=challenge,
    )

    if form.input_file.data:
        if form.is_inputfile.data:
            test_case.input_file.put(
                form.input_file.data,
                filename=form.input_file.data.filename,
                content_type=form.input_file.data.content_type,
            )
        else:
            data = form.input_file.data.read()
            test_case.input_string = data.replace("\r", "")

    if form.output_file.data:
        if form.is_outputfile.data:
            test_case.output_file.put(
                form.output_file.data,
                filename=form.output_file.data.filename,
                content_type=form.output_file.data.content_type,
            )
        else:
            test_case.output_string = form.output_file.data.read()

    if (not test_case.input_string) or len(test_case.input_string) == 0:
        test_case.input_string = form.input_string.data.replace("\r", "")

    if (not test_case.output_string) or len(test_case.output_string) == 0:
        test_case.output_string = form.output_string.data

    test_case.is_inputfile = form.is_inputfile.data
    test_case.is_outputfile = form.is_outputfile.data
    test_case.save()

    challenge.test_cases.append(test_case)
    challenge.save()

    return redirect(
        url_for("administration.challenges.view", challenge_id=challenge.id)
    )


@module.route("/<challenge_id>/testcases/<testcase_id>/edit", methods=["GET", "POST"])
# @acl.allows.requires(acl.is_lecturer)
@login_required
def edit_testcase(challenge_id, testcase_id):
    challenge = models.Challenge.objects.get(id=challenge_id)
    test_case = models.TestCase.objects.get(id=testcase_id)
    form = forms.challenges.TestCaseForm(obj=test_case)

    if not form.validate_on_submit():
        return render_template(
            "/administration/challenges/add-testcase.html",
            form=form,
            challenge=challenge,
        )

    data = form.data.copy()
    data.pop("input_file")
    data.pop("output_file")
    data.pop("csrf_token")

    test_case.update(**data)
    test_case.input_string = test_case.input_string.replace("\r", "")

    if form.input_file.data:

        if form.is_inputfile.data:
            test_case.input_file.put(
                form.input_file.data,
                filename=form.input_file.data.filename,
                content_type=form.input_file.data.content_type,
            )
        else:
            data = form.input_file.data.read()
            test_case.input_string = data.replace("\r", "")

    if form.output_file.data:
        if form.is_outputfile.data:
            test_case.output_file.put(
                form.output_file.data,
                filename=form.output_file.data.filename,
                content_type=form.output_file.data.content_type,
            )
        else:
            test_case.output_string = form.output_file.data.read()

    if (not test_case.input_string) or len(test_case.input_string) == 0:
        test_case.input_string = form.input_string.data

    if (not test_case.output_string) or len(test_case.output_string) == 0:
        test_case.output_string = form.output_string.data

    test_case.is_inputfile = form.is_inputfile.data
    test_case.is_outputfile = form.is_outputfile.data
    test_case.save()

    return redirect(
        url_for("administration.challenges.view", challenge_id=challenge.id)
    )


@module.route("/<challenge_id>/testcases/<testcase_id>/delete")
# @acl.allows.requires(acl.is_lecturer)
@login_required
def delete_testcase(challenge_id, testcase_id):
    challenge = models.Challenge.objects.get(id=challenge_id)
    test_case = models.TestCase.objects.get(id=testcase_id)
    if test_case.input_file:
        test_case.input_file.delete()

    if test_case.output_file:
        test_case.output_file.delete()

    challenge.test_cases.remove(test_case)
    test_case.delete()
    challenge.save()

    return redirect(
        url_for("administration.challenges.view", challenge_id=challenge.id)
    )


@module.route("/<challenge_id>/add-code-for-testcase", methods=["GET", "POST"])
# @acl.allows.requires(acl.is_lecturer)
@login_required
def add_code_for_testcase(challenge_id):
    challenge = models.Challenge.objects.get(id=challenge_id)
    form = forms.challenges.CodeForTestCaseForm()
    form.language.choices = models.courses.LANGUAGE_CHOICES

    if not form.validate_on_submit():
        return render_template(
            "/administration/challenges/add-code-for-testcase.html",
            form=form,
            challenge=challenge,
        )
    solution = models.Solution.objects(
        challenge=challenge,
        type="challenge",
    ).first()

    if not solution:
        solution = models.Solution(
            owner=current_user._get_current_object(),
            challenge=challenge,
            language=form.language.data,
            type="challenge",
        )

        solution.code.put(
            form.code.data,
            filename=form.code.data.filename,
            content_type=form.code.data.content_type,
        )
    else:
        solution.owner = current_user._get_current_object()
        solution.language = form.language.data
        solution.code.replace(
            form.code.data,
            filename=form.code.data.filename,
            content_type=form.code.data.content_type,
        )
        solution.status = "waiting"

    solution.save()

    return redirect(
        url_for("administration.challenges.view", challenge_id=challenge.id)
    )


@module.route("/<challenge_id>/rerun-code-for-testcase", methods=["GET", "POST"])
# @acl.allows.requires(acl.is_lecturer)
@login_required
def rerun_code_for_testcase(challenge_id):
    challenge = models.Challenge.objects.get(id=challenge_id)
    solution = models.Solution.objects(
        challenge=challenge,
        type="challenge",
    ).first()

    if solution:
        solution.status = "waiting"
        solution.updated_date = datetime.datetime.now()

        solution.save()

    return redirect(
        url_for("administration.challenges.view", challenge_id=challenge.id)
    )


@module.route("/<challenge_id>/solutions")
# @acl.allows.requires(acl.is_lecturer)
@login_required
def list_solutions(challenge_id):
    challenge = models.Challenge.objects.get(id=challenge_id)
    solutions = models.Solution.objects(challenge=challenge).order_by("-id").limit(50)

    return render_template(
        "/administration/challenges/list-solutions.html",
        challenge=challenge,
        solutions=solutions,
    )
