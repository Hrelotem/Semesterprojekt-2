
import tkinter as tk
from tkinter import *
import time
import datetime as dt
from threading import Thread, Condition
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import matplotlib.figure
import threading
import sqlite3
import serial

class Buffer:
    def __init__(self):
        self.list = []
        self.Amount = 400

class Sensor:  
    def __init__(self, queue):
        self.ser = serial.Serial('COM3',38400,timeout=1)
        self.buffer = Buffer()
        self.queue = queue
        self.f = 0
        self.f1 = 0
        self.t = 0
        self.f2 = 0
        self.s = 0
        self.count = 0
        self.max = 0  
        self.threshold = 0
        self.HR = 0
        #self.infile = open("C:\\Users\\Alexander\\OneDrive\\Skrivebord\\SemesterProjekt 2\\Testmålinger.txt","r")
        #self.infile = open("C:\\Users\\Amanda\\OneDrive\\Dokumenter\\Universitet\\01. Sundhedsteknologi\\Semesterprojekt 2\\Testmålinger.txt", "r")
        notReady = True #Start på protokol
        print("Start")
        time.sleep(1)
        while notReady:
            data = self.ser.read()
            data = data.decode()
            print(data)
            if data == "K":
                pyReady = "R"
                pySend = pyReady.encode()
                self.ser.write(pySend)
                notReady = False

    def run(self):
            while True:
                self.data = self.ser.readline().decode().strip('\r\n')
                if len(self.data) > 0:
                    self.data = int(self.data)
                    self.buffer.list.append(self.data)
                    time.sleep(0.01)                                         
                    if len(self.buffer.list) == self.buffer.Amount:
                        self.bufferlist = self.buffer.list
                        self.queue.put(self.bufferlist)
                        self.buffer = Buffer()
                    if self.s >= 2:
                        self.t = self.data - self.f
                        self.f2 = self.t - self.f1
                        self.f1 = self.t
                        self.f = self.data
                        if self.s == 2:
                            self.s = 3
                    elif self.s == 0:
                        self.f = self.data
                        self.s = 1
                    elif self.s == 1:
                        self.f1 = self.data - self.f
                        self.f = self.data
                        self.s = 2
                        self.max = self.f1  
                    if self.s == 3:
                        if self.count < 1000:
                            if self.max < self.f1:
                                self.max = self.f1
                                print(self.s, self.f, self.f1, self.f2, self.max, self.count)
                            self.count += 1
                        else:
                            self.s = 4
                            self.count = 0
                            self.threshold = self.max * 0.60
                            print(self.threshold)
                    if self.s == 4:
                        if self.f1 > self.threshold and self.f2 <= 0 and self.count > 30:
                            self.HR = (400/self.count)*60
                            print(self.s, self.f, self.f1, self.f2, self.count)
                            print("Puls: ", self.HR)
                            self.count = 0
                        else:
                            self.count += 1
    #def run(self):
    #    for aline in self.infile:
    #        self.value = aline.split()
    #        self.value = float(self.value[0])
    #        self.buffer.list.append(self.value)
    #        time.sleep(0.01)
    #        if len(self.buffer.list) == self.buffer.Amount:
    #            self.bufferlist = self.buffer.list
    #            self.queue.put(self.bufferlist)
    #            self.buffer = Buffer()

class Queue:
    def __init__(self):
        self.queue = []
        self._lock = Condition()
        self.bufferCount = 0
    
    def put(self, buffer):
        with self._lock:
            self.queue.append(buffer)
            self.bufferCount += 1
            if self.bufferCount == 1:
                self._lock.notify()

    def get(self):
        with self._lock:
            if self.bufferCount == 0:
                self._lock.wait()
            self.bufferCount = self.bufferCount - 1
            return self.queue.pop(0)

class Database:
    def __init__(self, queue1, queue2):
        self.Q1 = queue1
        self.Q2 = queue2
        self.patientID = 1
        self.patientUnknown = True

    def run(self):
        try:
            self.connection = sqlite3.connect("PatientData.db")
            self.cursor = self.connection.cursor()

            self.dropPatientTable = "DROP TABLE IF EXISTS PatientTable"
            self.cursor.execute(self.dropPatientTable)               
            self.createPatientTable = "CREATE TABLE PatientTable(ID INTEGER PRIMARY KEY AUTOINCREMENT, CPR INTEGER, Name STRING)"
            self.cursor.execute(self.createPatientTable)

            self.patientQuery = "INSERT INTO PatientTable (CPR, Name) VALUES(0, 'O')"
            self.cursor.execute(self.patientQuery)
            self.connection.commit()

            self.cursor.execute("PRAGMA foreign_keys = ON")

            self.dropEKGTable = "DROP TABLE IF EXISTS EKGTable"
            self.cursor.execute(self.dropEKGTable)                
            self.createEKGTable = "CREATE TABLE EKGTable(ID INTEGER PRIMARY KEY AUTOINCREMENT, Value INTEGER, PatientID INTEGER, FOREIGN KEY(PatientID) REFERENCES PatientTable(ID))"
            self.cursor.execute(self.createEKGTable)

            while True:
                dataToDatabase = self.Q1.get()
                if dataToDatabase != None:
                    query = "INSERT INTO EKGTable (Value, PatientID) VALUES"
                    for i in range(len(dataToDatabase)):
                        query += "(" + str(dataToDatabase[i]) + "," + str(self.patientID) + ")"
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

    def savePatientData(self, cpr, name):
        try:
            self.connection1 = sqlite3.connect("PatientData.db")
            self.cursor1 = self.connection1.cursor()
            self.cpr = cpr
            self.name = name

            if self.patientUnknown:
                deleteQuery1 = "DELETE from EKGTable where PatientID = 1"
                deleteQuery2 = "DELETE from PatientTable where CPR = 0"
                self.cursor1.execute(deleteQuery1)
                self.cursor1.execute(deleteQuery2)
                self.connection1.commit()
                print("Successfully deleted")
                self.patientUnknown = False

            self.patientQuery = "INSERT INTO PatientTable (CPR, Name) VALUES(" + str(self.cpr) + "," + "'" + str(self.name) + "'" + ")"
            self.cursor1.execute(self.patientQuery)
            self.connection1.commit()
                
        except sqlite3.Error as e:
            print("Fejl: ", e)

        finally:
            self.cursor1.close()
            self.connection1.close()
    
    def updatePatientID(self, id):
        self.patientID = id

class Model:
    def __init__(self, database):
        self.valid = None
        self.patientCPRs = []
        self.returnedBuffer = []
        self.database = database

    def authPatient(self, data):                                        
        try:
            int(data["cpr"])
            if (len(data["cpr"]) == 10):
                self.valid = "Yes"
            else:
                self.valid = "No"
        except:
            self.valid = "No"

    def savePatient(self, data):
        if (data["cpr"] not in self.patientCPRs):
            self.patientCPRs.append(data["cpr"])
            id = self.patientCPRs.index(data["cpr"]) + 2
            self.database.updatePatientID(id)
            self.database.savePatientData(data["cpr"], data["name"]) 
        else:
            id = self.patientCPRs.index(data["cpr"]) + 2
            self.database.updatePatientID(id)

class Root(Tk):
    def __init__(self):
        super().__init__()
        self.title("EKG for patient")
        self.configure(width=1050, height=600)    
        self.minsize(width=1050, height=600)                            #Sætter en mindste-størrelse af vinduet

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        #Sætter tid og dato i bunden af skærmen
        self.Timelabel=tk.Label(self, font=("Helvetica bold", 10))
        self.Timelabel.grid(row = 1, column = 0, sticky = W, padx=25)
        def digitalclock():                                                                 #opretter funktion for at kunne vise tiden 
            text_input = time.strftime("%H:%M:%S")                                          #viser tiden i timer, minutter og sekunder og gemmer det som en variable
            self.Timelabel.config(text=text_input)
            self.Timelabel.after(200, digitalclock)                                         #opdaterer tiden efter 200 milisekunder
        digitalclock()

        self.date = dt.datetime.now()                                                       #kalder på funktionen der viser tiden og gemmer den i variablen
        self.format_date = f"{self.date:%A, %B %d, %Y}"                                     #viser datoen i dag, måned, dato og år 
        self.Datelabel=tk.Label(self, text = self.format_date,  font=("Helvetica bold", 10))
        self.Datelabel.grid(row = 1,  column = 0, sticky = W, padx=100)

        self.space = Label(self, text="  ", font=("Segoe UI",5))
        self.space.grid(row=2, column=0)

class View:
    def __init__(self):
        self.root = Root()
        self.frames = {}                                                #Opretter tom dictionary, som skal indeholde siderne i applikationen
        
        self.addFrame(PatientView, "Patient")                           #tilføjer opslag i dictionary med key = instans af PatientView og værdi = Patient
        self.addFrame(EKGView, "EKG")

    def addFrame(self, Frame, name):                                    #funktion der sætter key-value-par (en frame med navn) i dictionary self.frames
        self.frames[name] = Frame(self.root)
        self.frames[name].grid(row=0, column=0, sticky= NSEW)

    def showPage(self, name):
        frame = self.frames[name]
        frame.tkraise()

    def startMainloop(self):
        self.showPage("Patient")
        self.root.mainloop()

class PatientView(Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.header = Label(self, text="Patient", font=("Helvetica bold", 30))
        self.header.grid(row=0, column=0, pady=80, sticky=S, columnspan=2)

        self.text = Label(self, text="Indtast patientoplysninger for at se målinger for patienten.", font=("Segoe UI", 14))
        self.text.grid(row=1, column=0, columnspan=2)

        self.space = Label(self, text="  ", font=("Segoe UI",30))
        self.space.grid(row=2, column=0)
        
        self.CPR = tk.Label(self, text = "Patientens CPR-nummer:", font=("Segoe UI",14))
        self.CPR.grid(row=3, column=0, sticky = E)

        self.CPREntry = tk.Entry(self) 
        self.CPREntry.grid(row=3, column=1, ipadx=100, ipady=5, sticky = W, padx = 20)

        self.space1 = Label(self, text="  ",  font=("Segoe UI",10))
        self.space1.grid(row=4, column=0)

        self.name = tk.Label(self, text = "Patientens navn:", font=("Segoe UI",14))
        self.name.grid(row=5, column=0, sticky = E)

        self.nameEntry = tk.Entry(self) 
        self.nameEntry.grid(row=5, column=1, ipadx=100, ipady=5, sticky = W, padx = 20)

        self.space1 = Label(self, text="  ",  font=("Segoe UI",10))
        self.space1.grid(row=6, column=0)

        self.SavePatientData = IntVar()
        self.button = tk.Button(self, text="Se EKG for patient", bg="white", font=("Segoe UI",14), command = self.saveData)
        self.button.grid(row=7, columnspan = 2, ipadx=50, pady=40)
    
    def saveData(self):
        self.patientName =tk.StringVar()
        self.patientCPR = tk.StringVar()
        if self.SavePatientData.get() == 1:
            self.PTName = self.patientName.set(self.nameEntry.get())
            self.PTCPR = self.patientCPR.set(self.CPREntry.get())
        
class EKGView(Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)

        self.patientName=tk.StringVar()
        self.showPatientName = tk.Label(self, font=("Helvetica bold", 30), textvariable=self.patientName)
        self.showPatientName.grid(row=0, column=0, pady = 40, sticky=S, columnspan=2)

        self.plotButton = tk.Button(self, text="Vis EKG", bg="DarkOliveGreen3", font=("Segoe UI",22))
        self.plotButton.grid(row=1, column=1, ipadx=52, ipady=6)

        self.HRFrame = Frame(self, height = 100, width = 200, highlightbackground = "gray", highlightthickness = 2)
        self.HRFrame.grid(row=2, column=1, padx=70)

        self.HRLabel = Label(self.HRFrame, text="Puls:", font=("Sergoe UI", 30))
        self.HRLabel.grid(row=0, column=0, padx=20, pady=20)

        self.HRValue=tk.StringVar()
        self.HRValue.set("10")
        self.HRValueLabel = Label(self.HRFrame, text="60", font=("Sergoe UI", 30), textvariable=self.HRValue)
        self.HRValueLabel.grid(row=0, column=1, padx=20, pady=20)

        self.button = tk.Button(self, text="Se data for ny patient", bg="white", font=("Segoe UI",14))
        self.button.grid(row=3, column=1, ipadx=15, ipady=5)

        self.EKGFrame = Frame(self, height=300, width = 500)
        self.EKGFrame.grid(row=1, column=0, rowspan=3, sticky=E)

        self.space = Label(self, text="  ", font=("Segoe UI",10))
        self.space.grid(row=4, column=0)

class Graph:
    def __init__(self, frame, queue):
        self.frame = frame
        self.queue = queue
        self.fig = matplotlib.figure.Figure()
        self.ax = self.fig.add_subplot()
        self.canvas = FigureCanvasTkAgg(self.fig, master = self.frame)
        self.canvas.get_tk_widget().grid(row=0, column=0)
        self.yar = []

    def plotGraph(self):  
        while True:
            self.yar = self.queue.get()
            self.ax.clear()
            self.ax.set_xlabel("Måling")
            self.ax.set_ylabel("mV")
            x = list(range(1, 401))
            y = self.yar
            self.ax.plot(x,y)
            self.canvas.draw()

class Controller:
    def __init__(self, model, view, queue, sensor):
        self.model = model
        self.view = view
        self.queue = queue
        self.sensor = sensor
        self.patientFrame = self.view.frames["Patient"]
        self.EKGFrame = self.view.frames["EKG"]      
        self._bind()   
        self.graph = Graph(self.EKGFrame.EKGFrame, self.queue)
        self._bind1()
        self._bind2()

    def start(self):
        self.view.startMainloop()
    
    def _bind(self):
        self.patientFrame.button.config(command=self.showEKGPage)

    def showEKGPage(self):
        cpr = self.patientFrame.CPREntry.get()
        name = self.patientFrame.nameEntry.get()
        data = {"cpr": cpr, "name": name}
        self.model.authPatient(data)
        if self.model.valid == "Yes":
            self.model.savePatient(data)
            self.EKGFrame.patientName.set("EKG for " + name)
            self.graph = Graph(self.EKGFrame.EKGFrame, self.queue)
            self.view.showPage("EKG")

    def _bind1(self):
        self.EKGFrame.button.config(command=self.showPatientPage)
    
    def showPatientPage(self):
        self.view.showPage("Patient")

    def _bind2(self):
        self.EKGFrame.plotButton.config(command=self.startPlotGraph)

    def startPlotGraph(self):
        self.t = Thread(target=self.graph.plotGraph)
        self.t.start()
        t1 = Thread(target=self.showPulse)
        t1.start()
    
    def showPulse(self):
        while True:
            self.EKGFrame.HRValue.set(round(self.sensor.HR))

def Main():
    Q1 = Queue()
    Q2 = Queue()
    sensor = Sensor(Q1)
    t1 = threading.Thread(target=sensor.run)
    t1.start()
    database = Database(Q1, Q2)
    t2 = threading.Thread(target=database.run)
    t2.start()
    model = Model(database)
    view = View()
    controller = Controller(model, view, Q2, sensor)
    controller.start()


if __name__ == "__main__":
    Main()