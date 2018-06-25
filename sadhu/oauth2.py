from flask import g, config, session
from flask_login import current_user
from authlib.flask.client import OAuth

from . import models

def fetch_token(name):
    token = models.OAuth2Token.objects(name=name,
            user=current_user._get_current_object()).first()
    return token.to_dict()

def update_token(name, token):
    item = models.OAuth2Token(name=name, user=current_user._get_current_object()).first()
    item.token_type = token.get('token_type', 'Bearer')
    item.access_token = token.get('access_token')
    item.refresh_token = token.get('refresh_token')
    item.expires = datetime.datetime.utcfromtimestamp(token.get('expires_at'))
    
    item.save()
    return item


oauth2_client = OAuth()

def init_oauth(app):
    oauth2_client.init_app(app,
                           fetch_token=fetch_token,
                           update_token=update_token)
    
    oauth2_client.register('principal')
    oauth2_client.register('engpsu')
