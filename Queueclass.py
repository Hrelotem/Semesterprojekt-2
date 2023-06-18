from threading import Condition
import threading
import random
import time
from Bufferclass import Buffer


class Queue:
    def __init__(self):
        self.queue = []
        self.testqueue = []
        self._lock = Condition()
        self.bufferCount = 0
    
    def put(self, buffer):
        with self._lock:
            self.queue.append(buffer)
            self.testqueue.append(buffer)
            self.bufferCount += 1
            if self.bufferCount == 1:
                self._lock.notify()

    def get(self):
        with self._lock:
            if self.bufferCount == 0:
                self._lock.wait()
            self.bufferCount = self.bufferCount - 1
            return self.queue.pop(0)

class QueueTest:
    def __init__(self):
        self.queue = Queue()
        self.buffer = Buffer()
        self.returnedQueue = []
        self.test()

    def sensor(self):
        while True:
            for i in range(10):
                self.data = round(random.random()*10)
                self.buffer.list.append(self.data)
            self.queue.put(self.buffer.list)
            self.buffer = Buffer()
            time.sleep(1)

    def database(self):
        while True:
            self.returnedQueue.append(self.queue.get())
            time.sleep(0.1)

    def test(self):
        t1 = threading.Thread(target=self.sensor)
        t2 = threading.Thread(target=self.database)
        t1.start(), t2.start()
        time.sleep(60)
        if self.queue.testqueue == self.returnedQueue and self.queue.bufferCount == 0:
            print("Program is working")
        else:
            print("Error in program")

unittest = QueueTest()
unittest.test()