# send()
# recv()
import socket
import time
import thread
import serial
from robot_interface.alan_robot import AlanRobot

luke = AlanRobot(run_time=86400, period=10.0)  # Run for 24 hours with default period
# leia = AlanRobot(run_time=86400, period=10.0)  # Run for 24 hours with default period

usbPort1 = 4
usbPort2 = 5
usbPort3 = 6
usbPort4 = 7

ser1 = serial.Serial(usbPort1, 57600)
ser2 = serial.Serial(usbPort2, 57600)
ser3 = serial.Serial(usbPort3, 57600)
ser4 = serial.Serial(usbPort4, 57600)



# Step 1
sock = socket.socket()
ip = "127.0.0.1"
port = 1932
ticket = "myticket"
sock.connect((ip, port))


#

def read(threadName):
    a = sock.recv(1000)
    # print(a)
    if a == None:
        return ("No event")
    a = a.decode("utf-8")
    b = a.splitlines()
    for i in b:
        if i == "CONNECTED":
            print("Succesfully received, CONNECTED")
    for i in b:
        c = i.split()
        if (len(c) > 0 and len(b) > 1):
            if ((str(c[0]) == "EVENT" or str(c[0]) == "VENT" or str(c[0]) == "ENT") and (len(c) >= 3)):
                e = []
                d = b[1]
                e.append(c[1])
                e.append(d)
                return (e)


def send(threadName, sentence=""):
    sock.send(bytes(sentence, "utf-8"))
    print("Succesfully sent, ", sentence)


# Step 2
try:
    thread.start_new_thread(send, ("Send",))
    send("Send", "CONNECT myticket Python\n")
except:
    print ("Error: Could not start sending thread 1")
time.sleep(1)
#

# Step 3
try:
    thread.start_new_thread(read, ("Receive",))
    read("Receive")
except:
    print ("Error: Could not start receiving thread")
#

time.sleep(1)
# Step 4
send("Send",
     "SUBSCRIBE action.speech action.speech.stop\n")  # sense.user.enter sense.user.leave action.speech action.speech.stop\n")

interrupted = False

luke.start_simulation()
# leia.start_simulation()

while (1):
    time.sleep(0.1)
    a = read("Receive")
    event = None
    close = 0
    try:
        if a != None:
            # print(a[0])
            if (a[0] == "action.speech"):
                b = a[1].split(",")
                # print(b)
                for i in b:
                    i = str(i)
                    b = i.split(":")
                    b[0] = b[0][1:-1]
                    if (b[0] == "agent"):
                        b[1] = b[1][1:-1]
                        agent = b[1]
                        event = agent
                        # print(event)
                        if (event == "agent1" and interrupted == False):
                            motorMovementRobot1 = 1
                            motorMovementRobot2 = 0
                            ser1.write(bytes([49]))
                            time.sleep(0.01)
                            ser2.write(bytes([49]))
                            time.sleep(0.01)
                            ser3.write(bytes([48]))
                            time.sleep(0.01)
                            ser4.write(bytes([48]))
                            time.sleep(0.01)
                            # ser3.write(bytes([51]))
                            # ser3.write(bytes([101]))
                            # ser3.write(bytes([151]))
                            # ser4.write(bytes([51]))
                            # ser4.write(bytes([101]))
                            # ser4.write(bytes([151]))
                            # ser3.write(bytes([51]))
                            # ser3.write(bytes([101]))
                            # ser3.write(bytes([151]))
                            # ser4.write(bytes([51]))
                            # ser4.write(bytes([101]))
                            # ser4.write(bytes([151]))
                            print("agent1 speech sequence")
                        elif (event == "agent2" and interrupted == False):
                            motorMovementRobot1 = 0
                            motorMovementRobot2 = 1
                            # ser1.write(bytes([51]))
                            # ser1.write(bytes([101]))
                            # ser1.write(bytes([151]))
                            # ser2.write(bytes([51]))
                            # ser2.write(bytes([101]))
                            # ser2.write(bytes([151]))
                            ser1.write(bytes([48]))
                            time.sleep(0.01)
                            ser2.write(bytes([48]))
                            time.sleep(0.01)
                            ser3.write(bytes([49]))
                            time.sleep(0.01)
                            ser4.write(bytes([49]))
                            time.sleep(0.01)
                            print("agent2 speech sequence")
                    if (b[0] == "display"):
                        b[1] = b[1][1:-1]
                        if (b[1] == " hm what was i saying" or b[1] == " oh what were you saying?"):
                            event = "Interrupt completed"
                            interrupted = False
                            print(event)
            # elif (a[0] == "sense.user.enter"):
            # 	event = "userEntered"
            # 	print(event)
            # elif (a[0] == "sense.user.leave"):
            # 	event = "userLeft"
            # 	print(event)
            elif (a[0] == "action.speech.stop"):
                event = "Interrupted"
                interrupted = True
                ser1.write(bytes([50]))
                time.sleep(0.01)
                ser2.write(bytes([50]))
                time.sleep(0.01)
                ser3.write(bytes([48]))
                time.sleep(0.01)
                ser4.write(bytes([48]))
                time.sleep(0.01)
                # ser1.write(bytes([90]))
                # ser1.write(bytes([140]))
                # ser1.write(bytes([151]))
                # ser2.write(bytes([51]))
                # ser2.write(bytes([101]))
                # ser2.write(bytes([151]))
                # ser3.write(bytes([51]))
                # ser3.write(bytes([101]))
                # ser3.write(bytes([151]))
                # ser4.write(bytes([51]))
                # ser4.write(bytes([101]))
                # ser4.write(bytes([151]))
                print(event)
    except:
        pass
        # elif (event == "Interrupted" or event == "waiting3sec"):
    #	motorMovementRobot1 = 0
    #	motorMovementRobot2 = 0
    #	ser1.write(bytes([0]))
    # else:
    #	motorMovementRobot1 = 0
    #	motorMovementRobot2 = 0
    #	ser1.write(bytes([0]))

    # if motorMovementRobot1 == 1:
    #	ser1.write(bytes([49]))
    # else:
    #	ser1.write(bytes([48]))

    if (close):
        send("Send", "CLOSE\n")