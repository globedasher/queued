import zmq

context = zmq.Context()

print("Connecting to world server...")
socket = context.socket(zmq.REQ)
rc = socket.connect("ipc:///tmp/myserver")
print(rc)


for request in range(10):
    print("Sending request %s" % request)
    socket.send(b"Hello")

    message = socket.recv()
    print("Recieved reply %s [ %s ]" % (request, message))
