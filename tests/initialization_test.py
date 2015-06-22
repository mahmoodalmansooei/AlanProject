__author__ = 'Petrut'

import nengo
from nengo.utils.functions import piecewise

model = nengo.Network("Initialization test")

with model:
    A = nengo.Ensemble(50, 1)

    inhib = nengo.Node(output=piecewise({0: 1, 1: 0}))

    init = nengo.Node(output=0.5)

    nengo.Connection(init, A)
    nengo.Connection(inhib, A.neurons, transform=[[-2.5]]*A.n_neurons)