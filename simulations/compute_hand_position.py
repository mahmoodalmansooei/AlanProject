__author__ = 'Petrut Bogdan'


import nengo
import numpy as np
from nengo.dists import Choice
from robot_models.matrix_multiplication import  MatrixMultiplication

l = 0.25
h = 0.2

upper_length = 0.3
lower_length = 0.35

# Population radii should be computed based on the lengths involved
radius = l + h + upper_length + lower_length

alpha = 1.
gamma = 0.1

beta = 1.

model = nengo.Network("Computing shoulder position")

position_mat = np.asarray([0, 0, 0])

shoulder_position_mat = np.asarray([l, 0, -h])

rotation_mat = np.asarray(np.eye(3))

elbow_position_mat = np.asarray([[0, upper_length, 0]])

# bottom_row = [0, 0, 0, 1]

N = 50

with model:
    # Compute elbow position
    # Angle values are in radians by default
    shoulder_angles = nengo.Node(output=lambda t: [alpha, gamma])

    # Shoulder
    shoulder = nengo.Node(output=shoulder_position_mat.ravel())
    S = nengo.networks.EnsembleArray(N, position_mat.size, radius=radius)
    nengo.Connection(shoulder, S.input)

    # Elbow
    elbow = nengo.Node(output=elbow_position_mat.ravel())
    E = nengo.networks.EnsembleArray(N, position_mat.size, radius=radius)
    nengo.Connection(elbow, E.input)

    # Rotation matrices
    rotation_mm = MatrixMultiplication(N, rotation_mat, rotation_mat)

    nengo.Connection(shoulder_angles[0], rotation_mm.input_A,
                     function=lambda x: [1, 0, 0,
                                         0, np.cos(x), -np.sin(x),
                                         0, np.sin(x), np.cos(x)])

    nengo.Connection(shoulder_angles[1], rotation_mm.input_B,
                     function=lambda x: [np.cos(x), 0, np.sin(x),
                                         0, 1, 0,
                                         -np.sin(x), 0, np.cos(x)])
