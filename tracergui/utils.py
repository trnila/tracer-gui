import subprocess

import hashlib
from PyQt5.QtWidgets import QMessageBox


def format_bytes(num, suffix='B'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


def system_open(path):
    subprocess.Popen(['xdg-open', path])


def save_file(filename, content):
    try:
        with open(filename, "w") as f:
            f.write(content)
    except OSError as e:
        report_os_error(e)


def read_file(filename):
    try:
        with open(filename) as f:
            return f.read()
    except OSError as e:
        report_os_error(e)
    return None


def report_os_error(e):
    QMessageBox().critical(None, "Could not open file", "Could not open file \"{}\": {}".format(e.filename, e.strerror))


def hash_file(handle):
    hash_md5 = hashlib.md5()
    with handle:
        for chunk in iter(lambda: handle.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()
