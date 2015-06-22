import nengo
from numpy import sign as sgn
from nengo.utils.functions import piecewise

model = nengo.Network(label="Signum")

with model:
    input = nengo.Node(piecewise({0:0, 2:1, 4:-1, 6:0.5, 8:-0.5, 10:0.25, 12:-0.25}))
    A = nengo.Ensemble(200, 1)
    sign = nengo.Ensemble(200, 1)

    nengo.Connection(input, A)
    nengo.Connection(A, sign, function=sgn)
