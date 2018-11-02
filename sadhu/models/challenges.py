import mongoengine as me
import datetime

from .users import User


class Challenge(me.Document):
    name = me.StringField(required=True)
    description = me.StringField(required=True)
    problem_statement = me.StringField(required=True)
    input_format = me.StringField()
    output_format = me.StringField()
    constraints = me.StringField(required=True)

    score = me.IntField(required=True, default=0)
    tags = me.ListField(me.StringField(required=True))

    created_date = me.DateTimeField(required=True,
                                    default=datetime.datetime.utcnow)
    updated_date = me.DateTimeField(required=True,
                                    default=datetime.datetime.utcnow,
                                    auto_now=True)

    owner = me.ReferenceField('User', dbref=True, required=True)
    contributors = me.ListField(
            me.ReferenceField('User',
                              dbref=True,
                              required=True))

    meta = {'collection': 'challenges'}

