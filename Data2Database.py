import time
from random import randrange
import random
from threading import Thread, Lock, Condition
import threading
import serial 
import sqlite3

"""
Database-klassen er meget ufærdig. Lige nu indsætter den kun én værdi fra bufferen i databasen og ikke hele bufferen.
Den indsætter ingen patientdata sammen med EKG-værdierne.

Spørgsmål:
2) Hvorfor returnerer get-metoden en None sammen med hver buffer???
3) Hvordan indsætter man en liste i databasen? Det er vel meningen, at vi netop ikke skal splitte listen/bufferen op? Det virker omstændigt med for-loop

"""

#Sensor-klassen opretter en buffer, henter værdier fra sensoren og lægger værdierne i bufferen
#Når bufferen er fuld, sendes den over i køen, og der oprettes en ny buffer (processen starter forfra)

class Buffer:
    def __init__(self):
        self.list = []
        self.Amount = 100

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

class Database:
    def __init__(self, queue):
        self.queue = queue

    def run(self):
        try:
            self.connection = sqlite3.connect("patientValues.db")
            self.cursor = self.connection.cursor()
            self.dropEKGTable = "DROP TABLE IF EXISTS EKGTable"
            self.cursor.execute(self.dropEKGTable)
            #self.createEKGTable = "CREATE TABLE EKGTable(Number INTEGER PRIMARY KEY AUTOINCREMENT, Value INTEGER)"
            self.createEKGTable = "CREATE TABLE EKGTable(ID INTEGER PRIMARY KEY, Value INTEGER)"
            self.cursor.execute(self.createEKGTable)
            self.insert = "INSERT INTO EKGTable VALUES ({},{})"
            self.id = 1

            while True:
                data = self.queue.get()
                if data != None:
                    print(data, "Databasedata")
                    for i in data:
                        self.cursor.execute(self.insert.format(self.id, i))
                        self.id +=1
                    #self.cursor.execute("INSERT INTO EKGTable (Value) VALUES (?)", [test])
                    self.connection.commit()
                    
        except sqlite3.Error as e:
            print("Fejl", e)
        finally:
            self.cursor.close()
            self.connection.close()


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