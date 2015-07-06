import nengo
import numpy as np

model = nengo.Network("Rotation")

with model:
    tau = 0.1
    xy_in = nengo.Node(output=lambda t: [np.sin(t), np.cos(t)])
    rotation = nengo.Ensemble(n_neurons=300, dimensions=2, radius=1.2)

    output = nengo.Ensemble(n_neurons=300, dimensions=2, radius=1.2)
    nengo.Connection(xy_in, rotation)
    nengo.Connection(rotation, output, transform=[[-1, 0], [0, -1]])