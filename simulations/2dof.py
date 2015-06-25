__author__ = 'Petrut Bogdan'
import nengo
import numpy as np
from nengo.utils.functions import piecewise

"""
Script that simulates a 2 DOF arm rotating in order to reach an object in
a random location


"""

model = nengo.Network("2DOF Arm")

# Move the target to check that this simulation works as expected
movement_test = piecewise({0: [-1, -1], 5: [0, 0], 10: [1, 1], 15: [-1, 1],
                           20: [0.3, -0.3], 25: [-0.7, 0.0]})


def error(x, x_sensitivity=1.0, y_sensitivity=1.0):
    """
    Squared-error function. Also gives the required direction of movement
    :param x: A vector consisting of the target position [0, 1] and the current
    posotion [2, 3]
    :type x: float[4]
    :param x_sensitivity: Degree of sensitivity on the x axis -- higher values
    equate to higher response on the x axis
    :type x_sensitivity: float
    :param y_sensitivity: Degree of sensitivity on the y axis -- higher values
    equate to higher response on the y axis
    :type y_sensitivity: float
    :return: The correction needed to match the target
    :rtype: float
    """
    return x_sensitivity * np.sign(x[0] - x[2]) * ((x[0] - x[2]) ** 2), \
        y_sensitivity * np.sign(x[1] - x[3]) * ((x[1] - x[3]) ** 2)


with model:
    # Population radii           (found experimentally)
    radius = 1.1
    # Time constant for synapses (found experimentally)
    tau = 0.9
    # Node to input the initial orientation of the arm
    # Arm needs to be initialized to its initial position (reference position)
    initial_x = nengo.Node(output=piecewise({0: 1, 1: 0}))
    initial_y = nengo.Node(output=piecewise({0: 0.4, 1: 0}))
    # The ensemble representing the current orientation
    current_position = nengo.Ensemble(n_neurons=200, dimensions=2,
                                      radius=radius)
    # nengo.Connection(pre=initial_position, post=current_position)
    nengo.Connection(pre=initial_x, post=current_position[0])
    nengo.Connection(pre=initial_y, post=current_position[1])

    # Node to input the target position
    target_position_x = nengo.Node(piecewise({0: -1, 5: 0, 10: 1, 15: -1,
                                              20: .3, 25: -0.7}))
    target_position_y = nengo.Node(piecewise({0: -1, 5: 0, 10: 1, 15: 1,
                                              20: -0.3, 25: 0}))
    # The ensemble that combines the two signals (target and current
    # positions)
    controller = nengo.Ensemble(n_neurons=600, dimensions=4, radius=radius)
    nengo.Connection(pre=target_position_x, post=controller[0])
    nengo.Connection(pre=target_position_y, post=controller[1])
    nengo.Connection(pre=current_position[0], post=controller[2])
    nengo.Connection(pre=current_position[1], post=controller[3])
    # Ensemble that approximates the error function
    _error = nengo.Ensemble(n_neurons=400, dimensions=2, radius=1.5 * radius,
                            label="Error")
    nengo.Connection(pre=controller, post=_error, function=error)

    # Connections that feedback into current
    nengo.Connection(pre=_error, post=current_position,
                     transform=[[tau, 0], [0, tau]], synapse=tau)
    nengo.Connection(current_position, current_position, synapse=tau)

    # Simulated motor neurons
    x_motor = nengo.Ensemble(n_neurons=100, dimensions=1, radius=radius)
    y_motor = nengo.Ensemble(n_neurons=100, dimensions=1, radius=radius)

    nengo.Connection(pre=_error[0], post=x_motor, transform=[[tau]],
                     synapse=tau)
    nengo.Connection(pre=_error[1], post=y_motor, transform=[[tau]],
                     synapse=tau)
