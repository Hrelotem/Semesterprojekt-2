import sqlite3
from Queueclass import Queue

class Database:
    def __init__(self, queue1, queue2):
        self.Q1 = queue1
        self.Q2 = queue2

    def run(self):
        try:
            self.connection = sqlite3.connect("PatientData.db")
            self.cursor = self.connection.cursor()
            self.dropEKGTable = "DROP TABLE IF EXISTS EKGTable"
            self.cursor.execute(self.dropEKGTable)                
            self.createEKGTable = "CREATE TABLE EKGTable(ID INTEGER PRIMARY KEY AUTOINCREMENT, Value INTEGER)"
            self.cursor.execute(self.createEKGTable)

            #Nedenstående er Sheilas tilføjelser af kode. Rykket sammen, fordi Amanda har ryddet op i sin del.
            self.dropPatientTable = "DROP TABLE IF EXISTS PatientTable"
            self.cursor.execute(self.dropPatientTable)                     
            self.createPatientTable = "CREATE TABLE PatientTable(ID INTEGER PRIMARY KEY, Name VARCHAR, CPR INTEGER)"
            self.cursor.execute(self.createPatientTable)                 
            self.insertPatient = "INSERT INTO Patient VALUES ({},'{}',{})"

            while True:
                dataToDatabase = self.Q1.get()
                #print(dataToDatabase)
                if dataToDatabase != None:
                    query = "INSERT INTO EKGTable (Value) VALUES"
                    for i in range(len(dataToDatabase)):
                        query += "(" + str(dataToDatabase[i]) + ")"
                        if i < len(dataToDatabase)-1: 
                            query += ","
                    self.cursor.execute(query)
                    self.connection.commit()
                    self.Q2.put(dataToDatabase)
                
        except sqlite3.Error as e:
            print("Fejl", e)

        finally:
            self.cursor.close()
            self.connection.close()