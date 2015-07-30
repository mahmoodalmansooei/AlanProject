import nengo
import numpy as np
from nengo.utils.functions import piecewise
import robot_control.robot

robot_control.robot = reload(robot_control.robot)

model = nengo.Network(label="Entire robot test")

testing_hand_position = np.asarray(np.linspace(0, -1, 3))
with model:
    actions = nengo.Node(output=lambda t: [1, 0])
    lip_enable = nengo.Node(output=lambda t: [0])
    hand_position = nengo.Node(testing_hand_position.ravel())
    finger_enable = nengo.Node(output=lambda t: [0])
    head_position = nengo.Node(output=lambda t: [np.pi / 2, np.pi/6])

    mr_robot = robot_control.robot.Robot()

    nengo.Connection(actions, mr_robot.action.actions.input)
    nengo.Connection(lip_enable, mr_robot.action.lip_enable)
    nengo.Connection(hand_position, mr_robot.action.hand_position)
    nengo.Connection(finger_enable, mr_robot.action.finger_enable)
    nengo.Connection(head_position, mr_robot.action.head_position)
