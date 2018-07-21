import daemon

import mail_queue

with daemon.DaemonContext():
    mail_queue()
