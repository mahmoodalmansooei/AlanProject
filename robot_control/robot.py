__author__ = 'Petrut Bogdan'
import nengo
import numpy as np
from arm import Arm, HandType
from head import Head
from action import ActionSelectionExecution


class Robot(nengo.Network):
    def __init__(self, n_neurons=100, radius=1.7,
                 idle_position=np.asarray([[.3, .5, -.7]]),
                 gamma=0, shoulder_width=.3, neck_length=.2,
                 upper_arm_length=.5, lower_arm_length=.5, lip_distance=.2,
                 tau=0.2,
                 shoulder_sensitivity=2., elbow_sensitivity=2.,
                 finger_sensitivity=1.0,
                 label=None, seed=None, add_to_container=None):
        super(Robot, self).__init__(label, seed, add_to_container)
        # region Variable assignment
        self.finger_sensitivity = finger_sensitivity
        self.elbow_sensitivity = elbow_sensitivity
        self.shoulder_sensitivity = shoulder_sensitivity
        self.tau = tau
        self.shoulder_width = shoulder_width
        self.shoulder_position = np.asarray([shoulder_width, 0, -neck_length])
        self.idle_position = idle_position
        self.radius = radius
        self.n_neurons = n_neurons
        self.elbow_position = np.asarray([upper_arm_length, 0, 0])
        self.gamma = gamma
        self.hand_position = np.asarray([0, lower_arm_length, 0])
        self.lip_position = np.asarray([0, lip_distance, 0])
        # endregion
        with self:
            # region Motors
            self.head_motor = nengo.Node(size_in=1)
            self.eye_x_motor = nengo.Node(size_in=1)
            self.eye_y_motor = nengo.Node(size_in=1)
            self.right_shoulder_motor = nengo.Node(size_in=1)
            self.right_elbow_motor = nengo.Node(size_in=1)
            self.right_finger_motor = nengo.Node(size_in=1)
            self.left_shoulder_motor = nengo.Node(size_in=1)
            self.left_elbow_motor = nengo.Node(size_in=1)
            self.left_finger_motor = nengo.Node(size_in=1)
            # endregion
            self.right_arm = Arm(self.shoulder_position, self.elbow_position,
                                 self.hand_position, self.gamma,
                                 arm_type=HandType.RIGHT,
                                 n_neurons=self.n_neurons, seed=seed,
                                 label="Right arm controller")
            self.left_arm = Arm(self.shoulder_position, self.elbow_position,
                                self.hand_position, self.gamma,
                                arm_type=HandType.LEFT,
                                n_neurons=self.n_neurons, seed=seed,
                                label="Left arm controller")
            self.head = Head(self.lip_position, seed=seed,
                             label="Head controller")
            self.action = ActionSelectionExecution(
                seed=seed, label="Action selection and execution")

            # Lip position available in action selection and execution
            nengo.Connection(self.head.lips_position, self.action.lip_position)

            # Action enables arm and head
            nengo.Connection(self.action.right_arm_enable,
                             self.right_arm.enable)
            nengo.Connection(self.action.left_arm_enable, self.left_arm.enable)
            nengo.Connection(self.action.head_enable, self.head.enable)

            # Targets propagated to concerned components
            nengo.Connection(self.action.right_arm_target_position,
                             self.right_arm.target_position.input)
            nengo.Connection(self.action.left_arm_target_position,
                             self.left_arm.target_position.input,
                             transform=[[-1, 0, 0],
                                        [0, 1, 0],
                                        [0, 0, 1]])
            nengo.Connection(self.action.head_position,
                             self.head.target_position.input)

            # Arm finger enabling propagation
            nengo.Connection(self.action.right_finger_enable,
                             self.right_arm.action_enable)
            nengo.Connection(self.action.left_finger_enable,
                             self.left_arm.action_enable)

            # Motor connection
            nengo.Connection(self.head.head_motor, self.head_motor)
            nengo.Connection(self.head.eye_motor[0], self.eye_x_motor)
            nengo.Connection(self.head.eye_motor[1], self.eye_y_motor)

            nengo.Connection(self.right_arm.shoulder_motor,
                             self.right_shoulder_motor)
            nengo.Connection(self.right_arm.elbow_motor, self.right_elbow_motor)
            nengo.Connection(self.right_arm.finger_motor,
                             self.right_finger_motor)

            nengo.Connection(self.left_arm.shoulder_motor,
                             self.left_shoulder_motor)
            nengo.Connection(self.left_arm.elbow_motor, self.left_elbow_motor)
            nengo.Connection(self.left_arm.finger_motor,
                             self.left_finger_motor)

            # Control signals
            self.everything_done = nengo.Ensemble(self.n_neurons, 1)
            nengo.Connection(self.head.done, self.everything_done,
                             transform=[[.4]],
                             synapse=self.tau)
            nengo.Connection(self.right_arm.done, self.everything_done,
                             transform=[[.4]],
                             synapse=self.tau)
            nengo.Connection(self.left_arm.done, self.everything_done,
                             transform=[[.4]],
                             synapse=self.tau)
            self.done = nengo.Node(size_in=1)
            nengo.Connection(self.everything_done, self.done)


if __name__ == "__main__":
    mr_robot = Robot()
