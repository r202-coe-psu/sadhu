from flask import Blueprint, render_template, url_for, redirect
from flask_login import current_user, login_required


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
@acl.roles_required("teaching_assistant")
def index():
    return render_template("/administration/solutions/view.html.j2")


@module.route("/<solution_id>")
@acl.roles_required("teaching_assistant")
def view(solution_id):
    solution = models.Solution.objects.get(id=solution_id)
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
@acl.roles_required("teaching_assistant")
def download_code(solution_id):
    solution = models.Solutuib.objects.get(id=solution_id)
    return render_template("/administration/solutions/code.html.j2", solution)
