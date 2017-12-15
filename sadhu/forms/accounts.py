'''
Created on Oct 13, 2013

@author: boatkrap
'''
'''
Created on Jan 28, 2013

@author: boatkrap
'''

from wtforms import Form
from wtforms import fields
from wtforms import validators
from wtforms.fields import html5

from flask_wtf import FlaskForm

def validate_email(form, field):
#    user = models.User.objects(email=field.data).first()
    user = None
    if user is not None:
        raise validators.ValidationError(
            'This email: %s is available on system'% field.data)

def validate_username(form, field):

    if field.data.lower() in ['admin', 'administrator', 'lecturer', 'staff', 
                      'moderator', 'member', 'anonymous', 'pumbaa', 
                      'master', 'student', 'user', 'manager', 'coe',
                      'teacher', 'psu']:
        raise validators.ValidationError(
            'This username: %s is not allowed'% field.data)

    user = None
    # user = models.User.objects(username=field.data).first()

    # request = get_current_request()
    # request_user = request.user
    # if request_user == user:
    #     return
    
    if user is not None:
        raise validators.ValidationError(
            'This user: %s is available on system'% field.data)

def validate_display_name(form, field):

    if field.data.lower() in ['admin', 'administrator', 'lecturer', 'staff', 
                      'moderator', 'member', 'anonymous', 'pumbaa', 
                      'master', 'student', 'user', 'manager', 'coe',
                      'teacher', 'psu']:
        raise validators.ValidationError(
            'This display name: %s is not allowed'% field.data)

    user = models.User.objects(display_name=field.data).first()

    request = get_current_request()
    request_user = request.user
    if request_user == user:
        return
    
    if user is not None:
        raise validators.ValidationError(
            'This display name: %s is available on system'% field.data)
    

def validate_old_password(form, field):
    request = get_current_request()
    request_user = request.user
    
    if request_user.password != request.secret_manager.get_hash_password(field.data):
        raise validators.ValidationError(
            'Old password mismatch')

class LoginForm(FlaskForm): 
    name = fields.TextField('Username or Email', validators=[validators.InputRequired()])
    password = fields.PasswordField('Password', validators=[validators.InputRequired()])
    came_from = fields.HiddenField('Came Form')
    
class RegisterForm(FlaskForm):
    username = fields.TextField('Username',
            validators=[validators.InputRequired(), validators.Length(min=3), validate_username])
    email = html5.EmailField('Email', validators=[validators.InputRequired(), validators.Email(), validate_email])
    password = fields.PasswordField('Password', validators=[validators.InputRequired(), validators.Length(min=6), validators.EqualTo('password_conf', message="password mismatch")])
    password_conf = fields.PasswordField('Password Confirm', validators=[validators.InputRequired()])
    first_name = fields.TextField('First Name', validators=[validators.InputRequired()])
    last_name = fields.TextField('Last Name', validators=[validators.InputRequired()])
    agree_term = fields.BooleanField('Agree Term', validators=[validators.InputRequired()])
    
class PasswordForm(Form):
    old_password = fields.PasswordField('Old password', validators=[validators.InputRequired(), validators.Length(min=6), validate_old_password])
    password = fields.PasswordField('Password', validators=[validators.InputRequired(), validators.Length(min=6), validators.EqualTo('password_conf', message="password mismatch")])
    password_conf = fields.PasswordField('Password confirm', validators=[validators.InputRequired()])

class DisplayNameForm(Form):
    display_name = fields.TextField('Display Name', validators=[validators.InputRequired(), validate_display_name])
    first_name = fields.TextField('First Name', validators=[validators.InputRequired()])
    last_name = fields.TextField('Last Name', validators=[validators.InputRequired()])
