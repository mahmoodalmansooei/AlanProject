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


class ActionIterator(object):
    def __init__(self, dimensions):
        self.actions = np.ones(dimensions) * 0.1

    def step(self, t):
        # one action at time dominates
        dominate = int(t % 3)
        self.actions[:] = 0.1
        self.actions[dominate] = 0.8
        return self.actions


action_iterator = ActionIterator(dimensions=3)

model = nengo.Network("Action selector")

with model:
    d = 5
    basal_ganglia = nengo.networks.BasalGanglia(dimensions=3)
    control_signal = nengo.Node([0] * d, label="actions")
    nengo.Connection(control_signal[0:3], basal_ganglia.input, synapse=None)



# Action 1 execution
with model:
    pass

# Action 2 execution
with model:
    pass

# Action 3 execution
with model:
    pass

# Connecting the model
with model:
    pass
