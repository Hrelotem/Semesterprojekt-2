import time
from random import randrange
import random
from threading import Thread, Lock, Condition
import threading
import serial 
import numpy as np

class Sensor:
    def __init__(self, queue):
        self.buffer = Buffer()
        self.queue = queue
        #Når konstruktøren startes, oprettes en buffer
        #Klassen henter en værdi fra sensoren og lægger den i bufferen
        #Når bufferen er fuld, skal der oprettes en ny buffer
        #Sensor-klassen sender bufferen over i køen, når den er fuld

    def run(self):
        while True:
            data = round(random.random()*10)
            self.buffer.list.append(data)
            print(self.buffer.list)
            time.sleep(1)
            if len(self.buffer.list) == self.buffer.Amount:
                self.queue.put(self.buffer)
                self.buffer = Buffer()

    def calculateHR():
        pass
        #Det er formodentlig nemmest at beregne pulsen i denne klasse"""

#class Sensor(threading.Thread):
#    def __init__(self):
#        super().__init__()
#        pass
#
#    def run(self):
#        while True:
#            data = np.random.randint(0, 10, 10)
#            print(data)
#            time.sleep(1)

class Buffer:
    def __init__(self):
        self.list = []
        self.Amount = 5

class Queue:
    def __init__(self):
        self.queue = []
        self._lock = Condition()
        self.bufferCount = 0
        #Vi skal bruge lock-objektet på put() og get(), så de ikke kan udføres samtidig
        #Køen indeholder de buffere, som ikke er sendt videre til databasen
    
    def put(self, buffer):
        #modtager en buffer
        #tæller bufferCount én op, når den modtager en buffer
        #sender en notify, hvis den tæller bufferCount én op (vækker get())
        with self._lock:
            self.queue.append(buffer.list)
            self.bufferCount += 1
            print(self.queue, self.bufferCount)
            self._lock.notify()
    
    def get(self):
        #undersøger, om værdien i køens tæller er større end 0. Hvis den er, kalder den en wait()
        #piller den buffer ud af kø-listen, der har ligget i listen i længst tid, og returnerer den
        #tæller bufferCount én ned, når den returnerer en buffer
        with self._lock:
            if self.bufferCount > 0:
                print("Buffercount > 0")

class Database:
    def __init__(self, queue):
        self.queue = queue

    def run(self):
        while True:
            self.queue.get()
            print("Hey")
            time.sleep(5)


def Main():
    Q1 = Queue()
    sensor = Sensor(Q1)
    database = Database(Q1)
    t = threading.Thread(target=sensor.run)
    t.start()
    t1 = threading.Thread(target=database.run)
    t1.start()
    #t = Sensor()
    #t.start()

if __name__ == "__main__":
    Main()