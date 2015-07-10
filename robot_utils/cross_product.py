__author__ = 'Petrut Bogdan'

import nengo
from nengo import Network
import numpy as np
from robot_utils.matrix_multiplication import MatrixMultiplication

_matrix = np.eye(3)
_vector = np.zeros((3, 1))


class CrossProduct(Network):
    def __init__(self, n_neurons, radius=1.0,
                 label=None, seed=None,
                 add_to_container=None, **ens_kwargs):
        """
        Cross product between two 3x1 vectors
        :param n_neurons:
        :type n_neurons:
        :param radius:
        :type radius:
        :param label:
        :type label:
        :param seed:
        :type seed:
        :param add_to_container:
        :type add_to_container:
        :param ens_kwargs:
        :type ens_kwargs:
        :return:
        :rtype:
        """
        super(CrossProduct, self).__init__(label, seed,
                                           add_to_container)
        self.config[nengo.Ensemble].update(ens_kwargs)
        self.n_neurons = n_neurons
        self.radius = radius

        with self:
            self.in_A = nengo.Node(size_in=_vector.size)
            self.in_B = nengo.Node(size_in=_vector.size)

            self.multiplier = MatrixMultiplication(n_neurons=self.n_neurons,
                                                   matrix_A=_matrix,
                                                   matrix_B=_vector,
                                                   radius=self.radius)

            nengo.Connection(self.in_A[0], self.multiplier.in_A[[0, 4, 8]],
                             transform=[[0]] * 3)
            nengo.Connection(self.in_A[0], self.multiplier.in_A[[7, 5]],
                             transform=[[1], [-1]])
            nengo.Connection(self.in_A[1], self.multiplier.in_A[[2, 6]],
                             transform=[[1], [-1]])
            nengo.Connection(self.in_A[2], self.multiplier.in_A[[3, 1]],
                             transform=[[1], [-1]])

            nengo.Connection(self.in_B, self.multiplier.in_B)

            self.output = nengo.Node(size_in=_vector.size)

            nengo.Connection(self.multiplier.output, self.output)
