from threading import Condition
import random

class Queue:
    def __init__(self):
        self.queue = []
        self._lock = Condition()
        self.bufferCount = 0
    
    def put(self, bufferlist):
        #modtager en buffer og tæller bufferCount én op
        #sender en notify, hvis den tæller bufferCount én op (vækker get())
        with self._lock:
            self.queue.append(bufferlist)           
            self.bufferCount += 1
            if self.bufferCount == 1:
                self._lock.notify()

    def get(self):
        #undersøger, om værdien i bufferCount er større end 0
        #hvis bufferCount > 0 returneres den buffer i køen, som har ligget der længst
        #+ der kaldes en wait() + bufferCount tælles én ned
        with self._lock:
            if self.bufferCount == 0:
                self._lock.wait()
            self.bufferCount = self.bufferCount - 1
            return self.queue.pop(0)

#Test flg.:
#Put: Sender buffere, den modtager, i køen og tæller bufferCount op
#Get: Returnerer de buffere, der ligger i køen, og tæller bufferCount ned

class QueueTest:
    def __init__(self):
        self.queue = Queue()
        self.buffer = []

    def testPut(self):
        for i in range (5):
            for i in range(5):
                self.data = round(random.random()*10)
                self.buffer.append(self.data)
            self.queue.put(self.buffer)
            print("Queue: ", self.queue.queue, "Buffercount :", self.queue.bufferCount)
            self.buffer = []
    
    def testGet(self):
        for i in range (5):
            print("Gettest: ", self.queue.get(), self.queue.bufferCount)

    def test(self):
        self.testGet()
        self.testPut()
        self.testGet()

test = QueueTest()
test.testPut()
test.testGet()


#Få det til at køre med test-funktionen
#Ikke printe, men bare skrive "works"