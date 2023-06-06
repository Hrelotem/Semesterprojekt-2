import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
from random import randrange
from threading import Thread

fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)


def FileWriter():
    f=open("C:\\Users\\Alexander\\OneDrive\\Skrivebord\\IT sem 2\\IT-Semester-2-projekt\\UpdatingSample.txt",'a')
    i=0
    while True:
        i+=1
        j=randrange(10)
        data = f.write(str(i)+','+str(j)+'\n')
        print("wrote data")
        time.sleep(1)
        f.flush()


def animate(i):
    pullData = open("C:\\Users\\Alexander\\OneDrive\\Skrivebord\\IT sem 2\\IT-Semester-2-projekt\\UpdatingSample.txt","r").read()
    dataArray = pullData.split('\n')
    xar = []
    yar = []
    for eachLine in dataArray:
        if len(eachLine)>1:
            x,y = eachLine.split(',')
            xar.append(int(x))
            yar.append(int(y))
    ax1.clear()
    ax1.set_title("EKG")
    ax1.set_ylabel("y-akse")
    ax1.set_xlabel("x-akse")
    ax1.grid()
    ax1.plot(xar,yar)
    #if len(xar) == 10:  #prøver at fjerne al data efter 10 values
     #   ax1.clear()
      #  xar.clear()
       # yar.clear()
    
def Main():
    t1=Thread(target=FileWriter)
    t1.start()
    ani = animation.FuncAnimation(fig, animate, interval=1000)
    plt.show()
    print("done")

Main()
