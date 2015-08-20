__author__ = 'Petrut Bogdan'

import nengo
from nengo import Network


class VectorDifference(Network):
    def __init__(self, n_neurons, dimensions, radius=1.0,
                 label=None, seed=None,
                 add_to_container=None, **ens_kwargs):
        """
        Module that computes the difference between two vectors of the same
        dimension. In a mathematical, vectorial sense, A - B computes the vector
        pointing from B to A.

        :param n_neurons: numbered of neurons used to represent each value
        :type n_neurons: int
        :param dimensions: the number of dimensions in each vector
        :type dimensions: int
        :param radius: value representable by the ensembles
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
        super(VectorDifference, self).__init__(label, seed,
                                               add_to_container)
        self.config[nengo.Ensemble].update(ens_kwargs)

        self.n_neurons = n_neurons
        self.dimensions = dimensions
        self.radius = radius

        with self:
            self.in_A = nengo.Node(size_in=self.dimensions)
            self.in_B = nengo.Node(size_in=self.dimensions)

            self.A = nengo.networks.EnsembleArray(
                n_neurons=self.n_neurons, n_ensembles=self.dimensions,
                radius=radius)

            self.B = nengo.networks.EnsembleArray(
                n_neurons=self.n_neurons, n_ensembles=self.dimensions,
                radius=radius)

            nengo.Connection(self.in_A, self.A.input)
            nengo.Connection(self.in_B, self.B.input)

            self.S = nengo.networks.EnsembleArray(
                n_neurons=self.n_neurons, n_ensembles=self.dimensions,
                radius=2 * self.radius)

            nengo.Connection(self.A.output, self.S.input,
                             transform=[1.] * self.dimensions)
            nengo.Connection(self.B.output, self.S.input,
                             transform=[-1.] * self.dimensions)

            self.output = nengo.Node(size_in=self.dimensions)
            nengo.Connection(self.S.output, self.output)
