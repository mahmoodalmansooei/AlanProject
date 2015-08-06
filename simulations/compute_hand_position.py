__author__ = 'Petrut Bogdan'

import nengo
import numpy as np
from nengo.dists import Choice

l = 0.25
h = 0.2

upper_length = 0.3
lower_length = 0.35

# Population radii should be computed based on the lengths involved
radius = l + h + upper_length + lower_length

alpha = 1.
gamma = 0.1

beta = 1.

model = nengo.Network("Computing hand position")

position_mat = np.asarray([0, 0, 0])

shoulder_position_mat = np.asarray([l, 0, -h])

rotation_mat = np.asarray(np.eye(3))

elbow_position_mat = np.asarray([[0, upper_length, 0]])

hand_position_mat = np.asarray([[0, lower_length, 0]])
# bottom_row = [0, 0, 0, 1]

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
                                         n_ensembles=rotation_mat.size *
                                                     rotation_mat.shape[1],
                                         ens_dimensions=2,
                                         radius=1.5 * radius,
                                         encoders=Choice(
                                             [[1, 1], [-1, 1], [1, -1],
                                              [-1, -1]]))

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
    D = nengo.networks.EnsembleArray(
        N, n_ensembles=rotation_mat.shape[0] * rotation_mat.shape[1],
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

# Compute the position of the elbow in relation to the shoulder
# This involves multiplying the position vector of the elbow by the rotation
# matrix of the shoulder frame

with model:
    elbow_combo = nengo.networks.EnsembleArray(
        N, n_ensembles=elbow_position_mat.size * rotation_mat.shape[1],
        ens_dimensions=2,
        radius=1.5 * radius,
        encoders=Choice([[1, 1], [-1, 1], [1, -1], [-1, -1]]))

transformElbow = np.zeros((elbow_combo.dimensions, elbow_position_mat.size))
transformRotation = np.zeros((elbow_combo.dimensions, rotation_mat.size))

for i in range(elbow_position_mat.shape[0]):
    for j in range(elbow_position_mat.shape[1]):
        for k in range(rotation_mat.shape[1]):
            tmp = (j + k * elbow_position_mat.shape[1] + i * rotation_mat.size)
            transformElbow[tmp * 2][j + i * elbow_position_mat.shape[1]] = 1
            transformRotation[tmp * 2 + 1][k + j * rotation_mat.shape[1]] = 1

with model:
    nengo.Connection(E.output, elbow_combo.input, transform=transformElbow)
    nengo.Connection(D.output, elbow_combo.input, transform=transformRotation)
    elbow_in_upper_arm_space = nengo.networks.EnsembleArray(
        N, n_ensembles=elbow_position_mat.shape[0] * rotation_mat.shape[1],
        radius=radius)

transformElbow2 = np.zeros((elbow_in_upper_arm_space.dimensions, rotation_mat.size))
for i in range(rotation_mat.size):
    transformElbow2[i // rotation_mat.shape[0]][i] = 1

with model: # TODO Check that this outputs correct values
    prod2 = elbow_combo.add_output("product", product)
    nengo.Connection(prod2, elbow_in_upper_arm_space.input, transform=transformElbow2)


# World space position computation

with model:
    elbow_in_world_space = nengo.networks.EnsembleArray(N, n_ensembles=3, radius=2 * radius)

    nengo.Connection(elbow_in_upper_arm_space.output, elbow_in_world_space.input)
    nengo.Connection(S.output, elbow_in_world_space.input)


# Hand bit

with model:
    hand_position = nengo.Node(output=hand_position_mat.ravel())

    hand_in_world_space = nengo.networks.EnsembleArray(N, n_ensembles=3, radius=2 * radius)

    nengo.Connection(elbow_in_world_space.output, hand_in_world_space.input)
    nengo.Connection(hand_position, hand_in_world_space.input)

