# mail_queue.py to make a queue
#
#
###############################################################################

import datetime, signal, subprocess, sys, zmq, time, argparse
from multiprocessing import Process, Pipe
from py_core import logger


class Node():
    """
    Node Class.
    """
    next_node = None
    ident = 0
    value = 0

    def __init__(self, data, ident):
        self.value = data
        self.ident = ident


class MailQueue():
    """
    MailQueue class.
    """
    head = None

    def _pop_node(self, ident):
        #print("_pop_node")
        if not self.head:
            return None
        currentNode = self.head
        if currentNode.ident == ident:
            self.head = currentNode.next_node
            currentNode.next_node = None
            return currentNode
        while currentNode:
            if not currentNode.next_node:
                return None
            if currentNode.next_node.ident == ident:
                removal_target = currentNode.next_node
                currentNode.next_node = currentNode.next_node.next_node
                removal_target.next_node = None
                return currentNode
            currentNode = currentNode.next_node

        # If no node with that ident is found, return None
        return None

    def _insert_node(self, value, ident):
        # Create and insert a node
        new_node = Node(value, ident)
        # if no head exists on the queue
        if not self.head:
            self.head = new_node
        # if the new node value is less than the current head
        elif new_node.value < self.head.value:
            new_node.next_node = self.head
            self.head = new_node
        # else find the location to insert it
        else:
            currentNode = self.head
            while currentNode:
                # If we get to the end and haven't inserted the node, add it to
                # then end of the queue
                if not currentNode.next_node:
                    currentNode.next_node = new_node
                    break
                elif (new_node.value > currentNode.value
                    and new_node.value < currentNode.next_node.value):
                    new_node.next_node = currentNode.next_node
                    currentNode.next_node = new_node
                    break
                currentNode = currentNode.next_node

    def insert(self, value, ident):
        """
        Insert a value into the queue.  If a node with the specified ident is
        in the queue, it will be removed and a new node will be created based
        on the new value. If is not in the queue, it will be added at correct
        location.
        """
        print("Insert", value, ident)
        found_on_next_node = self._pop_node(ident)
        # if found_on_next_node:
        #     print("Found node:"
        #          ,found_on_next_node.value
        #          ,found_on_next_node.ident
        #          )
        self._insert_node(value, ident)


    def print_nodes(self):
        print("Print Nodes")
        currentNode = self.head
        node_number = 0
        while currentNode:
            print("Date:", currentNode.value
                 ,"Ident:", currentNode.ident
                 ,"Node number:", node_number
                 )
            currentNode = currentNode.next_node
            node_number += 1

    def end_node(self):
        print("End Node")
        currentNode = self.head
        while currentNode:
            if not currentNode.next_node:
                return currentNode.value
            currentNode = currentNode.next_node

    def expire(self):
        #print("Check for expired node")
        if self.head and self.head.value <= datetime.datetime.now():
            print("Expiring node", self.head.value, self.head.ident)
            self.head = self.head.next_node
        else:
            #print("No nodes to expire")
            pass


class Streams():
    """
    stdin, stdout, stderr class.
    """
    out_original = ''
    err_original = ''

    def __init__(self):
        print("Initializing system.")
        #self.config_out()
        #self.config_err()

    def config_out(self):
        print("config")
        # Redirect the standard output
        self.out_original = sys.stdout
        self.osock = open("output.log", "w")
        sys.stdout = self.osock

    def config_err(self):
        print("config")
        self.err_original = sys.stderr
        self.fsock = open("error.log", "w")
        sys.stderr = self.fsock

    def close(self):
        print("close_streams")
        if self.out_original:
            sys.stdout = self.out_original
        if self.err_original:
            sys.stderr = self.err_original

    def end_runtime(self, signum, frame):
        print("\n\nUser ended runtime.")
        self.close()
        print("\n\nUser ended runtime.")
        #print(dir(frame))
        sys.exit(signum)


class ControlComms():
    def __init__(self):
        print("Creating Controls")


def test_inserts(mail_queue, tests):
    value = 0
    #print(value)
    # This is the main loop of the program. One of the functions run by it will
    # need to check for any interrupt signals.
    while value < tests:
        if value == 0:
            print(datetime.datetime.now())
        value += 1
        #print(value)
        data = datetime.datetime.now()
        offset = datetime.timedelta(seconds = value + 0)
        data = data + offset
        ident = tests - value
        mail_queue.insert(data, ident)
    return mail_queue

def comms_loop(send_pipe):
    print("comms_loop")

    listen_context = zmq.Context()
    listen_socket = listen_context.socket(zmq.REP)
    listen_socket.bind("ipc:///tmp/mail_queue_ipc")

    while True:
        message = listen_socket.recv()
        #print("Received request: %s" % message)
        listen_socket.send(b"World")

        #print("Here")
        message = message.decode("utf-8")
        #print(message)
        if message == "insert":
            #print("Over here")
            send_pipe.send("insert")
        #sys.exit()

def main_loop(mail_queue, streams, recv_pipe):
    print("main_loop")
    ident = 0
    while True:
        # This is the main loop of the program. One of the functions run by it will
        # need to check for any interrupt signals.
        if recv_pipe.poll():
            message = recv_pipe.recv()
            print("Received message: %s" % message)
            if message == "insert":
                #print("insert")
                data = datetime.datetime.now()
                offset = datetime.timedelta(seconds = 2)
                data = data + offset
                mail_queue.insert(data, ident)
                ident += 1

        mail_queue.expire()
        time.sleep(.1)
        if not mail_queue.head:
            #streams.close()
            #break
            pass

    mail_queue.print_nodes()

def process_init(tests):
    print("Starting as process")

    streams = Streams()

    signal.signal(signal.SIGINT, streams.end_runtime)

    mail_queue = MailQueue()
    if tests:
        mail_queue = test_inserts(mail_queue, tests)
        #mail_queue.print_nodes()

    recv_pipe, send_pipe = Pipe()
    comms_loop_process = Process(target=comms_loop, args=(send_pipe, ))
    comms_loop_process.start()

    mail_queue_process = Process(target=main_loop
                       , args=(mail_queue, streams, recv_pipe))
    mail_queue_process.start()

def controls():
    """
    Controls to interact with a running instance of this process.
    """

    context = zmq.Context()

    print("Transmitting commands to process.")
    socket = context.socket(zmq.REQ)
    rc = socket.connect("ipc:///tmp/mail_queue_ipc")
    #print(rc)


    for request in range(2):
        print("Sending request %s" % request)
        socket.send(b"insert")

        message = socket.recv()
        print("Recieved reply %s [ %s ]" % (request, message))
        time.sleep(1)

def get_args():
    """
    Get argument data passed from the command line and return a dictionary of
    the arguments.
    """
    parser = argparse.ArgumentParser()

    help_text = """The control selector can be set to either 'process' or 'control'. 'process' will run the main loop of the process. 'control' will send commands to an instance of the process. """
    parser.add_argument("-s"
                        , "--selector"
                        , dest="selector"
                        , default=""
                        , help=help_text
                        )

    help_text = "Use -t or --tests to run test inserts on startup."
    parser.add_argument("-t"
                        , "--tests"
                        , type=int
                        , dest="tests"
                        , default=0
                        , help=help_text
                        )

    return parser.parse_args()

def main():
    args = get_args()
    print(args)

    if args.selector == "process":
        #print("process")
        process_init(args.tests)
    elif args.selector == "control":
        #print("controls")
        controls()
    else:
        # This else will allow dev to run this script with no args to just run
        # test insert.
        test_queue = MailQueue()
        test_queue = test_inserts(test_queue, 10)
        test_queue = test_inserts(test_queue, 5)
        test_queue.print_nodes()

    if args.selector != "process":
        print("End")

if __name__ == "__main__":
    main()
