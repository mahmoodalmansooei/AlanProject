__author__ = 'Petrut Bogdan'

import nengo
import numpy as np
from nengo.dists import Choice

l = 0.25
h = 0.2

upper_length = 0.3
lower_length = 0.35

radius = l + h + upper_length + lower_length

alpha = 1.
gamma = 0.1

beta = 1.

model = nengo.Network("Computing shoulder position")

position_mat = np.asarray([[0], [0], [0]])

shoulder_position_mat = np.asarray([[l], [0], [-h]])

rotation_mat = np.asarray(np.eye(3))

elbow_position_mat = np.asarray([0, upper_length, 0])

bottom_row = [0, 0, 0, 1]

N = 50

with model:
    # Angle values are in radians by default
    shoulder_angles = nengo.Node(output=lambda t: [alpha, gamma])

    # Shoulder
    shoulder = nengo.Node(output=shoulder_position_mat.ravel())
    S = nengo.networks.EnsembleArray(N, position_mat.size, radius=radius)
    nengo.Connection(shoulder, S.input)

    # Elbow
    elbow = nengo.Node(output=elbow_position_mat.ravel())
    E = nengo.networks.EnsembleArray(N, position_mat.size, radius=radius)
    nengo.Connection(elbow, E.input)

    # Rotation matrices
    Rx = nengo.networks.EnsembleArray(N, rotation_mat.size)

    nengo.Connection(shoulder_angles[0], Rx.input,
                     function=lambda x: [1, 0, 0,
                                         0, np.cos(x), -np.sin(x),
                                         0, np.sin(x), np.cos(x)])

    Ry = nengo.networks.EnsembleArray(N, rotation_mat.size)

    nengo.Connection(shoulder_angles[1], Ry.input,
                     function=lambda x: [np.cos(x), 0, np.sin(x),
                                         0, 1, 0,
                                         -np.sin(x), 0, np.cos(x)])

    combo = nengo.networks.EnsembleArray(N,
                                     n_ensembles=rotation_mat.size * rotation_mat.shape[1],
                                     ens_dimensions=2,
                                     radius=1.5 * radius,
                                     encoders=Choice(
                                         [[1, 1], [-1, 1], [1, -1], [-1, -1]]))

transformA = np.zeros((combo.dimensions, rotation_mat.size))
transformB = np.zeros((combo.dimensions, rotation_mat.size))

for i in range(rotation_mat.shape[0]):
    for j in range(rotation_mat.shape[1]):
        for k in range(rotation_mat.shape[1]):
            tmp = (j + k * rotation_mat.shape[1] + i * rotation_mat.size)
            transformA[tmp * 2][j + i * rotation_mat.shape[1]] = 1
            transformB[tmp * 2 + 1][k + j * rotation_mat.shape[1]] = 1

with model:
    # Check correct multiplication
    nengo.Connection(Ry.output, combo.input, transform=transformA)
    nengo.Connection(Rx.output, combo.input, transform=transformB)


with model:
    # Now compute the products and do the appropriate summing
    D = nengo.networks.EnsembleArray(N,
                                     n_ensembles=rotation_mat.shape[0] * rotation_mat.shape[1],
                                     radius=radius)

def product(x):
    return x[0] * x[1]

# The mapping for this transformation is much easier, since we want to
# combine D2 pairs of elements (we sum D2 products together)
transformC = np.zeros((9, 27))
for i in range(27):
    transformC[i // rotation_mat.shape[0]][i] = 1
# print("C->D")
# print(transformC)

with model:
    prod = combo.add_output("product", product)
    nengo.Connection(prod, D.input, transform=transformC)

