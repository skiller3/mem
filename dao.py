import utils
import json
import os


def init_memfiles_if_not_exist():
    fname = utils.get_config()["MEMFILES_DIR"]
    if not os.path.exists(fname):
        os.mkdir(fname)

def init_memstate_if_not_exist():
    fname = utils.get_config()["MEMSTATE_FILE"]
    if os.path.exists(fname):
        return
    memstate = {
        'focus_span': 8,
        'focus_targets': {}
    }
    with open(fname, "wt", encoding="utf-8") as fhandle:
        json.dump(memstate, fhandle, indent=2)
        fhandle.flush()

def load_memstate():
    fname = utils.get_config()["MEMSTATE_FILE"]
    with open(fname, "rt", encoding="utf-8") as fhandle:
        memstate = json.load(fhandle)
    return memstate

def save_memstate(memstate):
    fname = utils.get_config()["MEMSTATE_FILE"]
    with open(fname, "wt", encoding="utf-8") as fhandle:
        memstate = json.dump(memstate, fhandle, indent=2)
        fhandle.flush()

def load_description_snippet(name):
    fname = os.path.join(utils.get_config()["MEMFILES_DIR"], name)
    with open(fname, "rt", encoding="utf-8") as fhandle:
        snippet = fhandle.readline().strip()[:40]
    return snippet

def load_description(name):
    fname = os.path.join(utils.get_config()["MEMFILES_DIR"], name)
    with open(fname, "rt", encoding="utf-8") as fhandle:
        snippet = fhandle.read()
    return snippet

def get_description_filename(name):
    return os.path.join(utils.get_config()["MEMFILES_DIR"], name)

def save_description(name, description):
    fname = os.path.join(utils.get_config()["MEMFILES_DIR"], name)
    with open(fname, "wt", encoding="utf-8") as fhandle:
        fhandle.write(description)
        fhandle.flush()

def rename_description(old_name, new_name):
    old_file = os.path.join(utils.get_config()["MEMFILES_DIR"], old_name)
    new_file = os.path.join(utils.get_config()["MEMFILES_DIR"], new_name)
    os.rename(old_file, new_file)

def delete_description(name):
    fname = os.path.join(utils.get_config()["MEMFILES_DIR"], name)
    os.remove(fname)