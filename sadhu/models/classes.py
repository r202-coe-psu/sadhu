import mongoengine as me
import datetime

class Enrollment(me.Document):
    user = me.ReferenceField('User', dbref=True, required=True)
    enrolled_class = me.ReferenceField('Class', dbref=True, required=True)
    enrolled_date = me.DateTimeField(required=True,
                                     default=datetime.datetime.now)
    
    meta = {'collection': 'enrollments'}



class LimitedEnrollment(me.EmbeddedDocument):
    method = me.StringField(required=True)
    grantees = me.ListField(me.StringField(required=True))
    updated_date = me.DateTimeField(required=True,
                                    auto_now=True,
                                    default=datetime.datetime.now)

class AssignmentTime(me.EmbeddedDocument):
    assignment = me.ReferenceField('Assignment', required=True)
    started_date = me.DateTimeField(required=True,
                                    default=datetime.datetime.now)
    ended_date = me.DateTimeField(required=True,
                                  default=datetime.datetime.now)
    updated_date = me.DateTimeField(required=True,
                                    auto_now=True,
                                    default=datetime.datetime.now)


class Class(me.Document):
    name = me.StringField(required=True)
    description = me.StringField(required=True)
    code = me.StringField()
    course = me.ReferenceField('Course', required=True)
    assignment_schedule = me.ListField(
            me.EmbeddedDocumentField(AssignmentTime))
    tags = me.ListField(me.StringField(required=True))

    created_date = me.DateTimeField(required=True,
                                    default=datetime.datetime.now)
    updated_date = me.DateTimeField(required=True,
                                    default=datetime.datetime.now,
                                    auto_now=True)

    limited = me.BooleanField(required=True, default=False)
    limited_enrollment = me.EmbeddedDocumentField(LimitedEnrollment)
    enrollments = me.ListField(me.ReferenceField('Enrollment', dbref=True))
    started_date = me.DateTimeField(required=True,
                                    default=datetime.datetime.now)

    ended_date = me.DateTimeField(required=True,
                                    default=datetime.datetime.now)

    owner = me.ReferenceField('User', dbref=True, required=True)
    teaching_assistant = me.ListField(
            me.ReferenceField('User', dbref=True, required=True))
    contributors = me.ListField(me.ReferenceField('User',
                                                  dbref=True,
                                                  required=True))

    meta = {'collection': 'classes'}

    def get_assignment_schedule(self, assignment):
        ass_time = None
        for ass in self.assignment_schedule:
            if ass.assignment == assignment:
                ass_time = ass
                break

        return ass_time
