from . import users
from . import oauth2
from . import challenges
from . import courses
from . import classes
from . import assignments

from .users import User
from .oauth2 import OAuth2Token
from .challenges import (Challenge,
                         Solution,
                         TestCase,
                         TestResult,
                         ChallengeStatus)
from .courses import Course, LANGUAGE_CHOICES
from .classes import (Class,
                      Enrollment,
                      LimitedEnrollment,
                      AssignmentTime,
                      TeachingAssistant)
from .assignments import Assignment

__all__ = [users,
           User,
           oauth2,
           OAuth2Token,
           challenges,
           Challenge, Solution,
           TestCase, TestResult, ChallengeStatus,
           courses,
           Course, LANGUAGE_CHOICES,
           classes,
           Class, Enrollment, LimitedEnrollment, AssignmentTime,
           TeachingAssistant,
           assignments,
           Assignment
           ]


from flask_mongoengine import MongoEngine

db = MongoEngine()


def init_db(app):
    db.init_app(app)


def init_mongoengine(settings):
    import mongoengine as me
    dbname = settings.get('MONGODB_DB')
    host = settings.get('MONGODB_HOST', 'localhost')
    port = int(settings.get('MONGODB_PORT', '27017'))
    username = settings.get('MONGODB_USERNAME', '')
    password = settings.get('MONGODB_PASSWORD', '')

    me.connect(db=dbname,
               host=host,
               port=port,
               username=username,
               password=password)

