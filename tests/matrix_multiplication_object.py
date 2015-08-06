__author__ = 'Petrut Bogdan'

import nengo
import numpy as np

from robot_utils.matrix_multiplication import MatrixMultiplication

model = nengo.Network("MM Object Test", seed=len("SpiNNaker"))
radius = 1
A = np.asarray([[0, 0, -1], [0, 0, -1], [1, 1, 0]])
A = np.linspace(-1, 1, 9).reshape(3, 3)
A = np.linspace(-1, 1, 6).reshape(2, 3);radius = 2
B = np.asarray([[-1], [0], [1]])
B = np.linspace(-1, 1, 3).reshape(3, 1)

# A = np.asarray([[.5, -.5]])
# B = np.asarray([[0.58, -1.,], [.7, 0.1]])
with model:
    mm = MatrixMultiplication(50, A, B, radius=radius)

    inputA = nengo.Node(A.ravel())
    inputB = nengo.Node(B.ravel())

    nengo.Connection(inputA, mm.in_A)
    nengo.Connection(inputB, mm.in_B)
