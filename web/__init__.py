from flask import Flask, request, redirect, Response
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
import subprocess
import hashlib
import shlex
import utils
import dao
import sys
import os
import re


WEB_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(WEB_DIR)
MEM_CMD_EXT = 'bat' if sys.platform.startswith('win32') else 'sh'
MEM_CMD = os.path.join(BASE_DIR, f"mem.{MEM_CMD_EXT}")

app = Flask(__name__)

def _get_or_create_secret_key():
    fname = os.path.join(WEB_DIR, ".secret_key")

    # Create and persist a secret key if it doesn't exist
    if not os.path.exists(fname):
        import secrets
        with open(fname, "wt", encoding="utf-8") as fhandle:
              print(secrets.token_hex(), file=fhandle, end="", flush=True)

    with open(fname, "rt", encoding="utf-8") as fhandle:
        return fhandle.read()

def _adjust_eols(text):
    return text if sys.platform.startswith('win32') else text.replace("\n", "\r\n")

app.secret_key = _get_or_create_secret_key()
app.config['SECRET_KEY'] = _get_or_create_secret_key()
app.config['REMEMBER_COOKIE_SAMESITE'] = "Strict"
app.config['REMEMBER_COOKIE_SECURE'] = True
login_manager = LoginManager()
login_manager.session_protection = "basic"
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    print(f"load_user() called: {user_id}")
    users = utils.get_config()["USERS"]
    if user_id not in users:
        return None
    return User(user_id, True)

@app.route("/")
def redirect_from_root():
    print(f"current_user: {current_user}")
    if current_user.is_authenticated:
        return redirect("/static/memi.html", code=302)
    return redirect("/static/login.html", code=302)

@app.route("/static/memi.html")
def redirect_or_serve_memi():
    print(f"current_user: {current_user}")
    if current_user.is_authenticated:
        with open(os.path.join(WEB_DIR, "static", "memi.html"), "rt", encoding="utf-8") as fhandle:
            return Response(fhandle.read(), mimetype="text/html")
    return redirect("/static/login.html", code=302)

@app.route("/login", methods=['POST'])
def login():
    username = request.form["username"].strip()
    users = utils.get_config()["USERS"]
    if username not in users:
        return Response("Authentication Failed!", status=401)

    password = request.form["password"].strip()  
    password_hashed = hashlib.sha256(password.encode("utf-8")).hexdigest()

    if password_hashed != users.get(username):
        return Response("Authentication Failed!", status=401)

    user = User(username, True)
    login_user(user, remember=True)
    
    return redirect("/static/memi.html", code=302)

@app.route("/logout", methods=['POST'])
@login_required
def logout():
    logout_user()
    return Response(status=200)

@app.route("/memlist")
@login_required
def memlist():
    print("memlist() called")
    process = subprocess.run([MEM_CMD, 'l'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    return _adjust_eols(process.stdout.decode("utf-8"))

@app.route("/memcmd", methods=['POST'])
@login_required
def memcmd():
    print("memcmd() called")
    command = request.json["command"]
    command = command.strip()
    command = [MEM_CMD] + shlex.split(command)
    process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    errtext = process.stderr.decode("utf-8")
    if errtext:
        return _adjust_eols(errtext)
    return _adjust_eols(process.stdout.decode("utf-8"))


@app.route("/autocomplete", methods=['POST'])
@login_required
def autocomplete():
    print("autocomplete() called")
    command = request.json["command"]
    command_frags = re.split(r'\s+', command)
    if len(command_frags) < 2:
        return command
    prefix = command_frags[-1]
    if not prefix:
       return command
    targets = [t for t in dao.load_memstate()["focus_targets"].keys()]
    command_frags = command_frags[:-1] + [utils.autocomplete(prefix, targets)]
    return " ".join(command_frags)

class User():
    def __init__(self, username, authenticated):
        self.user_id = self.username = username
        self.is_active = True
        self.is_anonymous = False
        self.is_authenticated = authenticated
    
    def get_id(self):
        return self.user_id
