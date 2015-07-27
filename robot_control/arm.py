__author__ = 'Petrut Bogdan'

import nengo
import numpy as np
import warnings
from robot_utils.matrix_multiplication import MatrixMultiplication
import math


# TODO Consider error function using the difference of the slope of the
# target and current

def _alpha_error(x):
    target_alpha, current_alpha = x
    return np.sign(target_alpha - current_alpha) * \
           (target_alpha - current_alpha) ** 2


def _beta_error(x):
    target_beta, current_beta = x
    return np.sign(target_beta - current_beta) * \
           (target_beta - current_beta) ** 2


def _finger_error(x):
    target_angle, current_angle = x
    return np.sign(target_angle - current_angle) * \
           (target_angle - current_angle) ** 2


_rotation_mat = np.asarray(np.eye(3))
_position_vector = np.ones((3, 1))


class Arm(nengo.Network):
    def __init__(self, shoulder_position, elbow_position, hand_position, gamma,
                 n_neurons=100, length_radius=1.7,
                 angle_radius=1.57, tau=0.2, shoulder_sensitivity=1.3,
                 elbow_sensitivity=1.0, finger_sensitivity=2.0,
                 label=None, seed=None,
                 add_to_container=None):
        """
        Class that represents a robotic arm with 3 degrees of freedom moving in
        world space. The goal of the arm is to move the end effector in the
        desired position and then execute an action. This should only happen if
        the arm is not inhibited by a controller ensemble or action selector.

        The current implementation is compliant with the requirements of the
        Alan Project (art project for the Manchester Art Gallery).

        The arm will receive information from the outside world regarding:
        *   target position vector in world space
        *   control signal -- allowed to move the arm or not

        The arm will be initialised with these values:
        *   distances between joints (length of links):
            +   elbow in relation to the shoulder
            +   hand in relation to the elbow
        *   shoulder position
        *   shoulder constant offset

        Assumptions:
        *   links between joints are straight and rigid
        *   links do not change length
        *   base position (shoulder) does not change
        *   target position can change

        ========================================================================
        :param shoulder_position:
        :type shoulder_position:
        :param elbow_position:
        :type elbow_position:
        :param hand_position:
        :type hand_position:
        :param gamma:
        :type gamma:
        :param n_neurons:
        :type n_neurons:
        :param length_radius:
        :type length_radius:
        :param angle_radius:
        :type angle_radius:
        :param tau:
        :type tau:
        :param shoulder_sensitivity:
        :type shoulder_sensitivity:
        :param elbow_sensitivity:
        :type elbow_sensitivity:
        :param finger_sensitivity:
        :type finger_sensitivity:
        :param label:
        :type label:
        :param seed:
        :type seed:
        :param add_to_container:
        :type add_to_container:
        :return:
        :rtype:
        """
        # TODO Connect external error to motor/sensor (they must decay
        # TODO realistically if not updated)

        # TODO What position should the arm be in by default (idle position)

        # TODO Need to have an option for left / right hand

        # TODO Use self.done

        # TODO Use enums for referencing outputs (e.g. output[Enum.X] instead of
        # output[1]
        super(Arm, self).__init__(label, seed, add_to_container)
        # region Variable assignment
        self.n_neurons = n_neurons
        self.length_radius = length_radius
        self.angle_radius = angle_radius
        self.tau = tau
        self.shoulder_sensitivity = shoulder_sensitivity
        self.elbow_sensitivity = elbow_sensitivity
        self.finger_sensitivity = finger_sensitivity

        self.shoulder_position = shoulder_position
        self.elbow_position = elbow_position
        self.hand_position = hand_position
        self.gamma = gamma
        # endregion
        # region Type checking and casting; bounds checking
        if type(shoulder_position) != np.ndarray:
            self.shoulder_position = np.asarray(shoulder_position)

        assert self.shoulder_position.size == 3, "Position vector should " \
                                                 "have 3 dimensions"
        if not all(-self.length_radius <= x <= self.length_radius for x in
                   self.shoulder_position):
            warnings.warn(
                "Shoulder position vector seems to "
                "contain values that cannot be "
                "represented because of the currently selected length_radius")
        if type(elbow_position) != np.ndarray:
            self.elbow_position = np.asarray(elbow_position)
        assert self.elbow_position.size == 3, "Position vector should " \
                                              "have 3 dimensions"
        if not all(-self.length_radius <= x <= self.length_radius for x in
                   self.elbow_position):
            warnings.warn(
                "Elbow position vector seems to "
                "contain values that cannot be "
                "represented because of the currently selected length_radius")

        if type(hand_position) != np.ndarray:
            self.hand_position = np.asarray(hand_position)
        assert self.hand_position.size == 3, "Position vector should " \
                                             "have 3 dimensions"
        if not all(-self.length_radius <= x <= self.length_radius for x in
                   self.hand_position):
            warnings.warn(
                "Hand position vector seems to "
                "contain values that cannot be "
                "represented because of the currently selected length_radius")
        # endregion
        with self:
            # region input
            # self.target_position = nengo.Ensemble(3 * self.n_neurons,
            #                                       dimensions=3,
            #                                       radius=self.length_radius)

            self.target_position = nengo.networks.EnsembleArray(
                self.n_neurons, n_ensembles=3)

            self.external_shoulder_error = nengo.Ensemble(
                self.n_neurons, dimensions=1,
                radius=self.angle_radius)
            self.external_elbow_error = nengo.Ensemble(
                self.n_neurons, dimensions=1,
                radius=self.angle_radius)
            self.external_finger_error = nengo.Ensemble(
                self.n_neurons, dimensions=1,
                radius=self.angle_radius)
            # endregion
            # region output
            self.shoulder_motor = nengo.Ensemble(
                self.n_neurons, dimensions=1,
                radius=1)
            self.elbow_motor = nengo.Ensemble(
                self.n_neurons, dimensions=1,
                radius=1)
            self.finger_motor = nengo.Ensemble(
                self.n_neurons, dimensions=1,
                radius=1)
            self.done = nengo.Ensemble(
                self.n_neurons, dimensions=1,
                radius=1)
            # endregion
            # region control
            self.enable = nengo.Ensemble(self.n_neurons, dimensions=1, radius=1)
            self.action_enable = nengo.Ensemble(self.n_neurons, dimensions=1,
                                                radius=1)
            # endregion
            # region constants
            self._shoulder = nengo.Node(output=self.shoulder_position.ravel(),
                                        label="Shoulder position")
            self._elbow = nengo.Node(output=self.elbow_position.ravel(),
                                     label="Elbow position")
            self._hand = nengo.Node(output=self.hand_position.ravel(),
                                    label="Hand position")
            self.gamma_angle = nengo.Node(output=self.gamma,
                                          label="Constant shoulder incline")
            # endregion
            # region Compute the elbow position
            self.alpha_angle = nengo.Ensemble(n_neurons=self.n_neurons,
                                              dimensions=1,
                                              radius=self.angle_radius,
                                              label="Shoulder alpha angle")

            self.shoulder_Rz = nengo.networks.EnsembleArray(
                self.n_neurons,
                _rotation_mat.size,
                radius=self.angle_radius)

            nengo.Connection(self.gamma_angle, self.shoulder_Rz.input,
                             function=lambda x: [np.cos(x), -np.sin(x), 0,
                                                 np.sin(x), np.cos(x), 0,
                                                 0, 0, 1])

            self.shoulder_Ry = nengo.networks.EnsembleArray(
                self.n_neurons,
                _rotation_mat.size,
                radius=self.angle_radius)

            nengo.Connection(self.alpha_angle, self.shoulder_Ry.input,
                             function=lambda x: [np.cos(-x), 0, np.sin(-x),
                                                 0, 1, 0,
                                                 -np.sin(-x), 0, np.cos(-x)])

            self.elbow_rotation = MatrixMultiplication(
                n_neurons=self.n_neurons, matrix_A=_rotation_mat,
                matrix_B=_rotation_mat, radius=1,
                seed=self.seed)

            nengo.Connection(self.shoulder_Rz.output, self.elbow_rotation.in_B)
            nengo.Connection(self.shoulder_Ry.output, self.elbow_rotation.in_A)

            self.elbow_position_computer = MatrixMultiplication(
                n_neurons=self.n_neurons, radius=self.length_radius,
                seed=self.seed)

            nengo.Connection(self.elbow_rotation.output,
                             self.elbow_position_computer.in_A)
            nengo.Connection(self._elbow,
                             self.elbow_position_computer.in_B)

            self.elbow_world_position = nengo.Ensemble(
                n_neurons=3 * self.n_neurons, dimensions=3,
                radius=self.length_radius)

            nengo.Connection(self.elbow_position_computer.output,
                             self.elbow_world_position, synapse=self.tau)
            nengo.Connection(self._shoulder,
                             self.elbow_world_position, synapse=self.tau)

            # endregion
            # region Compute the hand position
            self.beta_angle = nengo.Ensemble(n_neurons=self.n_neurons,
                                             dimensions=1,
                                             radius=self.angle_radius)
            self.elbow_Rz = nengo.networks.EnsembleArray(self.n_neurons,
                                                         _rotation_mat.size,
                                                         radius=self.angle_radius)

            nengo.Connection(self.beta_angle, self.elbow_Rz.input,
                             function=lambda x: [np.cos(x), -np.sin(x), 0,
                                                 np.sin(x), np.cos(x), 0,
                                                 0, 0, 1])

            self.hand_rotation = MatrixMultiplication(
                n_neurons=self.n_neurons, matrix_A=_rotation_mat,
                matrix_B=_rotation_mat, radius=self.angle_radius,
                seed=self.seed)

            nengo.Connection(self.elbow_rotation.output,
                             self.hand_rotation.in_A)
            nengo.Connection(self.elbow_Rz.output, self.hand_rotation.in_B)

            self.hand_position_computer = MatrixMultiplication(
                n_neurons=self.n_neurons, radius=self.length_radius,
                seed=self.seed)

            nengo.Connection(self.hand_rotation.output,
                             self.hand_position_computer.in_A)
            nengo.Connection(self._hand, self.hand_position_computer.in_B)

            self.hand_world_position = nengo.Ensemble(
                n_neurons=3 * self.n_neurons, dimensions=3,
                radius=self.length_radius)

            nengo.Connection(self.hand_position_computer.output,
                             self.hand_world_position, synapse=self.tau)
            nengo.Connection(self.elbow_world_position,
                             self.hand_world_position, synapse=self.tau)
            # endregion
            # region Error between target and current alpha angles
            self.translated_target_position = nengo.Ensemble(
                6 * self.n_neurons, 2,
                radius=self.length_radius)
            nengo.Connection(self._shoulder, self.translated_target_position,
                             transform=[[1, 0, 0], [0, 0, 1]])
            nengo.Connection(self.target_position.output,
                             self.translated_target_position,
                             transform=[[-1, 0, 0], [0, 0, -1]])

            self.target_angle = nengo.Ensemble(2 * self.n_neurons, 1,
                                               radius=self.angle_radius)

            self.quadrant_identifier = nengo.Network(
                label="Quadrant identifier", seed=self.seed)
            with self.quadrant_identifier:
                self.target_rotation = MatrixMultiplication(
                    self.n_neurons, matrix_A=np.eye(2),
                    matrix_B=np.zeros((2, 1)),
                    radius=self.length_radius,
                    seed=self.seed)

                self._right_angle_rotation = nengo.Node(
                    np.array([[0, 1], [-1, 0]]).ravel())

                nengo.Connection(self._right_angle_rotation,
                                 self.target_rotation.in_A)
                nengo.Connection(self.translated_target_position,
                                 self.target_rotation.in_B)

                self.faux_target_position = nengo.Ensemble(4 * self.n_neurons,
                                                           2)

                nengo.Connection(self.target_rotation.output,
                                 self.faux_target_position)

                self.quadrant_selector = nengo.Ensemble(3 * self.n_neurons, 1)

                nengo.Connection(self.faux_target_position,
                                 self.quadrant_selector,
                                 function=lambda x: np.sign(
                                     np.arctan2(x[1], x[0])))

                self.quadrant_based_action_selector = \
                    nengo.networks.BasalGanglia(2, self.n_neurons)

                nengo.Connection(self.quadrant_selector,
                                 self.quadrant_based_action_selector.input[0])
                nengo.Connection(self.quadrant_selector,
                                 self.quadrant_based_action_selector.input[1],
                                 transform=[[-1]])

                self._const_pi = nengo.Node(output=np.pi)
                self.offset = nengo.Ensemble(self.n_neurons, 1,
                                             radius=2 * self.angle_radius)

                nengo.Connection(self.quadrant_based_action_selector.output[0],
                                 self.offset.neurons,
                                 transform=[[1]] * self.offset.n_neurons)

                nengo.Connection(self._const_pi, self.offset)

            self.potential_target_angle = nengo.Ensemble(
                4 * n_neurons, 1,
                radius=2 * self.angle_radius)

            self.directional_offset = nengo.Ensemble(
                6 * self.n_neurons, 2,
                radius=2 * self.angle_radius)
            nengo.Connection(self.offset, self.directional_offset[0])

            nengo.Connection(self.translated_target_position,
                             self.directional_offset[1],
                             function=lambda x: np.arctan2(x[1], x[0]))

            nengo.Connection(self.translated_target_position,
                             self.potential_target_angle,
                             function=lambda x: np.arctan2(x[1], x[0]))

            nengo.Connection(self.directional_offset,
                             self.potential_target_angle,
                             function=lambda x: -np.sign(x[1]) * x[0])

            nengo.Connection(self.potential_target_angle, self.target_angle)

            self.shoulder_controller = nengo.Ensemble(2 * self.n_neurons, 2,
                                                      radius=self.angle_radius)

            nengo.Connection(self.target_angle, self.shoulder_controller[0])
            nengo.Connection(self.alpha_angle, self.shoulder_controller[1])

            self.shoulder_error = nengo.Ensemble(self.n_neurons, 1,
                                                 radius=self.angle_radius)

            nengo.Connection(self.shoulder_controller, self.shoulder_error,
                             function=_alpha_error)

            # Feedback error

            nengo.Connection(self.shoulder_error, self.alpha_angle,
                             synapse=self.tau,
                             transform=[[self.shoulder_sensitivity * self.tau]])
            nengo.Connection(self.alpha_angle, self.alpha_angle,
                             synapse=self.tau)
            # endregion
            # region Error between target and current beta angles
            """
            Beta angle error will be computed in the following way:

            - compute the position of the new_target = target - shoulder
            - rotate the new_target by -alpha around Y, then by -gamma around Z
            - compute the np.arctan2 of the final_target
            - error computation will take into account that beta is should be
            considered as beta + pi/2 because beta=0 should be the angle at
            which the lower arm is perpendicular on the upper arm
            """

            self.new_target = nengo.networks.EnsembleArray(
                self.n_neurons, 3,
                radius=self.length_radius)

            nengo.Connection(self.target_position.output, self.new_target.input)
            nengo.Connection(self._shoulder, self.new_target.input,
                             transform=-np.eye(3))

            self.inv_shoulder_Rz = nengo.networks.EnsembleArray(
                self.n_neurons,
                _rotation_mat.size,
                radius=self.angle_radius)

            nengo.Connection(self.gamma_angle, self.inv_shoulder_Rz.input,
                             function=lambda x: [np.cos(-x), -np.sin(-x), 0,
                                                 np.sin(-x), np.cos(-x), 0,
                                                 0, 0, 1])

            self.inv_shoulder_Ry = nengo.networks.EnsembleArray(
                self.n_neurons,
                _rotation_mat.size,
                radius=self.angle_radius)

            nengo.Connection(self.alpha_angle, self.inv_shoulder_Ry.input,
                             function=lambda x: [np.cos(x), 0, np.sin(x),
                                                 0, 1, 0,
                                                 -np.sin(x), 0, np.cos(x)])

            self.inv_rotations = MatrixMultiplication(self.n_neurons,
                                                      matrix_A=_rotation_mat,
                                                      matrix_B=_rotation_mat,
                                                      radius=1)

            nengo.Connection(self.inv_shoulder_Rz.output,
                             self.inv_rotations.in_A)
            nengo.Connection(self.inv_shoulder_Ry.output,
                             self.inv_rotations.in_B)

            self.final_target = MatrixMultiplication(self.n_neurons,
                                                     radius=self.angle_radius)

            nengo.Connection(self.inv_rotations.output, self.final_target.in_A)
            nengo.Connection(self.new_target.output, self.final_target.in_B)

            # Elbow error

            self.final_target_XY = nengo.Ensemble(8 * self.n_neurons,
                                                  dimensions=2,
                                                  radius=2 * self.length_radius)

            nengo.Connection(self.final_target.output[0:2],
                             self.final_target_XY)
            nengo.Connection(self._elbow[0:2], self.final_target_XY,
                             transform=[[-1, 0], [0, -1]])

            self.elbow_controller = nengo.Ensemble(8 * self.n_neurons,
                                                   dimensions=2,
                                                   radius=self.angle_radius)

            nengo.Connection(self.final_target_XY, self.elbow_controller[0],
                             function=lambda x: [
                                 np.abs(np.arctan2(x[1], x[0])) - np.pi / 2])
            nengo.Connection(self.beta_angle, self.elbow_controller[1])

            self.elbow_error = nengo.Ensemble(6 * self.n_neurons, 1,
                                              radius=self.angle_radius)
            nengo.Connection(self.elbow_controller, self.elbow_error,
                             function=_beta_error)

            # Feedback error

            nengo.Connection(self.elbow_error, self.beta_angle,
                             synapse=self.tau,
                             transform=[[self.elbow_sensitivity * self.tau]])
            nengo.Connection(self.beta_angle, self.beta_angle,
                             synapse=self.tau)

            # Shoulder error inhibits the elbow

            # endregion
            # region Error between target and current finger angles
            # Finger error
            self.finger = nengo.Ensemble(n_neurons=self.n_neurons, dimensions=1,
                                         radius=self.angle_radius)
            # The 'up' or extended position of the finger
            self.finger_up = nengo.Node(output=np.pi / 2)
            # The finger's target position
            self.finger_target = nengo.Ensemble(n_neurons=self.n_neurons,
                                                dimensions=1,
                                                radius=self.angle_radius)
            nengo.Connection(self.finger_up, self.finger_target)
            # The ensemble that combines the target position for the finger
            # and its current position
            self.finger_controller = nengo.Ensemble(
                n_neurons=2 * self.n_neurons, dimensions=2,
                radius=self.angle_radius)
            self.finger_error = nengo.Ensemble(self.n_neurons, 1,
                                               radius=self.angle_radius)

            nengo.Connection(self.finger_target, self.finger_controller[0])
            nengo.Connection(self.finger, self.finger_controller[1])

            nengo.Connection(self.finger_controller, self.finger_error,
                             function=_finger_error)

            # Feedback error

            nengo.Connection(self.finger_error, self.finger,
                             synapse=self.tau,
                             transform=[[self.finger_sensitivity * self.tau]])
            nengo.Connection(self.finger, self.finger,
                             synapse=self.tau)

            # Elbow error inhibits the finger
            nengo.Connection(self.elbow_error, self.finger_target.neurons,
                             transform=[[-3]] * self.finger_target.n_neurons)
            # endregion
            # region Upper arm movement
            self.shoulder_motor_control = nengo.Ensemble(
                n_neurons=self.n_neurons, dimensions=1, radius=1)
            nengo.Connection(self.shoulder_error, self.shoulder_motor_control,
                             transform=[[self.shoulder_sensitivity]],
                             synapse=0.1)
            nengo.Connection(self.shoulder_motor_control, self.shoulder_motor)
            # endregion
            # region Lower arm movement
            self.elbow_motor_control = nengo.Ensemble(
                n_neurons=self.n_neurons, dimensions=1, radius=1)
            nengo.Connection(self.elbow_error, self.elbow_motor_control,
                             transform=[[self.elbow_sensitivity]],
                             synapse=0.1)
            nengo.Connection(self.elbow_motor_control, self.elbow_motor)
            # endregion
            # region Finger movement
            self.finger_motor_control = nengo.Ensemble(
                n_neurons=self.n_neurons, dimensions=1, radius=1)
            nengo.Connection(self.finger_error, self.finger_motor_control,
                             transform=[[self.finger_sensitivity]],
                             synapse=0.1)
            nengo.Connection(self.finger_motor_control, self.finger_motor)

            nengo.Connection(self.action_enable, self.finger_target.neurons,
                             transform=[[-3]] * self.finger_target.n_neurons)
            nengo.Connection(
                self.action_enable,
                self.finger_motor_control.neurons,
                transform=[[-3]] * self.finger_motor_control.n_neurons)
            # endregion
            # region Inhibitory gating which enables or disables the module
            nengo.Connection(
                self.enable, self.shoulder_motor_control.neurons,
                transform=[[-2.5]] * self.shoulder_motor_control.n_neurons)
            nengo.Connection(
                self.enable, self.elbow_motor_control.neurons,
                transform=[[-2.5]] * self.elbow_motor_control.n_neurons)
            nengo.Connection(
                self.enable, self.finger_motor_control.neurons,
                transform=[[-2.5]] * self.finger_motor_control.n_neurons)

            nengo.Connection(
                self.enable, self.shoulder_controller.neurons,
                transform=[[-2.5]] * self.shoulder_controller.n_neurons)

            nengo.Connection(
                self.enable, self.elbow_controller.neurons,
                transform=[[-2.5]] * self.elbow_controller.n_neurons)
            # endregion


if __name__ == "__main__":
    arm = Arm(np.zeros((3, 1)), np.zeros((3, 1)), np.zeros((3, 1)), 0)
