import nengo
from nengo.utils.functions import piecewise
import numpy as np

model = nengo.Network(label="Signum")

with model:
    input = nengo.Node(piecewise({0:0, 2:1, 4:-1, 6:0.5, 8:-0.5, 10:0.25, 12:-0.25}))
    A = nengo.Ensemble(400, 1)
    sign = nengo.Ensemble(400, 1)
    sign2 = nengo.Ensemble(400,1)

    nengo.Connection(input, A)
    nengo.Connection(A, sign, function=lambda x: np.sign(x), synapse=1)
    nengo.Connection(sign, sign2, function=np.sign, synapse=0.01)
