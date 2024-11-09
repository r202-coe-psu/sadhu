from wtforms import Form
from wtforms import fields
from wtforms import validators
from wtforms import widgets

import datetime

from .fields import TagListField

from flask_wtf import FlaskForm
from sadhu import models


class AssignmentTimeForm(FlaskForm):
    started_date = fields.DateTimeField(
        "Started Date",
        format="%Y-%m-%d %H:%M",
        default=datetime.date.today,
        widget=widgets.TextInput(),
    )

    ended_date = fields.DateTimeField(
        "Ended Data",
        format="%Y-%m-%d %H:%M",
        default=datetime.date.today,
        widget=widgets.TextInput(),
    )


class ChallengeAddingForm(FlaskForm):
    challenges = fields.SelectMultipleField("Challenges")
    # randomLevel = fields.SelectField(
    #     "Random Level", choices=models.challenges.CHALLENGE_LEVEL
    # )
    random_count = fields.IntegerField(
        "number of challanges",
        validators=[validators.InputRequired(), validators.NumberRange(min=0)],
        default=0,
    )
    random_or_not = fields.SelectField(
        "Random or Not", choices=[("Random Choice"), ("Not Random Choice")]
    )


class AssignmentForm(FlaskForm):
    name = fields.StringField(
        "Name", validators=[validators.InputRequired(), validators.Length(min=3)]
    )
    description = fields.StringField(
        "Description",
        validators=[validators.InputRequired()],
        widget=widgets.TextArea(),
    )
    score = fields.IntegerField(
        "Score",
        validators=[validators.InputRequired(), validators.NumberRange(min=0)],
        default=0,
    )
    course = fields.SelectField(
        "Course",
    )
    #            validators=[validators.InputRequired()])
    tags = TagListField(
        "Tags", validators=[validators.InputRequired(), validators.Length(min=3)]
    )
    level = fields.SelectField("Level", choices=models.assignments.Assignment_level)
