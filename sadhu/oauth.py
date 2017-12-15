from flask import g, config, session
from flask_oauthlib.client import OAuth

principal_remote = None

def init_oauth(app):
    global principal_remote
    oauth = OAuth(app)

    principal_setting = app.config.get('OAUTH2_REMOTE_PRINCIPAL')
    
    remote = oauth.remote_app(
        principal_setting['name'],
        consumer_key=principal_setting['consumer_key'],
        consumer_secret=principal_setting['consumer_secret'],
        request_token_params=principal_setting['request_token_params'],
        base_url=principal_setting['base_url'],
        request_token_url=principal_setting['request_token_url'],
        access_token_method=principal_setting['access_token_method'],
        access_token_url=principal_setting['access_token_url'],
        authorize_url=principal_setting['authorize_url']
    )

    @remote.tokengetter
    def get_oauth_token():
        tokens = session.get('principal-tokens')
        return tokens.get('access_token'), ''

    principal_remote = remote

def get_remote():
    return principal_remote

