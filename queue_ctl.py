import zmq, time

context = zmq.Context()

print("Connecting to world server...")
socket = context.socket(zmq.REQ)
rc = socket.connect("ipc:///tmp/myserver")
print(rc)


for request in range(2):
    print("Sending request %s" % request)
    socket.send(b"insert")

    message = socket.recv()
    print("Recieved reply %s [ %s ]" % (request, message))
    time.sleep(1)
