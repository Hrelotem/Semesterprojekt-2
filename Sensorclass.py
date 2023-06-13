from Bufferclass import Buffer
from Queueclass import Queue
import random
import time

class Sensor:
    def __init__(self, queue):
        self.buffer = Buffer()
        self.queue = queue

    def run(self):
        while True:
            self.data = round(random.random()*10)
            self.buffer.list.append(self.data)
            time.sleep(0.1)                                         #Denne skal formodentlig fjernes/ændres i endelig kode
            if len(self.buffer.list) == self.buffer.Amount:
                self.queue.put(self.buffer)
                self.buffer = Buffer()

    def calculateHR():
        pass
        #Det er formodentlig nemmest at beregne pulsen i denne klasse


