import mongoengine as me
import datetime

from .users import User

class Solution(me.Document):
    code = me.FileField(required=True)
    output = me.StringField()
    messages = me.StringField()
    status = me.StringField(required=True, default='waiting')
    enrolled_class = me.ReferenceField('Class',
                                       required=True,
                                       dbref=True)
    challenge = me.ReferenceField('Challenge',
                                  required=True,
                                  dbref=True)
    user = me.ReferenceField('User',
                             required=True,
                             dbref=True)

    submitted_date = me.DateTimeField(required=True,
                                      default=datetime.datetime.now)

    executed_date = me.DateTimeField()
    meta = {'collection': 'solutions'}

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
                                    default=datetime.datetime.now)
    updated_date = me.DateTimeField(required=True,
                                    default=datetime.datetime.now,
                                    auto_now=True)

    owner = me.ReferenceField('User', dbref=True, required=True)
    contributors = me.ListField(
            me.ReferenceField('User',
                              dbref=True,
                              required=True))

    meta = {'collection': 'challenges'}

    def get_solutions(self):
        return Solution.objects(challenge=self).first()
