from threading import Condition
import threading
import random
import time

class Queue:
    def __init__(self):
        self.queue = []
        self._lock = Condition()
        self.bufferCount = 0
    
    def put(self, bufferlist):
        with self._lock:
            self.queue.append(bufferlist)           
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
        self.buffer = []
        self.totalQueue = []                            #Kø med alle buffere, som produceres og sendes til kø-klassen af put
        self.totalReturnedQueue = []                    #Kø med alle buffere, som returneres fra kø-klassen med get

    def sensor(self):
        while True:
            for i in range(600):                          #simulering af sensorværdier, der lægges 600 ad gangen i buffere
                self.data = round(random.random()*10)
                self.buffer.append(self.data)
                time.sleep(0.001)
            self.queue.put(self.buffer)
            self.totalQueue.append(self.buffer)
            self.buffer = []

    def database(self):
        while True:
            self.totalReturnedQueue.append(self.queue.get())

    def test(self):
        t1 = threading.Thread(target=self.sensor)
        t2 = threading.Thread(target=self.database)
        t1.start(), t2.start()
        time.sleep(60)                                  #programmet testes i 60 sekunder
        if self.totalQueue == self.totalReturnedQueue and self.queue.bufferCount == 0:
            print("Program is working")
        else:
            print("Error in program")


unittest = QueueTest()
unittest.test()