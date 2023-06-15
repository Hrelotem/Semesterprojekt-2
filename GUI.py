
import tkinter as tk
from tkinter import *
import time
import datetime as dt
from random import randrange
from threading import Thread, Condition
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import matplotlib.figure
import random
import threading
import sqlite3
import serial

#Tre relevante steder at kende - her ændres bufferstørrelse + hastighed, hvormed simulerede værdier hentes
#1) buffer-klassens amount
#2) sensor-klassens time.sleep i run-metoden
#3) graf-klassens plotgraph-metode

#Obs. I den endelige kode kan nogle af de importerede libraries nok fjernes.

class Buffer:
    def __init__(self):
        self.list = []
        self.Amount = 274

class Sensor:
    def __init__(self, queue):
        self.buffer = Buffer()
        self.queue = queue
        self.infile = open("C:\\Users\\Amanda\\OneDrive\\Dokumenter\\Universitet\\01. Sundhedsteknologi\\Semesterprojekt 2\\Testmålinger.txt", "r")

    """def run(self):
        while True:
            self.data = round(random.random()*10)
            self.data = ser.readline().decode().strip('\r\n')
            if len(self.data) > 0:
                self.buffer.list.append(int(self.data))
                self.buffer.list.append(self.data)
                time.sleep(0.01)                                         #Denne skal formodentlig fjernes/ændres i endelig kode
                if len(self.buffer.list) == self.buffer.Amount:
                    self.queue.put(self.buffer)
                    self.buffer = Buffer()"""
    
    """Nedenstående funktion simulerer tilfældige værdier
        def run(self):
        while True:
            self.data = round(random.random()*10)
            self.buffer.list.append(self.data)
            time.sleep(0.001)                                         #Denne skal formodentlig fjernes/ændres i endelig kode
            if len(self.buffer.list) == self.buffer.Amount:
                self.bufferlist = self.buffer.list
                self.queue.put(self.bufferlist)
                self.buffer = Buffer()"""

    def run(self):
        for aline in self.infile:
            value = aline.split()
            value = value[0]
            self.buffer.list.append(value)
            time.sleep(0.01)
            if len(self.buffer.list) == self.buffer.Amount:
                self.bufferlist = self.buffer.list
                self.queue.put(self.bufferlist)
                self.buffer = Buffer()

    def calculateHR():
        pass
        #Det er formodentlig nemmest at beregne pulsen i denne klasse

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
                print(dataToDatabase)
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

class Model:
    def __init__(self):
        self.valid = None
        self.patientCPRs = []
        self.returnedBuffer = []

    def authPatient(self, data):                                        #OBS! Funktion som validerer, at CPR består af 1 tal. SKAL ÆNDRES TIL 10!
        try:
            int(data["cpr"])
            if (len(data["cpr"]) == 1):
                self.valid = "Yes"
                if (data["cpr"] not in self.patientCPRs):               #hvis cpr ikke er i listen self.patientCPRs, tilføjes det
                    self.patientCPRs.append(data["cpr"])
            else:
                self.valid = "No"
        except:
            self.valid = "No"       

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
        self.HRValue.set("70")
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
            self.yar = [eval(i) for i in self.yar]
            self.ax.clear()
            self.ax.set_xlabel("Måling")
            self.ax.set_ylabel("mV")
            self.ax.set_yticks([0.0045, 0.005, 0.0055, 0.006, 0.0065])
            self.ax.set_ylim(bottom = 0.0044, top = 0.0065, auto=False)
            x = list(range(1, 275))
            y = self.yar
            self.ax.plot(x,y)
            self.canvas.draw()

class Controller:
    def __init__(self, model, view, queue):
        self.model = model
        self.view = view
        self.queue = queue
        self.ekgController = EKGController(model, view, queue)
        self.patientController = PatientController(model, view)         

    def start(self):
        self.view.startMainloop()

class PatientController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.patientFrame = self.view.frames["Patient"]
        self.EKGFrame = self.view.frames["EKG"]
        self._bind()
    
    def _bind(self):
        self.patientFrame.button.config(command=self.showEKGPage)

    def showEKGPage(self):
        cpr = self.patientFrame.CPREntry.get()
        name = self.patientFrame.nameEntry.get()
        data = {"cpr": cpr, "name": name}
        self.model.authPatient(data)
        if self.model.valid == "Yes":
            self.EKGFrame.patientName.set("EKG for " + name)
            self.view.showPage("EKG")

class EKGController:
    def __init__(self, model, view, queue):
        self.model = model
        self.view = view
        self.queue = queue
        self.EKGFrame = self.view.frames["EKG"]
        self.graph = Graph(self.EKGFrame.EKGFrame, self.queue)
        self._bind1()
        self._bind2()
    
    def _bind1(self):
        self.EKGFrame.button.config(command=self.showPatientPage)
    
    def showPatientPage(self):
        self.view.showPage("Patient")

    def _bind2(self):
        self.EKGFrame.plotButton.config(command=self.startPlotGraph)

    def startPlotGraph(self):
        t = Thread(target=self.graph.plotGraph)
        t.start()

def Main():
    Q1 = Queue()
    Q2 = Queue()
    sensor = Sensor(Q1)
    database = Database(Q1, Q2)
    t1 = threading.Thread(target=sensor.run)
    t1.start()
    t2 = threading.Thread(target=database.run)
    t2.start()
    model = Model()
    view = View()
    controller = Controller(model, view, Q2)
    controller.start()

if __name__ == "__main__":
    Main()
