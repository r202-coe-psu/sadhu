import mongoengine as me
import datetime


class Assignment(me.Document):
    name = me.StringField(required=True)
    description = me.StringField(required=True)
    score = me.IntField(required=True, default=0)
    tags = me.ListField(me.StringField(required=True))
    course = me.ReferenceField('Course',
                               dbref=True,
                               required=True)

    started_date = me.DateTimeField(required=True,
                                    default=datetime.datetime.utcnow)
    ended_date = me.DateTimeField(required=True,
                                  default=datetime.datetime.utcnow)

    created_date = me.DateTimeField(required=True,
                                    default=datetime.datetime.utcnow)
    updated_date = me.DateTimeField(required=True,
                                    default=datetime.datetime.utcnow,
                                    auto_now=True)

    questions = me.ListField(me.ReferenceField('Question', db_ref=True))

    owner = me.ReferenceField('User', db_ref=True, required=True)
    contributors = me.ListField(
            me.ReferenceField('User',
                              dbref=True,
                              required=True))

    meta = {'collection': 'assignments'}

