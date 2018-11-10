import mongoengine as me
import datetime


class Course(me.Document):
    name = me.StringField(required=True)
    description = me.StringField(required=True)
    tags = me.ListField(me.StringField(required=True))

    created_date = me.DateTimeField(required=True,
                                    default=datetime.datetime.now)
    updated_date = me.DateTimeField(required=True,
                                    default=datetime.datetime.now,
                                    auto_now=True)

    assignments = me.ListField(
            me.ReferenceField('Assignment', dbref=True, requiree=True))

    owner = me.ReferenceField('User', dbref=True, required=True)
    contributors = me.ListField(me.ReferenceField('User',
                                                  dbref=True,
                                                  required=True))

    meta = {'collection': 'courses'}

