from flask import g, config, session
from flask_login import current_user
from authlib.flask.client import OAuth

from . import models

def fetch_token(name):
    token = models.OAuth2Token.objects(name=name,
            user=current_user._get_current_object()).first()
    return token.to_dict()

def update_token(name, token):
    item = models.OAuth2Token(name=name, user_id=current_user.id).first()
    item.token_type = token.get('token_type', 'bearer')
    item.access_token = token.get('access_token')
    item.alt_token = token.get('refresh_token')
    item.expires_at = token.get('expires_at')
    
    item.save()
    return item


oauth2_client = OAuth()

def init_oauth(app):
    oauth2_client.init_app(app,
                           fetch_token=fetch_token,
                           update_token=update_token)

    principal_settings = app.config.get('AUTHLIB_CLIENT_PRINCIPAL')
    
    oauth2_client.register(
        principal_settings['name'],
        client_key=principal_settings['client_key'],
        client_secret=principal_settings['client_secret'],
        request_token_url=principal_settings['request_token_url'],
        request_token_params=principal_settings['request_token_params'],
        access_token_url=principal_settings['access_token_url'],
        access_token_params=principal_settings['access_token_params'],
        refresh_token_url=principal_settings['refresh_token_url'],
        authorize_url=principal_settings['authorize_url'],
        api_base_url=principal_settings['api_base_url'],
        client_kwargs=principal_settings['client_kwargs']
    )
