import mongoengine as me
import datetime

from flask_login import UserMixin


class User(me.Document, UserMixin):
    username = me.StringField(required=True, unique=True)

    email = me.StringField()
    first_name = me.StringField(required=True)
    last_name = me.StringField(required=True)

    status = me.StringField(required=True, default='disactive')
    roles = me.ListField(me.StringField(), default=['user'])

    created_date = me.DateTimeField(required=True,
                                    default=datetime.datetime.now)
    updated_date = me.DateTimeField(required=True,
                                    default=datetime.datetime.now,
                                    auto_now=True)

    resources = me.DictField()

    meta = {'collection': 'users'}

    def has_roles(self, roles):
        for role in roles:
            if role in self.roles:
                return True
        return False
