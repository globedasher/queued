# queue.py to make a queue
#
#
###############################################################################

import datetime, signal, daemon, subprocess

class Node():
    """
    Node Class.
    """
    next_node = None
    value = 0

    def __init__(self, data):
        self.value = data


class Queue():
    """
    Queue class.
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
        if self.head.value <= datetime.datetime.now():
            print("Expiring node", self.head.value)
            self.head = self.head.next_node
        else:
            #print("No nodes to expire")
            pass


def configure():
    # Create a queue to pass to the main loop.
    return Queue()

def test_inserts(q):
    print("test_inserts")
    value = 0
    print(value)
    # This is the main loop of the program. One of the functions run by it will
    # need to check for any interrupt signals.
    while value < 5:
        value += 1
        print(value)
        data = ( datetime.datetime.now()
                + datetime.timedelta(seconds= value + 2)
                )
        q.insert(data)

    return q

def main_loop(q):
    print("main_loop")

    q = test_inserts(q)
    q.print_nodes()

    while True:
        # This is the main loop of the program. One of the functions run by it will
        # need to check for any interrupt signals.
        q.expire()
        if not q.head:
            print("No more nodes.")
            break

    q.print_nodes()

def main():
    mail_queue = configure()
    main_loop(mail_queue)

if __name__ == "__main__":
    main()
