from __future__ import print_function
import nengo
import numpy as np
from nengo.utils.functions import piecewise
import robot_control.robot
import nengo_spinnaker

robot_control.robot = reload(robot_control.robot)

model = nengo.Network(label="Entire robot test")

with model:
    mr_robot = robot_control.robot.Robot()

    # mr_robot.servos.set_default_callback(lambda k, v: print(k, "->", v))

if __name__ == "__main__":
    sim = nengo_spinnaker.Simulator(model)
    with sim:
        sim.run(3)
