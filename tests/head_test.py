__author__ = 'Petrut Bogdan'

import nengo
import numpy as np
import robot_control.head
from nengo.utils.functions import piecewise


robot_control.head = reload(robot_control.head)

model = nengo.Network("Head movement test", seed=len("SpiNNaker"))

lips_offset = np.asarray([0, .2, 0])

with model:
    target = nengo.Node(output=lambda t: [np.pi / 2, np.pi / 4])
    enabled = nengo.Node(output=piecewise({0: 1, 2: 0}))
    # enabled = nengo.Node(output=0)
    head = robot_control.head.Head(lips_offset)
    nengo.Connection(target, head.target_position)
    nengo.Connection(enabled, head.enable)
