__author__ = 'Petrut Bogdan'

import nengo
import numpy as np

model = nengo.Network("Rotation")

with model:
    tau = 0.1
    x_in = nengo.Node(output=np.sin)
    y_in = nengo.Node(output=np.cos)
    rotation = nengo.Ensemble(n_neurons=300, dimensions=2, radius=1.2)

    output = nengo.Ensemble(n_neurons=300, dimensions=2, radius=1.2)
    nengo.Connection(x_in, rotation[0])
    nengo.Connection(y_in, rotation[1])
    nengo.Connection(rotation, output, transform=[[-1, 0], [0, -1]])
