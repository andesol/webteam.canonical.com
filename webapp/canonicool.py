import requests
import os
import humanize
import hashlib
import math

from datetime import datetime
from dateutil import parser
from flask import Blueprint, render_template, request

DEPLOYMENT_ID = os.getenv(
    "DEPLOYMENT_ID",
    "AKfycbxml18LuuG6tgJ2Dr8n1OLMgvrK4djN94GUje3I2-wt6LgXXGcHeHiXY3hG6dUrLByw",
)
CANONICOOL_SHEET_URL = (
    f"https://script.google.com/macros/s/{DEPLOYMENT_ID}/exec"
)

canonicool = Blueprint(
    "canonicool",
    __name__,
    template_folder="/templates",
    static_folder="/static",
)


def hash_email(email):
    return hashlib.md5(email.encode("utf-8")).hexdigest()


@canonicool.route("/")
def index():
    limit = request.args.get("limit", default=6, type=int)
    offset = request.args.get("offset", default=0, type=int)
    page = request.args.get("page", default=1, type=int)
    response = requests.get(CANONICOOL_SHEET_URL)

    future_events = []
    past_events = []

    today = datetime.today()

    for canonicool_session in response.json():
        session_date = parser.parse(canonicool_session["date"])
        canonicool_session["human_date"] = humanize.naturalday(session_date)
        canonicool_session["presenter1_email_hash"] = hash_email(
            canonicool_session["presenter1_email"]
        )

        canonicool_session["presenter2_email_hash"] = hash_email(
            canonicool_session["presenter2_email"]
        )
    
        canonicool_session["presenter3_email_hash"] = hash_email(
            canonicool_session["presenter3_email"]
        )
        if today > session_date.replace(tzinfo=None):
            past_events.insert(0, canonicool_session)
        elif today <= session_date.replace(tzinfo=None):
            future_events.append(canonicool_session)

    paginated_past_events = past_events[0:6]

    return render_template(
        "canonicool.html",
        past_events=paginated_past_events,
        future_events=future_events,
    )
