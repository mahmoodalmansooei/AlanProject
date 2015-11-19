import nengo
import numpy as np
from nengo.utils.functions import piecewise
import robot_control.robot

robot_control.robot = reload(robot_control.robot)

model = nengo.Network(label="Entire robot test")

with model:
    mr_robot = robot_control.robot.Robot()

    left = nengo.Node([0,0,0])
    right = nengo.Node([0,0,0])

    nengo.Connection(left, mr_robot.left_target_position.input)
    nengo.Connection(right, mr_robot.right_target_position.input)

