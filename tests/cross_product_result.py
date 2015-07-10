from robot_utils.cross_product import CrossProduct

__author__ = 'Petrut Bogdan'

import nengo
import numpy as np

model = nengo.Network("Connection test")
dimensions = 3
radius = 1.
n_neurons = 50

A = np.asarray([[1, -1, 0]])
B = np.asarray([[-1, 0, 1]])
with model:
    a = nengo.Node(output=A.ravel())
    b = nengo.Node(output=B.ravel())
    cp = CrossProduct(n_neurons, radius)

    nengo.Connection(a, cp.in_A)
    nengo.Connection(b, cp.in_B)
