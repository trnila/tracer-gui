import subprocess

from PyQt5.QtWidgets import QMessageBox


def format_bytes(num, suffix='B'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


def system_open(path):
    subprocess.Popen(['xdg-open', path])


def report_os_error(e):
    QMessageBox().critical(None, "Could not open file", "Could not open file \"{}\": {}".format(e.filename, e.strerror))
