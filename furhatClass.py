# send()
# recv()
import socket
import time
import thread
import serial
from robot_interface.alan_robot import AlanRobot
from scipy.interpolate import interp1d
import numpy as np

servo_to_com = dict()
index_to_range = {0: [51, 100], 1: [101, 150], 2: [151, 200]}
nengo_radius = 1

simulation_params_luke = {
    'hostname': '192.168.240.1',
    'width': 8,
    'height': 8
}

simulation_params_leia = {
    'hostname': '192.168.240.3',
    'width': 8,
    'height': 8
}

# TODO - Run booting etc. in parallel
luke = AlanRobot(run_time=86400,
                 period=10.0, **simulation_params_luke)  # Run for 24 hours with default period
# luke = AlanRobot(run_time=15, period=10.0)  # Run for 24 hours with default period
leia = AlanRobot(run_time=86400,
                 period=10.0, **simulation_params_leia)  # Run for 24 hours with default period

usbPort1 = 4
usbPort2 = 5
usbPort3 = 6
usbPort4 = 7

ser1 = serial.Serial(usbPort1, 57600)
ser2 = serial.Serial(usbPort2, 57600)
ser3 = serial.Serial(usbPort3, 57600)
ser4 = serial.Serial(usbPort4, 57600)

servo_to_com[
    AlanRobot.key_with_label_in_container("left_servos", luke.servos)] = ser1
servo_to_com[
    AlanRobot.key_with_label_in_container("right_servos", luke.servos)] = ser2

# servo_to_com[AlanRobot.key_with_label_in_container("left_servos", leia.servos)] = ser3
# servo_to_com[AlanRobot.key_with_label_in_container("right_servos", leia.servos)] = ser4

luke_moving = True

luke_action = np.asarray([1., 0.])
luke_direction = np.asarray([.7, .7])
luke_silence_position = np.asarray([.3, .7, 1])

leia_action = np.asarray([1., 0.])
leia_direction = np.asarray([.7, .7])
leia_silence_position = np.asarray([.3, .7, 1])


def transmission_callback(servo, data):
    '''
    Callback function that sends the relevant data sequentially to the respective controlling Arduinos.
    More specifically, the data in the servos from Nengo is linearly interpolated into the accepted range for that
    joint (by indexing into index_to_range and applying interp1d from scipy) and sending the rounded value down the
    serial point resulting from indexing the servo into servo_to_com.
    :param servo: robot_models.servo
    :param data: numpy.ndarray
    :return: None
    '''
    global index_to_range, servo_to_com, nengo_radius, luke_moving, luke, leia

    if servo in luke.servos.dictionary and luke_moving or \
                            servo in leia.servos.dictionary and not luke_moving:
        # value clipping [-1, 1]
        data = np.clip(data, -nengo_radius, nengo_radius)
        for index in xrange(data.size):
            servo_range = index_to_range[index]
            interpolation = interp1d([-nengo_radius, nengo_radius], servo_range)
            com_link = servo_to_com[servo]

            interpolated_output = int(interpolation(data))

            com_link.write(bytearray(
                [interpolated_output]
            ))


luke.servos.set_default_callback(transmission_callback)
# leia.servos.set_default_callback(transmission_callback)

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
            if ((str(c[0]) == "EVENT" or str(c[0]) == "VENT" or str(
                    c[0]) == "ENT") and (len(c) >= 3)):
                e = []
                d = b[1]
                e.append(c[1])
                e.append(d)
                return (e)


def send(threadName, sentence=""):
    sock.send(bytearray(sentence))
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

print("oh my life -------------")
time.sleep(10)  # <--
luke.start_simulation()
# leia.start_simulation()

while (1):
    time.sleep(0.1)
    a = read("Receive")
    event = None
    close = 0
    try:
        if a != None:
            if (a[0] == "action.speech"):
                b = a[1].split(",")
                for i in b:
                    i = str(i)
                    b = i.split(":")
                    b[0] = b[0][1:-1]
                    if (b[0] == "agent"):
                        b[1] = b[1][1:-1]
                        agent = b[1]
                        event = agent
                        if (event == "agent1" and interrupted == False):
                            # TODO pass input into neural sim
                            luke_moving = True
                            ser3.write(bytearray([48]))
                            time.sleep(0.01)
                            ser4.write(bytearray([48]))
                            time.sleep(0.01)
                            luke.gesture()

                            print("agent1 speech sequence")
                        elif (event == "agent2" and interrupted == False):
                            # TODO pass input into neural sim
                            luke_moving = False
                            ser1.write(bytearray([48]))
                            time.sleep(0.01)
                            ser2.write(bytearray([48]))
                            time.sleep(0.01)
                            leia.gesture()
                            print("agent2 speech sequence")
                    if (b[0] == "display"):
                        b[1] = b[1][1:-1]
                        if (b[1] == " hm what was i saying" or b[
                            1] == " oh what were you saying?"):
                            event = "Interrupt completed"
                            interrupted = False
                            print(event)
            elif (a[0] == "action.speech.stop"):
                event = "Interrupted"
                interrupted = True

                luke.silence()

                ser3.write(bytearray([48]))
                time.sleep(0.01)
                ser4.write(bytearray([48]))
                time.sleep(0.01)
                print(event)
    except:
        pass

    if (close):
        send("Send", "CLOSE\n")
