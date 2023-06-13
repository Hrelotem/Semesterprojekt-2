import sqlite3
from Kø-klasse import Queue

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