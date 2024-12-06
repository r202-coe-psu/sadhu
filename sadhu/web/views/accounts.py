import datetime
import markdown
import mongoengine as me

from flask import (
    Blueprint,
    render_template,
    url_for,
    redirect,
    request,
    session,
    current_app,
    send_file,
    abort,
)
from flask_login import login_user, logout_user, login_required, current_user

from .. import models
from .. import oauth2
from .. import forms

module = Blueprint("accounts", __name__)


def get_user_and_remember():
    client = oauth2.oauth2_client
    result = client.principal.get("me")
    # print('got: ', result.json())
    data = result.json()

    user = models.User.objects(username=data.get("username", "")).first()
    if not user:
        user = models.User(
            id=data.get("id"),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            email=data.get("email"),
            username=data.get("username"),
            status="active",
        )
        roles = []
        for role in ["student", "lecturer", "staff"]:
            if role in data.get("roles", []):
                roles.append(role)

        user.save()

    if user:
        login_user(user, remember=True)


@module.route("/login", methods=("GET", "POST"))
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    if "next" in request.args:
        session["next"] = request.args.get("next", None)

    oauth_clients = current_app.extensions["authlib.integrations.flask_client"]._clients

    return render_template("/accounts/login.html", oauth_clients=oauth_clients)


@module.route("/login/<name>")
def login_oauth(name):
    client = oauth2.oauth2_client

    scheme = request.environ.get("HTTP_X_FORWARDED_PROTO", "http")
    redirect_uri = url_for(
        "accounts.authorized_oauth", name=name, _external=True, _scheme=scheme
    )
    response = None
    if name == "google":
        response = client.google.authorize_redirect(redirect_uri)
    elif name == "facebook":
        response = client.facebook.authorize_redirect(redirect_uri)
    elif name == "line":
        response = client.line.authorize_redirect(redirect_uri)

    elif name == "psu":
        response = client.psu.authorize_redirect(redirect_uri)
    elif name == "engpsu":
        response = client.engpsu.authorize_redirect(redirect_uri)
    return response


@module.route("/auth/<name>")
def authorized_oauth(name):
    client = oauth2.oauth2_client
    remote = None
    try:
        if name == "google":
            remote = client.google
        elif name == "facebook":
            remote = client.facebook
        elif name == "line":
            remote = client.line
        elif name == "psu":
            remote = client.psu
        elif name == "engpsu":
            remote = client.engpsu

        token = remote.authorize_access_token()

    except Exception as e:
        print("autorize access error =>", e)
        return redirect(url_for("accounts.login"))

    session["oauth_provider"] = name
    return oauth2.handle_authorized_oauth2(remote, token)


@module.route("/logout")
@login_required
def logout():
    name = session.get("oauth_provider")
    logout_user()
    session.clear()

    client = oauth2.oauth2_client
    remote = None
    logout_url = None
    if name == "google":
        remote = client.google
        logout_url = f"https://accounts.google.com/Logout?redirect={ request.scheme }://{ request.host }"
    elif name == "facebook":
        remote = client.facebook
    elif name == "line":
        remote = client.line
    elif name == "psu":
        remote = client.psu
        logout_url = f"{ remote.server_metadata.get('end_session_endpoint') }"
    elif name == "engpsu":
        remote = client.engpsu

    if logout_url:
        return redirect(logout_url)

    return redirect(url_for("site.index"))


@module.route("/accounts/<user_id>")
def profile(user_id):
    user = models.User.objects.get(id=user_id)

    biography = ""
    if user.biography:
        biography = markdown.markdown(user.biography)
    return render_template("/accounts/index.html", user=user, biography=biography)


@module.route("/accounts")
@login_required
def index():
    return render_template("/accounts/index.html", user=current_user)


@module.route("/accounts/edit-profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = forms.accounts.ProfileForm(
        obj=current_user,
    )
    if not form.validate_on_submit():
        return render_template("/accounts/edit-profile.html", form=form)

    user = current_user._get_current_object()
    form.populate_obj(user)

    # if form.pic.data:
    #     if user.picture:
    #         user.picture.replace(
    #             form.pic.data,
    #             filename=form.pic.data.filename,
    #             content_type=form.pic.data.content_type,
    #         )
    #     else:
    #         user.picture.put(
    #             form.pic.data,
    #             filename=form.pic.data.filename,
    #             content_type=form.pic.data.content_type,
    #         )
    user.metadata["thai_first_name"] = form.thai_first_name.data
    user.metadata["thai_last_name"] = form.thai_last_name.data
    user.metadata["student_id"] = form.student_id.data
    user.metadata["organization"] = form.organization.data

    user.updated_date = datetime.datetime.now()
    user.save()

    return redirect(url_for("accounts.index"))


@module.route("/accounts/<user_id>/picture/<filename>", methods=["GET", "POST"])
def picture(user_id, filename):
    user = models.User.objects.get(id=user_id)

    if not user or not user.picture or user.picture.filename != filename:
        return abort(403)

    response = send_file(
        user.picture,
        attachment_filename=user.picture.filename,
        mimetype=user.picture.content_type,
    )
    return response
