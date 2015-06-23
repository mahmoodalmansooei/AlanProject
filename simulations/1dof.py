__author__ = 'Petrut Bogdan'

import nengo
import numpy as np

"""
Script that simulates a 1 DOF arm rotating in order to reach an object in
a random location

The point around which the "arm" rotates is the origin of the system (0,0)


"""

model = nengo.Network("1DOF Arm")

def error(x):
    """
    Squared-error function. Also gives the required direction of movement
    :param x: A vector consisting of the target orientation [1] and the current
    number of degrees [0]
    :type x: float[2]
    :return: The correction needed to match the target
    :rtype: float
    """
    return np.sign(x[1] - x[0]) * ((x[0] - x[1]) ** 2)


with model:
    # Time constant for synapses (found experimentally)
    tau = 0.95
    # Population radii           (found experimentally)
    radius = 1.2
    # Node to input the initial orientation of the arm
    # Arm needs to be initialized to its initial position (reference position)
    initial_angle = nengo.Node(output=0.0)
    # The ensemble representing the current orientation
    current = nengo.Ensemble(n_neurons=200, dimensions=1, radius=radius)
    nengo.Connection(pre=initial_angle, post=current, transform=[[tau]],
                     synapse=tau)
    # Node to input the target angle (orientation)
    object_angle = nengo.Node(output=0.5)
    # The ensemble representing the target's orientation
    target = nengo.Ensemble(n_neurons=200, dimensions=1, radius=radius)
    nengo.Connection(pre=object_angle, post=target)
    # The ensemble that combines the two signals (target and current
    # orientation)
    controller = nengo.Ensemble(n_neurons=500, dimensions=2, radius=radius)

    # Connections between the current --> controller and target --> controller
    nengo.Connection(pre=current, post=controller[0])
    nengo.Connection(pre=target,  post=controller[1])

    # Ensemble that approximates the error function
    _error = nengo.Ensemble(n_neurons=300, dimensions=1, radius=radius,
                            label="Error")

    _sensor = nengo.Ensemble(n_neurons=200, dimensions=1, radius=radius,
                             label="Sensor")
    _sensor_input = nengo.Node(output=0.0, label="Sensor input")
    nengo.Connection(pre=_sensor_input, post=_sensor)

    nengo.Connection(pre=_sensor, post=_error)
    nengo.Connection(pre=controller, post=_error, function=error)

    # Connections that feedback into current
    nengo.Connection(pre=_error,  post=current, transform=[[tau]], synapse=tau)
    nengo.Connection(pre=current, post=current, transform=[[1]],   synapse=tau)
