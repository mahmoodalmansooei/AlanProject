__author__ = 'Petrut Bogdan'

import nengo
import numpy as np

l = 0.25
h = 0.2

upper_length = 0.3
lower_length = 0.35

radius = l + h + upper_length + lower_length

alpha = 1.
gamma = 0.1

b = 1.

model = nengo.Network("Computing shoulder position")

shoulder_mat = np.asarray([[l],[0],[-h],[0]])
with model:
    shoulder = nengo.Node(output=shoulder_mat.ravel())
    S = nengo.networks.EnsembleArray(50, shoulder_mat.size, radius=1)

    nengo.Connection(shoulder, S.input)
