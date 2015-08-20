import nengo


class Differentiator(nengo.Network):
    def __init__(self, n_neurons=100,
                 radius=1.0, tau=0.1,
                 label=None, seed=None,
                 add_to_container=None):
        """
        This network takes as input a signal (function of time) and outputs
        the differentiated result (the slope of the signal).

        The opposite of an :py:func:`~nengo.networks.Integrator`.

        Applying :py:func:`~nengo.networks.Integrator` on the output of the
        Differentiator will result in an approximation of the original signal.

        :param n_neurons: The number of neurons.
        :type n_neurons: int
        :param radius: The range of values that can be represented
        :type radius: float
        :param tau: post synaptic time constant
        :type tau: float
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
        super(Differentiator, self).__init__(label, seed,
                                             add_to_container)
        # region Variable assignment
        self.n_neurons = n_neurons
        self.radius = radius
        self.tau = tau
        # endregion
        with self:
            self.input = nengo.Node(size_in=1)

            self.differentiator = nengo.Ensemble(n_neurons=self.n_neurons,
                                                 dimensions=2,
                                                 radius=self.radius)

            self.output = nengo.Node(size_in=1)
            nengo.Connection(self.input, self.differentiator[0])
            nengo.Connection(self.differentiator[0], self.differentiator[1],
                             synapse=self.tau)

            nengo.Connection(self.differentiator, self.output,
                             transform=[[1 / self.tau, -1 / self.tau]],
                             synapse=self.tau)
