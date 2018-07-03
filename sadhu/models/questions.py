import mongoengine as me
import datetime

from .users import User


class Question(me.Document):
    name = me.StringField(required=True)
    description = me.StringField(required=True)
    score = me.IntField(required=True, default=0)
    tags = me.ListField(me.StringField(required=True))

    created_date = me.DateTimeField(required=True,
                                    default=datetime.datetime.utcnow)
    updated_date = me.DateTimeField(required=True,
                                    default=datetime.datetime.utcnow,
                                    auto_now=True)

    owner = me.ReferenceField(User, required=True)
    contributors = me.ListField(me.ReferenceField(User))

    meta = {'collection': 'questions'}

