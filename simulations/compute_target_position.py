__author__ = 'Petrut Bogdan'
import nengo
import numpy as np
from nengo.utils.functions import piecewise

"""

"""

model = nengo.Network(label='Head rotation')

N = 100
Amat = np.asarray([[.5, -.5]])
Bmat = np.asarray([[0.58, -1.], [.7, 0.1]])

# Values should stay within the range (-radius,radius)
radius = 1

with model:
    # Make 2 EnsembleArrays to store the input
    A = nengo.networks.EnsembleArray(N, Amat.size, radius=radius)
    B = nengo.networks.EnsembleArray(N, Bmat.size, radius=radius)

    target_angle = nengo.Node(output=.45)  # Angle is in radians by default
    # connect inputs to them so we can set their value
    input_lips_location = nengo.Node(output=lambda t: [0, 1])
    nengo.Connection(input_lips_location, A.input)
    nengo.Connection(target_angle, B.input[0], function=np.cos)
    nengo.Connection(target_angle, B.input[1], function=lambda t: -np.sin(t))
    nengo.Connection(target_angle, B.input[2], function=np.sin)
    nengo.Connection(target_angle, B.input[3], function=np.cos)

from nengo.dists import Choice

with model:
    # The C matrix is composed of populations that each contain
    # one element of A and one element of B.
    # These elements will be multiplied together in the next step.

    # The appropriate encoders make the multiplication more accurate
    C = nengo.networks.EnsembleArray(N,
                                     n_ensembles=Amat.size * Bmat.shape[1],
                                     ens_dimensions=2,
                                     radius=1.5 * radius,
                                     encoders=Choice(
                                         [[1, 1], [-1, 1], [1, -1], [-1, -1]]))

transformA = np.zeros((C.dimensions, Amat.size))
transformB = np.zeros((C.dimensions, Bmat.size))

for i in range(Amat.shape[0]):
    for j in range(Amat.shape[1]):
        for k in range(Bmat.shape[1]):
            tmp = (j + k * Amat.shape[1] + i * Bmat.size)
            transformA[tmp * 2][j + i * Amat.shape[1]] = 1
            transformB[tmp * 2 + 1][k + j * Bmat.shape[1]] = 1

print("A->C")
print(transformA)
print("B->C")
print(transformB)

with model:
    nengo.Connection(A.output, C.input, transform=transformA)
    nengo.Connection(B.output, C.input, transform=transformB)

with model:
    # Now compute the products and do the appropriate summing
    D = nengo.networks.EnsembleArray(N,
                                     n_ensembles=Amat.shape[0] * Bmat.shape[1],
                                     radius=radius)


def product(x):
    return x[0] * x[1]

# The mapping for this transformation is much easier, since we want to
# combine D2 pairs of elements (we sum D2 products together)
transformC = np.zeros((D.dimensions, Bmat.size))
for i in range(Bmat.size):
    transformC[i // Bmat.shape[0]][i] = 1
print("C->D")
print(transformC)

with model:
    prod = C.add_output("product", product)
    print prod.size_in
    print prod.size_out
    nengo.Connection(prod, D.input, transform=transformC)
    D_probe = nengo.Probe(D.output, sample_every=0.01, synapse=0.01)
