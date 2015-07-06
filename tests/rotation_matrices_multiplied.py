__author__ = 'Petrut Bogdan'
__author__ = 'Petrut Bogdan'


import nengo
import numpy as np
from robot_models.matrix_multiplication import  MatrixMultiplication

# Population radii should be computed based on the lengths involved

alpha = 1.
gamma = 0.1

model = nengo.Network("Rotation matrix multiplication")
rotation_mat = np.asarray(np.eye(3))
# bottom_row = [0, 0, 0, 1]

N = 50

with model:
    # Compute elbow position
    # Angle values are in radians by default
    shoulder_angles = nengo.Node(output=lambda t: [alpha, gamma])

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
