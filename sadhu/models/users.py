import mongoengine as me
import datetime

from passlib.hash import bcrypt
from flask_login import UserMixin

class DataSource(me.EmbeddedDocument):
    provider = me.StringField(required=True)
    data = me.DictField()

    created_date = me.DateTimeField(required=True,
                                    default=datetime.datetime.utcnow)
    updated_date = me.DateTimeField(required=True,
                                    default=datetime.datetime.utcnow,
                                    auto_now=True)


class User(me.Document, UserMixin):
    username = me.StringField(required=True, unique=True)
    password = me.StringField()

    email = me.StringField()
    first_name = me.StringField(required=True)
    last_name = me.StringField(required=True)

    status = me.StringField(required=True, default='disactive')
    roles = me.ListField(me.StringField(), default=['user'])

    created_date = me.DateTimeField(required=True,
                                    default=datetime.datetime.utcnow)
    updated_date = me.DateTimeField(required=True,
                                    default=datetime.datetime.utcnow,
                                    auto_now=True)

    data_sources = me.EmbeddedDocumentListField(DataSource)
    meta = {'collection': 'users'}

    def __get_salt(self, salt):
        token = salt.replace(' ', '.')
        return '{:.<22.22}'.format(token)

    def set_password(self, password, salt=''):
        self.password = bcrypt.using(rounds=16).hash(
            password,
            salt=self.__get_salt(salt))

    def verify_password(self, password, salt=''):
        return bcrypt.verify(password,
                             self.password)

    def has_roles(self, roles):
        for role in roles:
            if role in self.roles:
                return True
        return False
