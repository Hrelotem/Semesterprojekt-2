import time
from random import randrange
import random
from threading import Thread, Lock, Condition
import threading
import serial 
import sqlite3

"""
OBS ift. koden:
Database-klassen er meget ufærdig. Lige nu indsætter den kun én værdi fra bufferen i databasen og ikke hele bufferen.
Den indsætter alle værdier i databasen knyttet til nummeret 1 i stedet for et autogenereret nummer.
Den indsætter ingen patientdata sammen med EKG-værdierne.
Man skal manuelt slette databasen på sin pc, hver gang man gerne vil køre programmet igen.
Koden skal indsættes i try/except/finally-blokke.

Spørgsmål:
1) Er notify/wait/lock brugt rigtigt? Seems like it, but not sure
2) Hvorfor returnerer get-metoden en None sammen med hver buffer???
3) Hvordan indsætter man en liste i databasen? Det er vel meningen, at vi netop ikke skal splitte listen/bufferen op?

"""


#Sensor-klassen opretter en buffer, henter værdier fra sensoren og lægger værdierne i bufferen
#Når bufferen er fuld, sendes den over i køen, og der oprettes en ny buffer (processen starter forfra)

class Sensor:
    def __init__(self, queue):
        self.buffer = Buffer()
        self.queue = queue

    def run(self):
        while True:
            data = round(random.random()*10)
            self.buffer.list.append(data)
            time.sleep(1)
            if len(self.buffer.list) == self.buffer.Amount:
                self.queue.put(self.buffer)
                self.buffer = Buffer()

    def calculateHR():
        pass
        #Det er formodentlig nemmest at beregne pulsen i denne klasse

class Buffer:
    def __init__(self):
        self.list = []
        self.Amount = 5

#Kø-klassen indeholder en kø af buffere, som ikke er sendt videre til databasen
#Lock-objekt skal forhindre, at put() og get() udføres samtidig

class Queue:
    def __init__(self):
        self.queue = []
        self._lock = Condition()
        self.bufferCount = 0
    
    def put(self, buffer):
        #modtager en buffer og tæller bufferCount én op
        #sender en notify, hvis den tæller bufferCount én op (vækker get())
        with self._lock:
            self.queue.append(buffer.list)
            self.bufferCount += 1
            self._lock.notify()

    def get(self):
        #undersøger, om værdien i bufferCount er større end 0
        #hvis bufferCount > 0 returneres den buffer i køen, som har ligget der længst
        #+ der kaldes en wait() + bufferCount tælles én ned
        with self._lock:
            if self.bufferCount == 0:
                self._lock.wait()
            else:
                self.bufferCount = self.bufferCount - 1
                return self.queue.pop(0)

                
class Database:
    def __init__(self, queue):
        self.queue = queue

    def run(self):
        self.createEKGTable = "CREATE TABLE EKGTable(Number INTEGER, Value INTEGER)"
        self.insertEKG = "INSERT INTO EKGTable VALUES ({}, {})"
        self.connection = sqlite3.connect("patientValues.db")
        self.cursor = self.connection.cursor()

        self.cursor.execute(self.createEKGTable)
        
        while True:
            data = self.queue.get()
            if data != None:
                print(data)
                test = data[0]
                self.cursor.execute(self.insertEKG.format(1, test))
                self.connection.commit()

"""
class Database:
    def __init__(self, queue):
        self.queue = queue

    def run(self):
        try:
            dropEKGTable = "DROP TABLE IF EXISTS EKGTable"
            self.cursor.execute(dropEKGTable)
            self.createEKGTable = "CREATE TABLE EKGTable(Number INTEGER, Value INTEGER)"
            self.insertEKG = "INSERT INTO EKGTable VALUES ({}, {})"
            self.connection = sqlite3.connect("patientValues.db")
            self.cursor = self.connection.cursor()

            self.cursor.execute(self.createEKGTable)
        
            while True:
                data = self.queue.get()
                if data != None:
                    print(data)
                    test = data[0]
                    self.cursor.execute(self.insertEKG.format(1, test))
                    self.connection.commit()
        
        except sqlite3.Error as e:
            print("Kommunikationsfejl med SQLite", e)
        
        #finally:
        #    self.cursor.close()
        #    self.connection.close()
"""


def Main():
    Q1 = Queue()
    sensor = Sensor(Q1)
    database = Database(Q1)
    t1 = threading.Thread(target=sensor.run)
    t1.start()
    t2 = threading.Thread(target=database.run)
    t2.start()

if __name__ == "__main__":
    Main()