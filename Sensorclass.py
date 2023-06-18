
import time
import serial
from Bufferclass import Buffer

class Sensor:  
    def __init__(self, queue):
        #self.ser = serial.Serial('COM3',38400,timeout=1)
        self.buffer = Buffer()
        self.queue = queue
        self.infile = open("C:\\Users\\Alexander\\OneDrive\\Skrivebord\\SemesterProjekt 2\\Testmålinger.txt","r")
        self.value = 0.004
        self.diffTime = 1
        #notReady = True #Start på protokol
        #print("Start")
        #time.sleep(1)
        #while notReady:
         #   data = self.ser.read()
          #  data = data.decode()
           # print(data)
            #if data == "K":
             #   pyReady = "R"
              #  pySend = pyReady.encode()
               # self.ser.write(pySend)
                #notReady = False

#    def run(self):
 #       while True:
  #          self.data = self.ser.readline().decode().strip('\r\n')
   #         if len(self.data) > 0:
    #            self.buffer.list.append(int(self.data))
     #           time.sleep(0.01)                                         #Denne skal formodentlig fjernes/ændres i endelig kode
      #          if len(self.buffer.list) == self.buffer.Amount:
       #             self.bufferlist = self.buffer.list
        #            self.queue.put(self.bufferlist)
         #           self.buffer = Buffer()
    

    def run(self):
        for aline in self.infile:
            self.value = aline.split()
            self.value = float(self.value[0])
            self.buffer.list.append(self.value)
            if len(self.buffer.list) == self.buffer.Amount:
                self.bufferlist = self.buffer.list
                self.queue.put(self.bufferlist)
                self.buffer = Buffer()

            self.threshold = 0.0055
            self.obj = time.gmtime(0)
            self.epoch = time.asctime(self.obj)
            self.curr_time = round(time.time()*1000)
            if self.value > self.threshold:
                time.sleep(0.1)
                self.newCurrTime = round(time.time()*1000)
                self.diffTime = self.newCurrTime-self.curr_time
                self.curr_time = self.newCurrTime           
                self.pulse = 6000/self.diffTime
                self.pulse = round(self.pulse)
                print("Puls: ", self.pulse)

