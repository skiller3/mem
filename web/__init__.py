from flask import Flask, request, redirect, Response
import subprocess
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

@app.route("/")
def redirect_from_root():
    return redirect("/static/memi.html", code=302)

@app.route("/memlist")
def memlist():
    print("memlist() called")
    process = subprocess.run([MEM_CMD, 'l'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    return _adjust_eols(process.stdout.decode("utf-8"))

@app.route("/memcmd", methods=['POST'])
def memcmd():
    print("memcmd() called")
    command = request.json["command"]
    command = command.strip()
    command = [MEM_CMD] + shlex.split(command)
    process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    errtext = process.stderr.decode("utf-8")
    text = errtext if errtext else process.stdout.decode("utf-8")
    return _adjust_eols(text)

@app.route("/autocomplete", methods=['POST'])
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
