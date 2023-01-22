from flask import Flask, request, redirect, Response, send_file
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


def _adjust_eols(text):
    return text if sys.platform.startswith('win32') else text.replace("\n", "\r\n")

@app.route("/")
def redirect_from_root():
    return redirect("/static/memi.html", code=302)

@app.route("/static/edit.html")
def redirect_from_edit_send():
    focus_item = request.args.get("focusitem")
    if focus_item not in dao.load_memstate()["focus_targets"]:
        return redirect("/static/memi.html", code=302)
    return send_file(os.path.join(WEB_DIR, "static", "edit.html"), download_name="edit/html",
                     mimetype="text/html")

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

@app.route("/description", methods=['GET'])
def load_description():
    focus_item = request.args.get("focusitem")
    return dao.load_description(focus_item)

@app.route("/description", methods=['POST'])
def save_description():
    focus_item = request.json["focusitem"]
    text = request.json["text"]
    dao.save_description(focus_item, text)
    return Response(status=200)