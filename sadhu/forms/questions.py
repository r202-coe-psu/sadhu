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

class QuestionForm(FlaskForm):
    name = fields.StringField('Name',
            validators=[validators.InputRequired(),
                        validators.Length(min=3)])
    description = fields.StringField('Description',
            validators=[validators.InputRequired()],
            widget=widgets.TextArea())
    score = fields.IntegerField('Score',
            validators=[validators.InputRequired(),
                validators.NumberRange(min=0)],
            default=0)
    tags = TagListField('Tags',
            validators=[validators.InputRequired(),
                        validators.Length(min=3)])
