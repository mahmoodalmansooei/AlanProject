from robot_utils.matrix_multiplication import MatrixMultiplication

__author__ = 'Petrut Bogdan'

import nengo
import numpy as np
import warnings


# TODO Consider error function using the difference of the slope of the
# target and current

def _error(x):
    target_x, target_y, current_x, current_y = x
    return (target_x - current_x) ** 2, (target_y - current_y) ** 2


_rotation_mat = np.asarray(np.eye(3))
_position_vector = np.ones((3, 1))


class Arm(nengo.Network):
    def __init__(self, shoulder_position, elbow_position, hand_position, gamma,
                 n_neurons=100, length_radius=1.2,
                 angle_radius=1.6, tau=0.3, shoulder_sensitivity=1.3,
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
            self.target_position = nengo.Node(size_in=3)
            self.external_shoulder_error = nengo.Node(size_in=1)
            self.external_elbow_error = nengo.Node(size_in=1)
            self.external_finger_error = nengo.Node(size_in=1)
            # endregion
            # region output
            self.shoulder_motor = nengo.Node(size_in=1)
            self.elbow_motor = nengo.Node(size_in=1)
            self.finger_motor = nengo.Node(size_in=1)
            self.done = nengo.Node(size_in=1)
            # endregion
            # region control
            self.enable = nengo.Node(size_in=1)
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


            # region Compute the max distance elbow position

            # endregion
            # region Upper hand movement

            # endregion
            # region Lower hand movement

            # endregion
            # region Finger movement

            # endregion


if __name__ == "__main__":
    arm = Arm(np.zeros((3, 1)), np.zeros((3, 1)), np.zeros((3, 1)), 0)
