from nengo.utils.functions import piecewise

__author__ = 'bogdanp'

import nengo
import nengo.spa as spa

model = nengo.Network("Oscillator network")

with model:
    input = nengo.Node(piecewise({0: [1, 0], 0.1: [0, 0]}))
    osc = nengo.networks.Oscillator(1, 1, 100)
    nengo.Connection(input, osc.input)


