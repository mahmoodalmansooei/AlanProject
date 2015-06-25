__author__ = 'Petrut Bogdan'

import nengo
import numpy as np

model = nengo.Network("Differentiator")

with model:
    radius = 3.0
    tau = 0.1
    in_value = nengo.Node(output=np.sin)

    differentiator = nengo.Ensemble(n_neurons=400, dimensions=2, radius=radius)

    output = nengo.Ensemble(n_neurons=400, dimensions=1, radius=1.8)
    nengo.Connection(in_value, differentiator[0])
    nengo.Connection(differentiator[0], differentiator[1], synapse=tau)

    nengo.Connection(differentiator, output, transform=[[1 / tau, -1 / tau]], synapse=tau)

# Integrate the differentiation (should reconstruct the initial signal)
with model:
    integrator = nengo.Ensemble(n_neurons=400, dimensions=1)
    nengo.Connection(integrator, integrator, transform=[[1]], synapse=tau)
    nengo.Connection(output, integrator, transform=[[tau]], synapse=tau)
