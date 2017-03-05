import os

EDITORS = {
    "hex edit with vim": "xterm -e \"sh -c 'xxd %path% | vim -'\"",
    "vim": "xterm -e \"vim %path%\"",
    "system editor (xdg-open)": "xdg-open %path%"
}

try:
    with open(os.path.expanduser("~/.tracerguirc")) as f:
        exec(f.read())
except FileNotFoundError:
    pass
