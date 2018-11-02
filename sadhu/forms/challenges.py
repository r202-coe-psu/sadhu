from wtforms import Form
from wtforms import fields
from wtforms import validators
from wtforms import widgets
from wtforms.fields import html5

from .fields import TagListField

from flask_wtf import FlaskForm


class TestCase(Form):
    input = fields.FileField()
    output = fields.FileField()

class TestCase(FlaskForm):
    test_cases = fields.FieldList(fields.FormField(TestCase))

class ChallengeForm(FlaskForm):
    name = fields.StringField('Name',
            validators=[validators.InputRequired(),
                        validators.Length(min=3)])
    description = fields.StringField('Description',
            validators=[validators.InputRequired()])
    problem_statement = fields.StringField('Problem Statement',
            validators=[validators.InputRequired()],
            widget=widgets.TextArea())
    input_format = fields.StringField('Input Format',
            widget=widgets.TextArea())
    constraints = fields.StringField('Constraints',
            widget=widgets.TextArea())
    output_format = fields.StringField('Output Format',
            validators=[validators.InputRequired()],
            widget=widgets.TextArea())

    score = fields.IntegerField('Score',
            validators=[validators.InputRequired(),
                validators.NumberRange(min=0)],
            default=0)
    tags = TagListField('Tags',
            validators=[validators.InputRequired(),
                        validators.Length(min=3)])
