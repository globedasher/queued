import queuer, datetime

def queue_test():
    print("Perform queue_test()")
    q = queuer.Queue()
    value = 8
    q.insert(value)
    value = 3
    q.insert(value)
    value = 5
    q.insert(value)
    value = 1
    q.insert(value)
    value = 199
    q.insert(value)

    data = q.head

    q.print_nodes()

    if q.end_node() == value:
        print("Test passed!")
    else:
        print("Test failed.")

#queue_test()

def date_test():
    print("Perform date_test()")
    q = queuer.Queue()

    value = datetime.datetime.now()
    offset = datetime.timedelta(days=8)
    value = value + offset
    q.insert(value)

    value = datetime.datetime.now()
    offset = datetime.timedelta(days=-2)
    value = value + offset
    q.insert(value)

    value = datetime.datetime.now()
    offset = datetime.timedelta(days=6)
    value = value + offset
    q.insert(value)

    value = datetime.datetime.now()
    offset = datetime.timedelta(days=1)
    value = value + offset
    q.insert(value)

    value = datetime.datetime.now()
    offset = datetime.timedelta(days=199)
    value = value + offset
    q.insert(value)

    value = datetime.datetime.now()
    offset = datetime.timedelta(days=149)
    value = value + offset
    q.insert(value)

    print("")
    q.expire()
    print("")

    data = q.head

    q.print_nodes()

date_test()
