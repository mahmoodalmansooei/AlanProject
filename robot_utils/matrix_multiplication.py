__author__ = 'Petrut Bogdan'

import nengo
import numpy as np
from nengo.dists import Choice


def product(x):
    return x[0] * x[1]


_matrix = np.eye(3)
_vector = np.zeros((3, 1))


class MatrixMultiplication(nengo.Network):
    def __init__(self, n_neurons, matrix_A=_matrix, matrix_B=_vector,
                 radius=1.0, label=None, seed=None,
                 add_to_container=None, **ens_kwargs):
        super(MatrixMultiplication, self).__init__(label, seed,
                                                   add_to_container)
        self.config[nengo.Ensemble].update(ens_kwargs)
        self.n_neurons = n_neurons
        self.radius = radius
        self.matrix_A = matrix_A
        self.matrix_B = matrix_B

        if self.matrix_A.shape[1] != self.matrix_B.shape[0]:
            raise ArithmeticError("Matrix dimensions must agree")

        with self:
            self.in_A = nengo.Node(size_in=matrix_A.size)
            self.in_B = nengo.Node(size_in=matrix_B.size)

            self.A = nengo.networks.EnsembleArray(self.n_neurons, matrix_A.size)
            self.B = nengo.networks.EnsembleArray(self.n_neurons, matrix_B.size)

            nengo.Connection(self.in_A, self.A.input)
            nengo.Connection(self.in_B, self.B.input)

            self.C = nengo.networks.EnsembleArray(
                self.n_neurons,
                n_ensembles=self.matrix_A.size * self.matrix_B.shape[1],
                ens_dimensions=2,
                radius=1.5 * radius,
                encoders=Choice([[1, 1], [-1, 1], [1, -1], [-1, -1]]))

        transform_a = np.zeros((self.C.dimensions, self.matrix_A.size))
        transform_b = np.zeros((self.C.dimensions, self.matrix_B.size))

        for i in range(self.matrix_A.shape[0]):
            for j in range(self.matrix_A.shape[1]):
                for k in range(self.matrix_B.shape[1]):
                    tmp = (
                        j + k * self.matrix_A.shape[1] + i * self.matrix_B.size)
                    transform_a[tmp * 2][j + i * self.matrix_A.shape[1]] = 1
                    transform_b[tmp * 2 + 1][k + j * self.matrix_B.shape[1]] = 1

        with self:
            nengo.Connection(self.A.output, self.C.input, transform=transform_a)
            nengo.Connection(self.B.output, self.C.input, transform=transform_b)

            self.D = nengo.networks.EnsembleArray(
                self.n_neurons,
                n_ensembles=self.matrix_A.shape[0] * self.matrix_B.shape[1],
                radius=radius)

        transform_c = np.zeros((self.D.dimensions,
                                self.matrix_A.size * self.matrix_B.shape[1]))
        for i in range(self.matrix_A.size * self.matrix_B.shape[1]):
            transform_c[i // self.matrix_B.shape[0]][i] = 1

        with self:
            prod = self.C.add_output("product", product)
            nengo.Connection(prod, self.D.input, transform=transform_c)

            self.output = nengo.Node(size_in=self.D.dimensions)
            nengo.Connection(self.D.output, self.output)
