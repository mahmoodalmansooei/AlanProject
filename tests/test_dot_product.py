import robot_utils.dot_product
robot_utils.dot_product = reload(robot_utils.dot_product)


__author__ = 'bogdanp'

import nengo
import numpy as np

model = nengo.Network("Dot Product")

with model:
    A = nengo.Node([0.5, 0.5])
    B = nengo.Node([0.5, -0.5])

    dp = robot_utils.dot_product.DotProduct()

    nengo.Connection(A, dp.in_A)
    nengo.Connection(B, dp.in_B)


