__author__ = 'Petrut'

import nengo
import numpy as np

"""
Script that simulates a 1 DOF arm rotating in order to reach an object in
a random location

The point around which the "arm" rotates is the origin of the system (0,0)

First quadrant only
"""

model = nengo.Network("1dof -- square error(v4)")


def error(x):
    """
    Squared-error function. Also gives the required direction of movement
    :param x: A vector consisting of the target orientation [1] and the current
    number of degrees [0]
    :type x: float[2]
    :return: The correction needed to match the target
    :rtype: float
    """
    return np.sign(x[1] - x[0]) * (x[0] - x[1]) ** 2


with model:
    # Time constant for synapses (found experimentally)
    tau = 0.95
    # Population radii (found experimentally)
    radius = 1.2
    # Node to input the initial orientation of the arm TODO
    initial_angle = nengo.Node(0.0)
    # The ensemble representing the current orientation
    current = nengo.Ensemble(200, 1, radius=radius)

    nengo.Connection(initial_angle, current, transform=[0.01], synapse=tau)
    # Node to input the target angle (orientation)
    object_angle = nengo.Node(0.5)
    # The ensemble representing the target's orientation
    target = nengo.Ensemble(200, 1, radius=radius)

    nengo.Connection(object_angle, target)
    # The ensemble that combines the two signals (target and current
    # orientation)
    controller = nengo.Ensemble(400, 2, radius=radius)

    # Connections between the current --> controller and target --> controller
    nengo.Connection(current, controller[0])
    nengo.Connection(target, controller[1])

    # Ensemble that approximates the error function
    _error = nengo.Ensemble(200, 1, radius=radius)

    nengo.Connection(controller, _error, function=error)

    # Connections that feedback into current
    nengo.Connection(_error, current, transform=[[tau]], synapse=tau)
    nengo.Connection(current, current, transform=[[1]], synapse=tau)
