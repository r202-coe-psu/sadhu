from wtforms import Form
from wtforms import fields
from wtforms import validators
from wtforms import widgets

from .fields import TagListField

from flask_wtf import FlaskForm, file


class TestCaseForm(FlaskForm):
    input_string = fields.TextAreaField('Input Text')
    input_file = fields.FileField('Input File')
    is_inputfile = fields.BooleanField('Is Input File', default=False)
    
    output_string = fields.TextAreaField('Output Text')
    output_file = fields.FileField('Output File')
    is_outputfile = fields.BooleanField('Is Output File', default=False)

    public = fields.BooleanField('Public', default=False)


class Solution(FlaskForm):
    code = file.FileField('File',
            validators=[file.FileRequired()]
            )

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
