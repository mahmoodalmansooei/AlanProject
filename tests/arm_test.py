__author__ = 'Petrut Bogdan'

import nengo
import numpy as np
import robot_control.arm
from nengo.utils.functions import piecewise

robot_control.arm = reload(robot_control.arm)

model = nengo.Network("Arm movement test", seed=len("SpiNNaker"))

l = 0.25
h = 0.2

upper_length = 0.3
lower_length = 0.35

# gamma = np.pi / 4
gamma = 0

shoulder_position = np.asarray([l, 0, -h])

lips_offset = np.asarray([0, .2, 0])

# elbow_position = np.asarray([0, upper_length, 0])
elbow_position = np.asarray([0, upper_length, 0])

hand_position = np.asarray([0, lower_length, 0])

with model:
    target = nengo.Node(output=lips_offset.ravel())
    # enabled = nengo.Node(output=piecewise({0: 1, 2: 0}))
    arm = robot_control.arm.Arm(shoulder_position, elbow_position,
                                hand_position, gamma,
                                seed=len("SpiNNaker"))

    shoulder_alpha = nengo.Node(output=np.pi / 2)
    nengo.Connection(shoulder_alpha, arm.alpha_angle)

    elbow_beta = nengo.Node(output=np.pi / 2)
    nengo.Connection(elbow_beta, arm.beta_angle)
    # nengo.Connection(target, head.target_position)
    # nengo.Connection(enabled, head.enable)
