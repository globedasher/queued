import daemon

from . import queue

with daemon.DaemonContext():
    queue()
