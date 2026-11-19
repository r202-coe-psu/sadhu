from flask import Blueprint, render_template, url_for, redirect
from flask_login import current_user, login_required
from werkzeug.exceptions import Forbidden


from pygments.lexers import get_lexer_for_filename, get_lexer_by_name
from pygments import highlight
from pygments.formatters import HtmlFormatter

import difflib

from sadhu.web import acl, forms
from sadhu import models

module = Blueprint(
    "solutions",
    __name__,
    url_prefix="/solutions",
)


@module.route("/")
@acl.teaching_assistant_required
def index():
    return render_template("/administration/solutions/view.html.j2")


@module.route("/<solution_id>")
@acl.teaching_assistant_required
def view(solution_id):
    solution = models.Solution.objects.get(id=solution_id)
    # Only TAs of the class the solution was submitted in may view it.
    if not solution.enrolled_class.is_teaching_assistant(
        current_user._get_current_object()
    ):
        raise Forbidden()

    code = solution.code.read().decode()

    lexer = get_lexer_for_filename(solution.code.filename)

    formatter = HtmlFormatter(linenos=True)
    formated_code = highlight(code, lexer, formatter)
    style = formatter.get_style_defs(".highlight")

    console_lexer = get_lexer_by_name("console")
    return render_template(
        "/administration/solutions/view.html.j2",
        solution=solution,
        formated_code=formated_code,
        console_lexer=console_lexer,
        formatter=formatter,
        highlight=highlight,
        difflib=difflib,
        style=style,
    )


@module.route("/<solution_id>/code")
@acl.teaching_assistant_required
def download_code(solution_id):
    solution = models.Solutuib.objects.get(id=solution_id)
    return render_template("/administration/solutions/code.html.j2", solution)
