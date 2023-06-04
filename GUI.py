
import tkinter as tk
from tkinter import *

#Vise målinger fra EKG-apparat - hvad vil det sige? Er det bare i grafen?
#Vise dynamisk graf med EKG-signalet

class Model:
    pass

class Root(Tk):
    def __init__(self):
        super().__init__()
        self.title("EKG for patient")
        self.configure(width=1000, height=600)
        self.configure(bg='lightgray')        

        self.minsize(width=1000, height=600)                            #Sætter en mindste-størrelse af vinduet

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

class View:
    def __init__(self):
        self.root = Root()
        self.frames = {}                                                #Opretter tom dictionary, som skal indeholde siderne i applikationen
        
        self.addFrame(PatientView, "Patient")                           #tilføjer opslag i dictionary med key = instans af PatientView og værdi = Patient
        #self.addFrame(EKGView, "EKG")

    def addFrame(self, Frame, name):
        self.frames[name] = Frame(self.root)
        self.frames[name].grid(row=0, column=0, sticky="news")

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

        self.header = Label(self, text="Patient", font=("Helvetica bold", 18))
        self.header.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.text = Label(self, text="Indtast patientoplysninger for at se målinger for patienten.", font=("Segoe UI", 13))
        self.text.grid(row=1, column=0, sticky="w", padx=10)


class EKGView(Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pass


class Controller:
    def __init__(self, model, view):
        self.model = model
        self.view = view

    def start(self):
        self.view.startMainloop()

def main():
    model = Model()
    view = View()
    controller = Controller(model, view)
    controller.start()

if __name__ == "__main__":
    main()

#View().mainloop()