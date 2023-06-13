
import tkinter as tk
from tkinter import *
import time
import datetime as dt
from random import randrange
from threading import Thread
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import matplotlib.figure
import random
import threading


#Koden under bruges til at tjekke at der er kommunikation mellem arduino og python
#ser = serial.Serial('COM3',9600,timeout=1)

#def ready():
 #   notReady = True
  #  print("Start")
   # time.sleep(1)
    #while notReady:
     #   readyData = ser.read()
      #  readyData = readyData.decode()
       # print(readyData)
        #if readyData == "K":    
         #   pyReady = "R"
          #  pySend = pyReady.encode()
           # ser.write(pySend)
            #notReady = False

#def queue():
 #   arduino_data = [] # declare a list
  #  while True:
   #     data = ser.readline()
    #    if data:
     #       arduino_data.append(data) # Append a data to your declared list
      #      print(arduino_data)

#Vise målinger fra EKG-apparat - hvad vil det sige? Er det bare i grafen?
#Vise dynamisk graf med EKG-signalet

#Lige nu viser grafen ikke løbende målinger, men det gør den, hvis man går tilbage til de tal, den selv genererer


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

    def simulateBuffer(self):
        #Den endelige funktion her skal kalde get-funktionen i kø nr. 2
        self.returnedBuffer = [] 
        for i in range(10):
            self.data = round(random.random()*10)
            self.returnedBuffer.append(self.data)
        print("Returneret buffer fra model: ", self.returnedBuffer)
        #return self.returnedBuffer            

class Root(Tk):
    def __init__(self):
        super().__init__()
        self.title("EKG for patient")
        self.configure(width=1000, height=600)    
        self.minsize(width=1000, height=600)                            #Sætter en mindste-størrelse af vinduet

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        #Sætter tid og dato i bunden af skærmen
        self.Timelabel=tk.Label(self, font=("Helvetica bold", 10))
        self.Timelabel.grid(row = 1, column = 0, sticky = E, padx=48)
        def digitalclock():                                                                 #opretter funktion for at kunne vise tiden 
            text_input = time.strftime("%H:%M:%S")                                          #viser tiden i timer, minutter og sekunder og gemmer det som en variable
            self.Timelabel.config(text=text_input)
            self.Timelabel.after(200, digitalclock)                                         #opdaterer tiden efter 200 milisekunder
        digitalclock()

        self.date = dt.datetime.now()                                                       #kalder på funktionen der viser tiden og gemmer den i variablen
        self.format_date = f"{self.date:%A, %B %d, %Y}"                                     #viser datoen i dag, måned, dato og år 
        self.Datelabel=tk.Label(self, text = self.format_date,  font=("Helvetica bold", 10))
        self.Datelabel.grid(row = 1,  column = 0, sticky = E, padx=120)

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
        self.header.grid(row=0, column=0, pady=70, sticky=S, columnspan=2)

        self.text = Label(self, text="Indtast patientoplysninger for at se målinger for patienten.", font=("Segoe UI", 13))
        self.text.grid(row=1, column=0, columnspan=2)

        self.space = Label(self, text="  ", font=("Segoe UI",30))
        self.space.grid(row=2, column=0)
        
        self.CPR = tk.Label(self, text = "Patientens CPR-nummer:", font=("Segoe UI",13))
        self.CPR.grid(row=3, column=0, sticky = E)

        self.CPREntry = tk.Entry(self) 
        self.CPREntry.grid(row=3, column=1, ipadx=100, ipady=5, sticky = W, padx = 20)

        self.space1 = Label(self, text="  ",  font=("Segoe UI",10))
        self.space1.grid(row=4, column=0)

        self.name = tk.Label(self, text = "Patientens navn:", font=("Segoe UI",13))
        self.name.grid(row=5, column=0, sticky = E)

        self.nameEntry = tk.Entry(self) 
        self.nameEntry.grid(row=5, column=1, ipadx=100, ipady=5, sticky = W, padx = 20)

        self.space1 = Label(self, text="  ",  font=("Segoe UI",10))
        self.space1.grid(row=6, column=0)

        self.button = tk.Button(self, text="Se EKG for patient", bg="white", font=("Segoe UI",13))
        self.button.grid(row=7, columnspan = 2, ipadx=50, pady=40)

class EKGView(Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)

        self.patientName=tk.StringVar()
        self.showPatientName = tk.Label(self, font=("Helvetica bold", 30), textvariable=self.patientName)
        self.showPatientName.grid(row=0, column=0, pady = 70, sticky=S, columnspan=2)

        self.HRFrame = Frame(self, height = 100, width = 200, highlightbackground = "gray", highlightthickness = 2)
        self.HRFrame.grid(row=1, column=1)

        self.HRLabel = Label(self.HRFrame, text="Puls:", font=("Sergoe UI", 30))
        self.HRLabel.grid(row=0, column=0, padx=20, pady=20)

        self.HRValue=tk.StringVar()
        self.HRValue.set("70")
        self.HRValueLabel = Label(self.HRFrame, text="60", font=("Sergoe UI", 30), textvariable=self.HRValue)
        self.HRValueLabel.grid(row=0, column=1, padx=20, pady=20)

        self.button = tk.Button(self, text="Se data for ny patient", bg="white", font=("Segoe UI",14))
        self.button.grid(row=2, column=1, ipadx=15, ipady=5)

        self.EKGFrame = Frame(self, height=300, width = 500, bg="white")
        self.EKGFrame.grid(row=1, column=0, rowspan=2)

        self.fig = matplotlib.figure.Figure()
        self.ax = self.fig.add_subplot()
        self.canvas = FigureCanvasTkAgg(self.fig, master = self.EKGFrame)
        self.canvas.get_tk_widget().grid(row=0, column=0)

        self.space = Label(self, text="  ", font=("Segoe UI",30))
        self.space.grid(row=3, column=0)

        self.plotButton = tk.Button(self, text="Vis EKG", bg="white", font=("Segoe UI",14))#, command = self.startPlotThread)
        self.plotButton.grid(row=4, column=0, ipadx=15, ipady=5)

        self.xar = []
        self.yar = []

    #def getData(self):
    #    pullData = open("C:\\Users\\Amanda\\OneDrive\\Dokumenter\\Universitet\\UpdatingSample.txt", "r").read()
    #    dataArray = pullData.split('\n')
    #    for eachLine in dataArray:
    #        if len(eachLine)>1:
    #            x,y = eachLine.split(',')
    #            self.xar.append(int(x))
    #            self.yar.append(int(y))

    #def startPlotThread(self, yar):
    #    t1=Thread(target=self.plotGraph(args=yar,))
    #    t1.start()
        
    def plotGraph(self, yar):    
        while True:
            self.ax.clear()
            #x = np.random.randint(0, 10, 10)
            #y = np.random.randint(0, 10, 10)
            x = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            y = yar
            self.ax.plot(x,y)
            self.canvas.draw()
            time.sleep(2)

def FileWriter():
    f=open("C:\\Users\\Amanda\\OneDrive\\Dokumenter\\Universitet\\UpdatingSample.txt", 'a')
    i=0
    while True:
        i+=1
        j=randrange(10)
        data = f.write(str(i)+','+str(j)+'\n')
        print("wrote data")
        time.sleep(2)
        f.flush()

class Controller:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.ekgController = EKGController(model, view)
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
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.EKGFrame = self.view.frames["EKG"]
        self._bind1()
        self._bind2()
    
    def _bind1(self):
        self.EKGFrame.button.config(command=self.showPatientPage)
    
    def showPatientPage(self):
        self.view.showPage("Patient")

    def _bind2(self):
        self.EKGFrame.plotButton.config(command=self.startPlotGraph)

#Nedenstående funktion skal ændres - bufferen simuleres kun én gang, og der gives en statisk liste som argument i l. 286
    def startPlotGraph(self):
        #t=Thread(target=self.EKGFrame.plotGraph, args=([2, 4, 7, 9, 15],))
        t = Thread(target=self.model.simulateBuffer)
        t.start()
        #t=Thread(target=self.EKGFrame.plotGraph, args=(self.model.simulateBuffer,))
        #t.start()
        t1=Thread(target=self.EKGFrame.plotGraph, args=(self.model.returnedBuffer,))
        t1.start()

def Main():
    #ready()
    #t1=Thread(target=FileWriter)
    print("done")
    model = Model()
    view = View()
    controller = Controller(model, view)
    controller.start()

if __name__ == "__main__":
    Main()
