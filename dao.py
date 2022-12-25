import json
import os


def get_config():
    fname = os.path.join(os.path.dirname(__file__), "memconfig.json")
    with open(fname, "rt", encoding="utf-8") as fhandle:
        return json.load(fhandle)

def init_memfiles_if_not_exist():
    fname = get_config().MEMFILES_DIR
    if not os.path.exists(fname):
        os.mkdir(fname)

def init_memstate_if_not_exist():
    fname = get_config().MEMSTATE_FILE
    if os.path.exists(fname):
        return
    memstate = {
        'focus_span': 8,
        'focus_targets': {}
    }
    with open(fname, "wt") as fhandle:
        json.dump(memstate, fhandle, indent=2)
        fhandle.flush()

def get_memstate():
    fname = os.path.join(os.path.dirname(__file__), "memstate.json")

    with open(fname, "rt") as fhandle:
        memstate = json.load(fhandle)

    return memstate

def update_memstate(memstate):
    fname = os.path.join(os.path.dirname(__file__), "memstate.json")
    with open(fname, "wt") as fhandle:
        memstate = json.dump(memstate, fhandle, indent=2)
        fhandle.flush()

def get_description_snippet(name):
    fname = os.path.join(os.path.dirname(__file__), "memfiles", name)
    with open(fname, "rt") as filehandle:
        snippet = filehandle.readline().strip()[:40]
    return snippet