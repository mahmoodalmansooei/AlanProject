__author__ = 'Petrut Bogdan'

import nengo
import numpy as np

model = nengo.Network("Abs")

with model:
    sine = nengo.Node(output=np.sin)
    output = nengo.Ensemble(200, 1)
    nengo.Connection(sine, output, function=np.abs)