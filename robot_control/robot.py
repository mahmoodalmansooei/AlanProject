__author__ = 'Petrut Bogdan'
import nengo
import numpy as np
from arm import Arm
from head import Head
from action import ActionSelectionExecution

l = .5
h = .5

upper_length = .5
lower_length = .5

gamma = 0

shoulder_position = np.asarray([l, 0, -h])

lips_offset = np.asarray([0, .4, 0])

elbow_position = np.asarray([upper_length, 0, 0])

hand_position = np.asarray([0, lower_length, 0])


class Robot(nengo.Network):
    def __init__(self, n_neurons=100, label=None, seed=None, add_to_container=None):
        super(Robot, self).__init__(label, seed, add_to_container)
        # region Variable assignment
        self.n_neurons = n_neurons
        # endregion
        with self:
            # region Motors
            self.head_motor = nengo.Node(size_in=1)
            self.eye_x_motor = nengo.Node(size_in=1)
            self.eye_y_motor = nengo.Node(size_in=1)
            self.shoulder_motor = nengo.Node(size_in=1)
            self.elbow_motor = nengo.Node(size_in=1)
            self.finger_motor = nengo.Node(size_in=1)
            # endregion
            self.right_arm = Arm(shoulder_position, elbow_position,
                                 hand_position, gamma, seed=seed)
            self.head = Head(lips_offset)
            self.action = ActionSelectionExecution(2)

            # Lip position available in action selection and execution
            nengo.Connection(self.head.lips_position, self.action.lip_position)

            # Action enables arm and head
            nengo.Connection(self.action.arm_enable, self.right_arm.enable)
            nengo.Connection(self.action.head_enable, self.head.enable)

            # Targets propagated to concerned components
            nengo.Connection(self.action.arm_target_position,
                             self.right_arm.target_position.input)
            nengo.Connection(self.action.head_position,
                             self.head.target_position.input)

            # Arm finger enabling propagation
            nengo.Connection(self.action.finger_enable,
                             self.right_arm.action_enable)

            # Motor connection
            nengo.Connection(self.head.head_motor, self.head_motor)
            nengo.Connection(self.head.eye_motor[0], self.eye_x_motor)
            nengo.Connection(self.head.eye_motor[1], self.eye_y_motor)
            nengo.Connection(self.right_arm.shoulder_motor, self.shoulder_motor)
            nengo.Connection(self.right_arm.elbow_motor, self.elbow_motor)
            nengo.Connection(self.right_arm.finger_motor, self.finger_motor)


if __name__ == "__main__":
    mr_robot = Robot()
