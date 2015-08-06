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
        A = nengo.Ensemble(40, 1)
        output_val = nengo.Node(size_in=1)
        nengo.Connection(A, output_val)

    sine = nengo.Node(output=np.sin)
    nengo.Connection(sine, A)

