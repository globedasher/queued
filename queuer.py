# queuer.py to make a queue
#
#
###############################################################################

import datetime, signal, subprocess, sys, zmq, time
from multiprocessing import Process, Pipe
from py_core import logger


class Node():
    """
    Node Class.
    """
    next_node = None
    identifier = 0
    value = 0

    def __init__(self, data):
        self.value = data


class MailQueue():
    """
    MailQueue class.
    """
    head = None
    def insert(self, value):
        """
        Insert a value into the queue.
        """
        print("Insert", value)
        node = Node(value)
        if not self.head:
            self.head = node
        elif node.value < self.head.value:
            node.next_node = self.head
            self.head = node
        else:
            currentNode = self.head
            while currentNode:
                if not currentNode.next_node:
                    currentNode.next_node = node
                    break
                elif node.value < currentNode.next_node.value:
                    node.next_node = currentNode.next_node
                    currentNode.next_node = node
                    break
                elif not currentNode.next_node:
                    currentNode.next_node = node
                    break
                currentNode = currentNode.next_node

    def print_nodes(self):
        print("Print Nodes")
        currentNode = self.head
        while currentNode:
            print(currentNode.value)
            currentNode = currentNode.next_node

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
            print("Expiring node", self.head.value)
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



def test_inserts(q):
    print("test_inserts")
    value = 0
    print(value)
    # This is the main loop of the program. One of the functions run by it will
    # need to check for any interrupt signals.
    while value < 2:
        if value == 0:
            print(datetime.datetime.now())
        value += 1
        print(value)
        data = datetime.datetime.now()
        offset = datetime.timedelta(seconds = value + 0)
        data = data + offset
        q.insert(data)
    return q

def comms_loop(send_pipe):
    print("comms_loop")

    listen_context = zmq.Context()
    listen_socket = listen_context.socket(zmq.REP)
    listen_socket.bind("ipc:///tmp/myserver")

    while True:
        message = listen_socket.recv()
        print("Recieved request: %s" % message)
        listen_socket.send(b"World")

        print("Here")
        message = message.decode("utf-8")
        print(message)
        if message == "insert":
            print("Over here")
            send_pipe.send("insert")
        #sys.exit()

def main_loop(mail_queue, streams, recv_pipe):
    print("main_loop")

    while True:
        # This is the main loop of the program. One of the functions run by it will
        # need to check for any interrupt signals.
        if recv_pipe.poll():
            message = recv_pipe.recv()
            print("Received message: %s" % message)
            if message == "insert":
                print("insert")
                data = datetime.datetime.now()
                offset = datetime.timedelta(seconds = 2)
                data = data + offset
                mail_queue.insert(data)

        mail_queue.expire()
        time.sleep(.1)
        if not mail_queue.head:
            #streams.close()
            #break
            pass

    mail_queue.print_nodes()

def main():
    print("Starting")

    streams = Streams()

    signal.signal(signal.SIGINT, streams.end_runtime)

    mail_queue = MailQueue()
    mail_queue = test_inserts(mail_queue)
    mail_queue.print_nodes()

    recv_pipe, send_pipe = Pipe()
    cl = Process(target=comms_loop, args=(send_pipe, ))
    cl.start()

    p = Process(target=main_loop, args=(mail_queue, streams, recv_pipe))
    p.start()

if __name__ == "__main__":
    main()
