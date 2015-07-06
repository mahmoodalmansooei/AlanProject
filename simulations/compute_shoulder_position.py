__author__ = 'Petrut Bogdan'

import nengo

l = 0.25
h = 0.2

upper_length = 0.3
lower_length = 0.35

radius = l + h + upper_length + lower_length

alpha = 1.
gamma = 0.1

b = 1.

model = nengo.Network("Computing positions")

with model:
    pass
