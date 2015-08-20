__author__ = 'Petrut Bogdan'

import nengo
import numpy as np
from nengo.dists import Choice


def product(x):
    return x[0] * x[1]


class MatrixMultiplication(nengo.Network):
    def __init__(self, n_neurons=100, matrix_A=np.eye(3), matrix_B=np.zeros((3, 1)),
                 radius=1.0, label=None, seed=None,
                 add_to_container=None):

        """
        A network that does matrix multiplication based on two previously
        provided matrices that have the same shapes as the ones to be
        multiplied. For a more detailed presentation see this_ Nengo
        example.

        .. _this: https://pythonhosted.org/nengo/examples/matrix_multiplication.html

        :param n_neurons: The number of neurons.
        :type n_neurons: int
        :param matrix_A: A matrix that looks like the first one to be multiplied
            (the shape is the same, values are irrelevant)
        :type matrix_A: numpy.ndarray
        :param matrix_B: A matrix that looks like the first one to be multiplied
            (the shape is the same, values are irrelevant)
        :type matrix_B: numpy.ndarray
        :param radius: The min and max value to be represented
        :type radius: float
        :param label: Name of the model. Defaults to None.
        :type label: str
        :param seed: Random number seed that will be fed to the random
            number generator. Setting this seed makes the creation of the
            model a deterministic process; however, each new ensemble
            in the network advances the random number generator, so if
            the network creation code changes, the entire model changes.
        :type seed: int
        :param add_to_container: Determines if this Network will be added to
            the current container. Defaults to true iff currently with a Network
        :type add_to_container: bool
        """
        super(MatrixMultiplication, self).__init__(label, seed,
                                                   add_to_container)
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
