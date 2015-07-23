__author__ = 'Petrut Bogdan'

import nengo
import numpy as np
import warnings
from robot_utils.matrix_multiplication import MatrixMultiplication


# TODO Consider error function using the difference of the slope of the
# target and current

def _alpha_error(x):
    target_alpha, current_alpha = x
    return np.sign(target_alpha - current_alpha) * \
           (target_alpha - current_alpha) ** 2


def _beta_error(x):
    # x = np.asarray(x)
    # target = x[0:3]
    # current = x[3:6]
    # return np.sign(target[1] - current[1]) * np.sum((target - current) ** 2)
    target_y, current_y = x
    return np.sign(current_y - target_y) * (target_y - current_y) ** 2


_rotation_mat = np.asarray(np.eye(3))
_position_vector = np.ones((3, 1))


class Arm(nengo.Network):
    def __init__(self, shoulder_position, elbow_position, hand_position, gamma,
                 n_neurons=100, length_radius=1.2,
                 angle_radius=1.5, tau=0.2, shoulder_sensitivity=1.3,
                 elbow_sensitivity=2.0, finger_sensitivity=2.0,
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
            self.enable = nengo.Ensemble(
                self.n_neurons, dimensions=1, radius=1)
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

            self.shoulder_Rz = nengo.networks.EnsembleArray(self.n_neurons,
                                                            _rotation_mat.size,
                                                            radius=self.angle_radius)

            nengo.Connection(self.gamma_angle, self.shoulder_Rz.input,
                             function=lambda x: [np.cos(x), -np.sin(x), 0,
                                                 np.sin(x), np.cos(x), 0,
                                                 0, 0, 1])

            self.shoulder_Ry = nengo.networks.EnsembleArray(self.n_neurons,
                                                            _rotation_mat.size,
                                                            radius=self.angle_radius)

            nengo.Connection(self.alpha_angle, self.shoulder_Ry.input,
                             function=lambda x: [np.cos(-x), 0, np.sin(-x),
                                                 0, 1, 0,
                                                 -np.sin(-x), 0, np.cos(-x)])

            self.elbow_rotation = MatrixMultiplication(
                n_neurons=self.n_neurons, matrix_A=_rotation_mat,
                matrix_B=_rotation_mat, radius=self.angle_radius,
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
                6 * self.n_neurons, 3,
                radius=self.length_radius)
            nengo.Connection(self._shoulder, self.translated_target_position)
            nengo.Connection(self.target_position.output,
                             self.translated_target_position,
                             transform=-np.eye(3))

            self.target_angle = nengo.Ensemble(2 * self.n_neurons, 1,
                                               radius=self.angle_radius)

            # TODO Modify to take into account the fact that the angle should
            # be in quadrants I or IV
            nengo.Connection(self.translated_target_position, self.target_angle,
                             function=lambda x: np.arctan2(x[2], x[0]))

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
            # Elbow error
            self.elbow_controller = nengo.Ensemble(2 * self.n_neurons, 2,
                                                   radius=self.angle_radius)
            nengo.Connection(self.target_position.output[1],
                             self.elbow_controller[0])
            nengo.Connection(self.hand_world_position[1],
                             self.elbow_controller[1])

            self.elbow_error = nengo.Ensemble(self.n_neurons, 1,
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
            self.finger_error = nengo.Ensemble(self.n_neurons, 1,
                                               radius=self.angle_radius)
            # Elbow error inhibits the finger

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
