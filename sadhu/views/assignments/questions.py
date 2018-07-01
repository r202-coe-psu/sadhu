from flask import Blueprint, render_template

from sadhu import acl
from sadhu import forms

module = Blueprint('assignments.questions',
                   __name__,
                   url_prefix='/questions',
                   )


@module.route('/')
@acl.allows.requires(acl.is_lecturer)
def index():
    return render_template('/assignments/questions/index.html')


@module.route('/create')
def create():
    form = forms.questions.QuestionForm()
    if not form.validate():
        return render_template('/assignments/questions/create.html',
                               form=form)

    return redirect(url_for('assignments.questions.view'))


@module.route('/<id>/view')
def view():
    return render_template('/assignments/questions/view.html')
