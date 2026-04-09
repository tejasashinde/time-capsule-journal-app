from functools import wraps

from flask import Blueprint, current_app, flash, redirect, session, url_for

from .models import create_or_update_user, get_user_by_id
from .oauth import oauth


auth_bp = Blueprint("auth", __name__)


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("main.index"))
        return view(*args, **kwargs)

    return wrapped_view


def current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return get_user_by_id(user_id)


@auth_bp.route("/login")
@auth_bp.route("/login/google")
def login():
    if not current_app.config["GOOGLE_CLIENT_ID"] or not current_app.config["GOOGLE_CLIENT_SECRET"]:
        flash("Google OAuth is not configured yet. Add GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET.", "error")
        return redirect(url_for("main.index"))

    redirect_uri = url_for("auth.authorize", _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@auth_bp.route("/login/google/authorized")
def authorize():
    token = oauth.google.authorize_access_token()
    user_info = token.get("userinfo")
    if not user_info:
        user_info = oauth.google.userinfo()

    user = create_or_update_user(
        google_sub=user_info["sub"],
        email=user_info["email"],
        name=user_info.get("name", user_info["email"]),
    )
    session.clear()
    session["user_id"] = user.id
    return redirect(url_for("main.dashboard"))


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("main.index"))
