from nengo.processes import WhiteNoise

__author__ = 'bogdanp'

import nengo
import nengo.spa as spa
import numpy as np

dimensions = 64  # the dimensionality of the vectors


model = spa.SPA()
with model:
    model.cortex = spa.Buffer(dimensions=dimensions, neurons_per_dimension=100)
    model.motor = spa.Buffer(dimensions=dimensions, neurons_per_dimension=100)
    model.buffer = spa.Buffer(dimensions=dimensions, neurons_per_dimension=100)
    # model.buffer2 = spa.Buffer(dimensions=dimensions, neurons_per_dimension=100)
    model.direction = spa.Memory(dimensions=dimensions, tau=0.01)
    # model.time = nengo.networks.Oscillator(1, 1, 500)
    # model.perceived_time = spa.Memory(dimensions=dimensions, tau=0.1)
    # Specify the action mapping
    actions = spa.Actions(
        '.8 * dot(cortex, S) + dot(buffer, L)--> motor = LS, cortex = S',
        '.8 * dot(cortex, S) + dot(buffer, R)--> motor = RS, cortex = S',
        '.8 * dot(cortex, G) + dot(buffer, L)--> motor = LG, cortex = G',
        '.8 * dot(cortex, G) + dot(buffer, R)--> motor = RG, cortex = G',
    )

    cortical_actions = spa.Actions(
        'buffer= buffer + .1 * direction '
    )
    model.cortical = spa.Cortical(cortical_actions)

    model.bg = spa.BasalGanglia(actions=actions)
    model.thal = spa.Thalamus(model.bg)


def start(t):
    if t < 0.1:
        return 'G'
    else:
        return '0'

def update_direction(_):
    if np.random.rand(1) > 0.5:
        return 'L'
    else:
        return 'R'

with model:
    model.input = spa.Input(cortex=start)
    model.rand_input = spa.Input(direction=update_direction)
