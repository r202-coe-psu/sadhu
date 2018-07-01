from wtforms import Form
from wtforms import fields
from wtforms import validators
from wtforms import widgets
from wtforms.fields import html5

from flask_wtf import FlaskForm


class TestCase(Form):
    input = fields.FileField()
    output = fields.FileField()

class TestCase(FlaskForm):
    test_cases = fields.FieldList(fields.FormField(TestCase))

class QuestionForm(FlaskForm):
    name = fields.TextField('Name',
            validators=[validators.InputRequired(),
                        validators.Length(min=3)])
    description = fields.TextField('Description',
            validators=[validators.InputRequired()])
    tags = fields.FieldList(fields.StringField(
            validators=[validators.InputRequired(),
                        validators.Length(min=3)]))
