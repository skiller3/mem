import json
import os


def init_memfiles_if_not_exist():
    fname = os.path.join(os.path.dirname(__file__), "memfiles")
    if not os.path.exists(fname):
        os.mkdir(fname)  

def load_memstate():
    fname = os.path.join(os.path.dirname(__file__), "memstate")

    with open(fname, "rt") as fhandle:
        memstate = json.load(fhandle)

    return memstate

def save_memstate(memstate):
    fname = os.path.join(os.path.dirname(__file__), "memstate")
    with open(fname, "wt") as fhandle:
        memstate = json.dump(memstate, fhandle)
        fhandle.flush()

def get_description_snippet(name):
    fname = os.path.join(os.path.dirname(__file__), "memfiles", name)
    with open(fname, "rt") as filehandle:
        snippet = filehandle.readline().strip()[:40]
    return snippet