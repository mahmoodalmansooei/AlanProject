__author__ = 'Petrut Bogdan'

import nengo
import numpy as np
from numpy import sign as sgn

"""
Action selection achieved by using a basal ganglia implementation

|Currently considered robot actions:
\
 |-Talking to another robot
 |-Silencing the crowd
 |-Talk to approaching human
"""

model = nengo.Network("Action selector")

with model:
    d = 5
    basal_ganglia = nengo.networks.BasalGanglia(dimensions=3)
    control_signal = nengo.Node([0] * d, label="actions")
    nengo.Connection(control_signal[0:3], basal_ganglia.input, synapse=None)



# Action 1 execution
with model:
    input = nengo.Node(output=lambda t: np.sin(t))
    A = nengo.Ensemble(200, 1)
    sign = nengo.Ensemble(200, 1)

    nengo.Connection(input, A)
    nengo.Connection(A, sign, function=sgn)

# Action 2 execution
with model:
    radius = 3.0
    tau = 0.1
    in_value = nengo.Node(output=lambda t: np.abs(np.sin(t)))

    diff_control = nengo.Ensemble(n_neurons=200, dimensions=1)


    differentiator = nengo.Ensemble(n_neurons=400, dimensions=2, radius=radius)

    output = nengo.Ensemble(n_neurons=400, dimensions=1, radius=1.8)
    nengo.Connection(in_value, diff_control)
    nengo.Connection(diff_control, differentiator[0])
    nengo.Connection(differentiator[0], differentiator[1], synapse=tau)

    nengo.Connection(differentiator, output, transform=[[1 / tau, -1 / tau]], synapse=tau)

    # Integrate the differentiation (should reconstruct the initial signal)

    integrator = nengo.Ensemble(n_neurons=400, dimensions=1)
    nengo.Connection(integrator, integrator, transform=[[1]], synapse=tau)
    nengo.Connection(output, integrator, transform=[[tau]], synapse=tau)


# Connecting the model
with model:
    nengo.Connection(basal_ganglia.output[0], A.neurons, transform=[[1.]]*A.n_neurons)
    nengo.Connection(basal_ganglia.output[1], diff_control.neurons, transform=[[1.]]*diff_control.n_neurons)