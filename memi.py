from blessed import Terminal
from threading import Thread
from utils import out, autocomplete
from unicodedata import category
import subprocess
import msvcrt
import shlex
import time
import dao
import sys
import io
import re


def _draw(term, mem_output_buffer, user_input_buffer):
    term.location(0, 0)
    print(term.clear)
    print(mem_output_buffer.getvalue())
    print(term.move_y(term.height - 3))
    term.location(0, term.height - 3)
    sys.stdout.write("mem> ")
    sys.stdout.flush()
    sys.stdout.write(user_input_buffer.getvalue())
    sys.stdout.flush()

def _display_message(term, content):
    term.location(0, 0)
    print(term.clear)
    print(content)
    print("\n--------- PRESS ANY KEY TO CONTINUE ----------")
    msvcrt.getwche()

def memi():
    term = Terminal()
    mem_streaming_on = True
    mem_output_buffer = io.StringIO()
    user_input_buffer = io.StringIO()

    def stream_mem_content():
        process = subprocess.run(['mem.bat', 'l'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        output = process.stdout.decode("utf-8")
        mem_output_buffer.write(output)
        _draw(term, mem_output_buffer, user_input_buffer)
        while mem_streaming_on:
            process = subprocess.run(['mem.bat', 'l'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            new_output = process.stdout.decode("utf-8")
            if output != new_output:
                output = new_output
                mem_output_buffer.truncate(0)
                mem_output_buffer.seek(0)
                mem_output_buffer.write(output)
                _draw(term, mem_output_buffer, user_input_buffer)
            time.sleep(0.5)

    mem_thread = Thread(target=stream_mem_content)
    mem_thread.daemon = True
    mem_thread.start()

    with term.fullscreen(), term.cbreak():
        _draw(term, mem_output_buffer, user_input_buffer)
        while True:
            while not msvcrt.kbhit():
                time.sleep(0.01)
            ch = msvcrt.getwche()
            out(ch)
            out(str(ord(ch)))
            out(category(ch))
            if ch == "\t":
                memstate = dao.load_memstate()
                command = user_input_buffer.getvalue()
                command_frags = re.split(r'\s+', command)
                if len(command_frags) < 2:
                    _draw(term, mem_output_buffer, user_input_buffer)
                    continue
                prefix = command_frags[-1]
                if not prefix:
                    _draw(term, mem_output_buffer, user_input_buffer)
                    continue

                targets = [t for t in memstate["focus_targets"].keys()]

                completion = autocomplete(prefix, targets)

                user_input_buffer.truncate(0)
                user_input_buffer.seek(0)

                command = command[:(-1 * len(prefix))] + completion
                user_input_buffer.write(command)
                _draw(term, mem_output_buffer, user_input_buffer)
                continue
            if ord(ch) == 127:
                out("backspace")
                command = user_input_buffer.getvalue()
                command = str(command[:-1])
                user_input_buffer.truncate(0)
                user_input_buffer.seek(0)
                user_input_buffer.write(command)
                _draw(term, mem_output_buffer, user_input_buffer)
                continue
            if ch == "\r":
                command = user_input_buffer.getvalue()
                user_input_buffer.truncate(0)
                user_input_buffer.seek(0)
                if command.strip().lower() == "":
                    _draw(term, mem_output_buffer, user_input_buffer)
                    continue
                if command.strip().lower() in ["q", "quit"]:
                    mem_streaming_on = False
                    mem_thread.join()
                    break
                try:
                    command = ["mem.bat"] + shlex.split(command)
                except:
                    _display_message(term, f'Unable to parse command: {command}')
                    _draw(term, mem_output_buffer, user_input_buffer)
                    continue
                process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                try:
                    output = process.stderr.decode("utf-8")
                except:
                    _display_message(term, "Unable to decode sub-process stderr using UTF-8")
                else:
                    if output:
                        _display_message(term, output)
                try:
                    output = process.stdout.decode("utf-8")
                except:
                    _display_message(term, "Unable to decode sub-process stdout using UTF-8")
                else:
                    if output:
                        _display_message(term, output)
                _draw(term, mem_output_buffer, user_input_buffer)
                continue
            if category(ch)[0] == "C":
                # Discard control character and immediate following characters
                while msvcrt.kbhit():
                    msvcrt.getwche()
                _draw(term, mem_output_buffer, user_input_buffer)
                continue 
            user_input_buffer.write(ch)
            _draw(term, mem_output_buffer, user_input_buffer)


if __name__ == "__main__":
    memi()