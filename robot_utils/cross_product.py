__author__ = 'Petrut Bogdan'

import nengo
from nengo import Network
import numpy as np
from robot_utils.matrix_multiplication import MatrixMultiplication

_matrix = np.eye(3)
_vector = np.zeros((3, 1))


class CrossProduct(Network):
    def __init__(self, n_neurons=100, radius=1.0,
                 label=None, seed=None,
                 add_to_container=None):
        """
        Cross product between two 3x1 vectors.

        :param n_neurons: The number of neurons.
        :type n_neurons: int defaults to 100
        :param radius: The range of values that can be represented
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
        super(CrossProduct, self).__init__(label, seed,
                                           add_to_container)
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
