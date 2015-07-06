__author__ = 'Petrut Bogdan'

import nengo
from robot_models.matrix_multiplication import MatrixMultiplication
import numpy as np

model = nengo.Network("MM Object Test")
A = np.asarray([[1]])
B = np.asarray([[-1, 1, -1]])
with model:
    mm = MatrixMultiplication(50, A, B)

    inputA = nengo.Node(A.ravel())
    inputB = nengo.Node(B.ravel())

    nengo.Connection(inputA, mm.input_A)
    nengo.Connection(inputB, mm.input_B)

