from wtforms import Form
from wtforms import fields
from wtforms import validators
from wtforms import widgets

from flask_wtf import FlaskForm

class URIListField(fields.Field):
    widget = widgets.TextInput()

    def _value(self):
        if self.data:
            return ', '.join(self.data)
        else:
            return ''

    def process_formdata(self, valuelist):
        data = []
        if valuelist:
            data = [tag.strip() for tag in valuelist[0].split(',') if len(tag.strip()) > 0]
        self.data = data
        



class OAuthProjectForm(FlaskForm):
    name = fields.StringField('Name',
            validators=[validators.InputRequired(),
                        validators.Length(min=3)])
    description = fields.StringField('Description',
            validators=[validators.InputRequired()])
    confidential = fields.BooleanField(default=False)

    redirect_uris = URIListField('Redirect URIs',
            validators=[# validators.URL(),
                        validators.InputRequired()])

