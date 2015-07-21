__author__ = 'Petrut Bogdan'

import nengo
import numpy as np
import robot_utils.differentiator

robot_utils.differentiator = reload(robot_utils.differentiator)

model = nengo.Network("Differentiator")

with model:
    radius = 3.0
    tau = 0.1
    some_function = nengo.Node(output=lambda x: np.sin(x))
    differentiator = robot_utils.differentiator.Differentiator(
        200,
        radius=radius,
        tau=tau,
        label="Diff module")
    nengo.Connection(some_function, differentiator.input)

# Integrate the differentiation (should reconstruct the initial signal)
with model:
    integrator = nengo.Ensemble(n_neurons=400, dimensions=1)
    nengo.Connection(integrator, integrator, transform=[[1]], synapse=tau)
    nengo.Connection(differentiator.output, integrator, transform=[[tau]],
                     synapse=tau)
