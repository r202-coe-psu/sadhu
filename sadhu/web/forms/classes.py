from wtforms import Form
from wtforms import fields
from wtforms import validators
from wtforms import widgets
from flask_mongoengine.wtf import model_form

from flask_wtf import FlaskForm

from .fields import TagListField, TextListField

from .. import models


class TeachingAssistantAddingForm(FlaskForm):
    users = fields.SelectMultipleField("Users")


class LimitedEnrollmentForm(Form):
    method = fields.SelectField("Method", validators=[validators.InputRequired()])
    grantees = TextListField(
        "Grantees", validators=[validators.InputRequired(), validators.Length(min=1)]
    )
    # grantees = fields.StringField('Grantees',
    #         widget=widgets.TextArea())


BaseClassForm = model_form(
    models.Class,
    FlaskForm,
    exclude=["created_date", "updated_date", "owner"],
    field_args=dict(
        name=dict(label="Name"),
        description=dict(label="Description"),
        code=dict(label="Code"),
        course=dict(label="Course", label_modifier=lambda c: c.name),
        limited=dict(label="Limited Class"),
        # limited_enrollment=dict(label="Limited Enrollment"),
        started_date=dict(label="Started Date", format="%Y-%m-%d"),
        ended_date=dict(label="Ended Date", format="%Y-%m-%d"),
    ),
)


class ClassForm(BaseClassForm):
    limited_enrollment = fields.FormField(LimitedEnrollmentForm)
    tags = TagListField(
        "Tags", validators=[validators.InputRequired(), validators.Length(min=3)]
    )
