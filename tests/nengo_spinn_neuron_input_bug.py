__author__ = 'bogdanp'

import nengo
import nengo_spinnaker
import numpy as np

model = nengo.Network("Broken!")

with model:
    some_input = nengo.Node(np.sin)
    some_inhibition = nengo.Node(np.cos)

    A = nengo.networks.EnsembleArray(n_neurons=100, n_ensembles=1, ens_dimensions=1)
    inhibiting_input = A.add_neuron_input()

    nengo.Connection(some_input, A.input)
    nengo.Connection(some_inhibition, inhibiting_input, transform=[[-2.5]]*100)

sim = nengo_spinnaker.Simulator(model)

with sim:
    sim.run(1)
