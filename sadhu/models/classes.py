import mongoengine as me
import datetime

class Enrollment(me.Document):
    users = me.ReferenceField('User', dbref=True)
    enrolled_class = me.ReferenceField('Class', dbref=True)
    enrolled_date = me.DateTimeField(required=True,
                                     default=datetime.datetime.utcnow)
    
    meta = {'collection': 'enrollments'}


class LimitedEnrollment(me.EmbeddedDocument):
    method = me.StringField(required=True)
    grantees = me.ListField(me.StringField(required=True))
    updated_date = me.DateTimeField(required=True,
                                    auto_now=True,
                                    default=datetime.datetime.utcnow)

class Class(me.Document):
    name = me.StringField(required=True)
    description = me.StringField(required=True)
    code = me.StringField()
    course = me.ReferenceField('Course', required=True)
    tags = me.ListField(me.StringField(required=True))

    created_date = me.DateTimeField(required=True,
                                    default=datetime.datetime.utcnow)
    updated_date = me.DateTimeField(required=True,
                                    default=datetime.datetime.utcnow,
                                    auto_now=True)

    limited = me.BooleanField(required=True, default=False)
    limited_enrollment = me.EmbeddedDocumentField(LimitedEnrollment)
    enrollments = me.ListField(me.ReferenceField('Enrollment', dbref=True))
    started_date = me.DateTimeField(required=True,
                                    default=datetime.datetime.utcnow)

    ended_date = me.DateTimeField(required=True,
                                    default=datetime.datetime.utcnow)

    owner = me.ReferenceField('User', dbref=True, required=True)
    teaching_assistant = me.ListField(
            me.ReferenceField('User', dbref=True, required=True))
    contributors = me.ListField(me.ReferenceField('User',
                                                  dbref=True,
                                                  required=True))

    meta = {'collection': 'classes'}

