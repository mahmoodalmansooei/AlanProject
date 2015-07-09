from nengo.dists import Choice

__author__ = 'Petrut Bogdan'

import nengo
import numpy as np

def product(x):
    return x[0] * x[1]

class MatrixMultiplication(nengo.Network):
    def __init__(self, n_neurons, matrix_A, matrix_B, radius=1.0,
                 label=None, seed=None,
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
            # The C matrix is composed of populations that each contain
            # one element of A and one element of B.
            # These elements will be multiplied together in the next step.
            self.C = nengo.networks.EnsembleArray(
                self.n_neurons,
                n_ensembles=self.matrix_A.size * self.matrix_B.shape[1],
                ens_dimensions=2,
                radius=1.5 * radius,
                encoders=Choice([[1, 1], [-1, 1], [1, -1], [-1, -1]]))

        # Determine the transformation matrices to get the correct pairwise
        # products computed.  This looks a bit like black magic but if
        # you manually try multiplying two matrices together, you can see
        # the underlying pattern.  Basically, we need to build up D1*D2*D3
        # pairs of numbers in C to compute the product of.  If i,j,k are the
        # indexes into the D1*D2*D3 products, we want to compute the product
        # of element (i,j) in A with the element (j,k) in B.  The index in
        # A of (i,j) is j+i*D2 and the index in B of (j,k) is k+j*D3.
        # The index in C is j+k*D2+i*D2*D3, multiplied by 2 since there are
        # two values per ensemble.  We add 1 to the B index so it goes into
        # the second value in the ensemble.
        transformA = np.zeros((self.C.dimensions, self.matrix_A.size))
        transformB = np.zeros((self.C.dimensions, self.matrix_B.size))

        for i in range(self.matrix_A.shape[0]):
            for j in range(self.matrix_A.shape[1]):
                for k in range(self.matrix_B.shape[1]):
                    tmp = (
                        j + k * self.matrix_A.shape[1] + i * self.matrix_B.size)
                    transformA[tmp * 2][j + i * self.matrix_A.shape[1]] = 1
                    transformB[tmp * 2 + 1][k + j * self.matrix_B.shape[1]] = 1

        print("A->C")
        print(transformA)
        print("B->C")
        print(transformB)

        with self:
            nengo.Connection(self.A.output, self.C.input, transform=transformA)
            nengo.Connection(self.B.output, self.C.input, transform=transformB)

            self.D = nengo.networks.EnsembleArray(
                self.n_neurons,
                n_ensembles=self.matrix_A.shape[0] * self.matrix_B.shape[1],
                radius=radius)

        transformC = np.zeros((self.D.dimensions,
                               self.matrix_A.size * self.matrix_B.shape[1]))
        for i in range(self.matrix_A.size * self.matrix_B.shape[1]):
            transformC[i // self.matrix_B.shape[0]][i] = 1
        print("C->D")
        print(transformC)

        with self:
            prod = self.C.add_output("product", product)

            nengo.Connection(prod, self.D.input, transform=transformC)