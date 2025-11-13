from flask import Blueprint, render_template, request, redirect, jsonify, url_for
from flask_login import current_user, login_required

from pygments.lexers import get_lexer_for_filename, get_lexer_by_name
from pygments import highlight
from pygments.formatters import HtmlFormatter

import difflib

from .. import acl
from .. import forms
from sadhu import models


module = Blueprint(
    "solutions",
    __name__,
    url_prefix="/solutions",
)


@module.route("/")
@login_required
def index():
    solutions = models.Solution.objects(
        owner=current_user._get_current_object()
    ).order_by("-id")
    return render_template(
        "/solutions/index.html.j2",
        solutions=solutions,
    )


@module.route("/<solution_id>/")
# @acl.allows.requires(acl.is_solution_owner)
@login_required
def view(solution_id):
    solution = models.Solution.objects(
        id=solution_id,
        owner=current_user._get_current_object(),
    ).first()
    challenge = solution.challenge

    code = solution.code.read().decode(errors="ignore")

    lexer = get_lexer_for_filename(solution.code.filename)

    formatter = HtmlFormatter(linenos=True)
    formated_code = highlight(code, lexer, formatter)
    style = formatter.get_style_defs(".highlight")

    console_lexer = get_lexer_by_name("console")
    return render_template(
        "/administration/solutions/view.html.j2",
        solution=solution,
        challenge=challenge,
        formated_code=formated_code,
        console_lexer=console_lexer,
        formatter=formatter,
        highlight=highlight,
        difflib=difflib,
        style=style,
    )


@module.route("/<solution_id>/status")
# @acl.allows.requires(acl.is_solution_owner
#                      or acl.is_lecturer
#                      or acl.is_teaching_assistant)
@login_required
def status_api(solution_id):
    solution = models.Solution.objects(
        id=solution_id,
        owner=current_user._get_current_object(),
    ).first()
    data = dict(
        id=solution_id,
        status=solution.status,
        score=solution.score,
        passed=solution.passed,
    )
    return jsonify(data)
