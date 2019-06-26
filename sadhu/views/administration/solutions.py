from flask import (Blueprint,
                   render_template,
                   url_for,
                   redirect
                   )
from flask_login import current_user


from pygments.lexers import get_lexer_for_filename, get_lexer_by_name
from pygments import highlight
from pygments.formatters import HtmlFormatter

import difflib

from sadhu import acl
from sadhu import forms
from sadhu import models

module = Blueprint('administration.solutions',
                   __name__,
                   url_prefix='/solutions',
                   )


@module.route('/')
@acl.allows.requires(acl.is_lecturer)
def index():
    solutions = models.Solution.objects().order_by('-id').limit(50)
    return render_template('/administration/solutions/index.html',
                           solutions=solutions)


@module.route('/<solution_id>')
@acl.allows.requires(acl.is_lecturer)
def view(solution_id):
    solution = models.Solution.objects.get(id=solution_id)
    code = solution.code.read().decode(errors='ignore')

    lexer = get_lexer_for_filename(solution.code.filename)

    formatter = HtmlFormatter(linenos=True)
    formated_code = highlight(code, lexer, formatter)
    style = formatter.get_style_defs('.highlight')

    console_lexer = get_lexer_by_name("console")
    return render_template('/administration/solutions/view.html',
                           solution=solution,
                           formated_code=formated_code,
                           console_lexer=console_lexer,
                           formatter=formatter,
                           highlight=highlight,
                           difflib=difflib,
                           style=style)


@module.route('/<solution_id>/code')
@acl.allows.requires(acl.is_lecturer)
def download_code(solution_id):
    solution = models.Solutuib.objects.get(id=solution_id)
    return render_template('/administration/solutions/code.html',
                           solution)
