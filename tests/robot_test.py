import nengo
import numpy as np
from nengo.utils.functions import piecewise
import robot_control.robot

robot_control.robot = reload(robot_control.robot)

model = nengo.Network(label="Entire robot test")

with model:
    mr_robot = robot_control.robot.Robot()

