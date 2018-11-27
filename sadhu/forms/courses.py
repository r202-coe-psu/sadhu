from wtforms import Form
from wtforms import fields
from wtforms import validators
from wtforms import widgets
from wtforms.fields import html5

from .fields import TagListField

from flask_wtf import FlaskForm


class CourseForm(FlaskForm):
    name = fields.StringField('Name',
            validators=[validators.InputRequired(),
                        validators.Length(min=3)])
    description = fields.StringField('Description',
            validators=[validators.InputRequired()],
            widget=widgets.TextArea())
    languages = fields.SelectMultipleField('Languages',
            validators=[validators.InputRequired()],
            )
    tags = TagListField('Tags',
            validators=[validators.InputRequired(),
                        validators.Length(min=3)])
