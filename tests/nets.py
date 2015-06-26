__author__ = 'Petrut Bogdan'

"""
Learning how to use nets to group structures
"""
import nengo
import numpy as np

model = nengo.Network("Network of networks")
with model:
    net1 = nengo.Network("Subnet")
    with net1:
        net1.input_value = nengo.Node(size_in=1)
        net1.A = nengo.Ensemble(40, 1)
        net1.output_val = nengo.Node(size_in=1)

        nengo.Connection(net1.input_value, net1.A)
        nengo.Connection(net1.A, net1.output_val, function=lambda x: -x)

    net1.input = net1.input_value
    net1.output = net1.output_val

    sine = nengo.Node(output=np.sin)
    nengo.Connection(sine, net1.input, synapse=None)