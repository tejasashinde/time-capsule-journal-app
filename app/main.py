from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from .auth import current_user, login_required
from .models import create_entry, get_entries_for_user, get_entry_for_user, mark_entry_opened, utc_now


main_bp = Blueprint("main", __name__)

PRESET_OPTIONS = {
    "30": 30,
    "90": 90,
    "180": 180,
    "365": 365,
}
MIN_UNLOCK_DAYS = 7


def _today() -> date:
    return datetime.now(timezone.utc).date()


def _min_unlock_date() -> date:
    return _today() + timedelta(days=MIN_UNLOCK_DAYS)


def _resolve_unlock_date(form) -> tuple[date | None, str | None]:
    preset = form.get("unlock_preset", "30")
    if preset == "custom":
        custom_value = form.get("custom_unlock_date", "").strip()
        if not custom_value:
            return None, "Choose a custom unlock date."
        try:
            chosen_date = date.fromisoformat(custom_value)
        except ValueError:
            return None, "Enter a valid custom unlock date."
    else:
        days = PRESET_OPTIONS.get(preset)
        if not days:
            return None, "Choose a valid unlock option."
        chosen_date = _today() + timedelta(days=days)

    if chosen_date < _min_unlock_date():
        return None, "Unlock date must be at least 7 days in the future."

    return chosen_date, None


def _unlock_datetime(unlock_date: date) -> datetime:
    return datetime.combine(unlock_date, datetime.min.time(), tzinfo=timezone.utc)


def _dashboard_payload(user_id: int):
    all_entries = get_entries_for_user(user_id)
    locked_entries = [entry for entry in all_entries if not entry.is_unlocked]
    unlocked_entries = [entry for entry in all_entries if entry.is_unlocked]
    next_unlock = locked_entries[0].unlock_at_dt if locked_entries else None

    return {
        "locked_entries": locked_entries,
        "unlocked_entries": unlocked_entries,
        "stats": {
            "total": len(all_entries),
            "waiting": len(locked_entries),
            "unlocked": len(unlocked_entries),
            "next_unlock": next_unlock,
        },
        "min_unlock_date": _min_unlock_date().isoformat(),
        "today": _today().isoformat(),
    }


@main_bp.app_context_processor
def inject_user():
    return {"current_user": current_user()}


@main_bp.route("/")
def index():
    if current_user():
        return redirect(url_for("main.dashboard"))
    return render_template("index.html")


@main_bp.route("/dashboard")
@login_required
def dashboard():
    user = current_user()
    payload = _dashboard_payload(user.id)
    return render_template("dashboard.html", **payload)


@main_bp.route("/create")
@login_required
def create_page():
    return render_template("create.html", min_unlock_date=_min_unlock_date().isoformat())


@main_bp.route("/entries", methods=["POST"])
@login_required
def create_entry_view():
    user = current_user()
    title = request.form.get("title", "").strip()
    content = request.form.get("content", "").strip()
    unlock_date, error = _resolve_unlock_date(request.form)

    if not title:
        flash("Title is required.", "error")
    elif not content:
        flash("Write something to your future self.", "error")
    elif error:
        flash(error, "error")
    else:
        written_at = utc_now().isoformat()
        unlock_at = _unlock_datetime(unlock_date).isoformat()
        create_entry(user.id, title, content, written_at, unlock_at)
        flash("Capsule sealed successfuly.", "success")
        return redirect(url_for("main.dashboard"))

    return redirect(url_for("main.create_page"))


@main_bp.route("/entries/<int:entry_id>")
@login_required
def view_entry(entry_id: int):
    user = current_user()
    entry = get_entry_for_user(user.id, entry_id)
    if entry is None:
        abort(404)
    if not entry.is_unlocked:
        flash("That capsule is still locked.", "error")
        return redirect(url_for("main.dashboard"))

    if entry.is_new:
        mark_entry_opened(entry.id)
        entry = get_entry_for_user(user.id, entry.id)

    return render_template("entry_detail.html", entry=entry)
