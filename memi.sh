#!/bin/sh
SCRIPT=`readlink -f "$0"`
SCRIPT_DIR=`dirname "$SCRIPT"`
. $SCRIPT_DIR/.venv/bin/activate
python memi.py "$@"
deactivate
