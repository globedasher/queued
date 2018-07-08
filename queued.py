import daemon

import queuer

with daemon.DaemonContext():
    queuer()
