__author__ = 'Petrut Bogdan'

import nengo
import numpy as np
import robot_control.arm
from nengo.utils.functions import piecewise

robot_control.arm = reload(robot_control.arm)

model = nengo.Network("Arm movement test", seed=len("SpiNNaker"))

# l = 0.2
# h = 0.2
l = .5
h = .5

upper_length = .5
lower_length = .5

gamma = 0

shoulder_position = np.asarray([l, 0, -h])

lips_offset = np.asarray([0, .2, 0])

elbow_position = np.asarray([upper_length, 0, 0])

hand_position = np.asarray([0, lower_length, 0])

with model:
    target = nengo.Node(output=lips_offset.ravel())
    enabled = nengo.Node(output=piecewise({0: 1, 0.2: 0}))
    finger_enable = nengo.Node(output=0)
    arm = robot_control.arm.Arm(shoulder_position, elbow_position,
                                hand_position, gamma,
                                seed=len("SpiNNaker"))
    nengo.Connection(target, arm.target_position.input)
    nengo.Connection(enabled, arm.enable)
    nengo.Connection(finger_enable, arm.action_enable)
