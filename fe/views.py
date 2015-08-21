__all__ = [
    "get_apps"
    "do_deploy"
]

from flask import render_template, request, redirect, url_for, abort
from flask import session, current_app
import requests


def get_login():
    return render_template('login.html')


def do_login():
    # POST to the API/login with the username and password for validation
    # expect back an access token to be stored in a session for use in future API calls
    r = requests.post("{}login/".format(current_app.config["API_URI"]), request.form)
    session["username"] = request.form["username"]
    session["fakeauth"] = r.content
    return redirect(url_for('get_apps'))

def do_logout():
    session.clear()
    return redirect(url_for('get_apps'))


def get_apps():
    fake_auth_header = session.get("fakeauth", None)
    headers = {"fakeauth": fake_auth_header} if fake_auth_header else {}
    try:
        r = requests.get("{}apps/".format(current_app.config["API_URI"]), headers=headers)
        r.raise_for_status()
        apps = r.json()
        apps = [
            dict(a.items() + {"stages": {s["name"]: s for s in a["stages"]}}.items())
            for a in apps
        ]
    except requests.HTTPError as e:
        if e.response.status_code:
            return redirect(url_for('get_login'))
    return render_template(
        'index.html',
        apps=apps, username=session["username"])

def login():
    if request.method == "GET":
        return render_template('login.html')
    elif request.method == "POST":
        return redirect(url_for('login'))


def do_deploy():
    app = request.form["app"]
    version = request.form["version"]
    stage = request.form["stage"]
    apps[app]["stage"][stage]["version"] = version
    return redirect(url_for('get_apps'))
