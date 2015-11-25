__author__ = 'Petrut Bogdan'

import nengo
from nengo import Network
import numpy as np


class DotProduct(Network):
    def __init__(self, n_neurons=100, radius=1.0, dimensions=2,
                 label=None, seed=None,
                 add_to_container=None):
        """
        Dot product of 2 N dimensional vectors.

        :param n_neurons: The number of neurons.
        :type n_neurons: int defaults to 100
        :param radius: The range of values that can be represented
        :type radius: float
        :param dimensions: The number of dimensions in each vector.
        :type dimensions: int defaults to 2
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
        super(DotProduct, self).__init__(label, seed, add_to_container)
        self.n_neurons = n_neurons
        self.radius = radius
        self.dimensions = dimensions

        def product(x):
            return x[0] * x[1]

        with self:
            # Input to the network
            self.in_A = nengo.Node(size_in=self.dimensions)
            self.in_B = nengo.Node(size_in=self.dimensions)
            # Ensemble to multiply each respective dimension
            self.multiplier = nengo.networks.EnsembleArray(n_neurons=2 * self.n_neurons, n_ensembles=self.dimensions,
                                                           ens_dimensions=2)
            nengo.Connection(self.in_A, self.multiplier.input[[np.arange(self.dimensions) * 2]])
            nengo.Connection(self.in_B, self.multiplier.input[[np.arange(self.dimensions) * 2 + 1]])
            prod = self.multiplier.add_output("product", product)
            # Add all of the products together to give the final value (if normalised input is provided then the output
            # is the cosine between the two vectors)
            self.adder = nengo.Ensemble(n_neurons=self.n_neurons, dimensions=1)
            nengo.Connection(prod, self.adder, transform=[[1]* prod.size_out])
            # Output from the network
            self.output = nengo.Node(size_in=1)
            nengo.Connection(self.adder, self.output)


if __name__ == "__main__":
    dp = DotProduct()
