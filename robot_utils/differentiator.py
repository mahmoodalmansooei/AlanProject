import nengo


class Differentiator(nengo.Network):
    def __init__(self, n_neurons,
                 radius=1.0, tau=0.1,
                 label=None, seed=None,
                 add_to_container=None, **ens_kwargs):
        super(Differentiator, self).__init__(label, seed,
                                             add_to_container)
        # region Variable assignment
        self.config[nengo.Ensemble].update(ens_kwargs)
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
