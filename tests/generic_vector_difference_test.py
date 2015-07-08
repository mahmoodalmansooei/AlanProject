__author__ = 'Petrut Bogdan'

import nengo
from nengo import Network
import numpy as np
from robot_models.vector_difference import VectorDifference

myseed = len("SpiNNaker")
model = nengo.Network("Vector difference test", seed=myseed)

with model:
    A = nengo.Node(output=lambda t: [0, .4, .3])
    B = nengo.Node(output=lambda t: [0, .4, .3])
    D = VectorDifference(50, 3, seed=myseed)
    nengo.Connection(A, D.in_A)
    nengo.Connection(B, D.in_B)
