__author__ = 'Petrut Bogdan'

import nengo
import numpy as np
from robot_utils.matrix_multiplication import MatrixMultiplication
import warnings


def h_error(x):
    """
    Squared-error function. Also gives the required direction of movement
    :param x: A vector consisting of the target orientation [1] and the current
    number of degrees [0]
    :type x: float[2]
    :return: The correction needed to match the target
    :rtype: float
    """
    return np.sign(x[1] - x[0]) * ((x[0] - x[1]) ** 2)


def e_error(x):
    """
    Squared-error function. Also gives the required direction of movement
    :param x: A vector consisting of the target position [0, 1], the current
    position [2, 3] and the current head position
    :type x: float[5]
    :return: The correction needed to match the target
    :rtype: float
    """
    adjusted_target = x[0] - x[4]
    return np.sign(adjusted_target - x[2]) * ((adjusted_target - x[2]) ** 2), \
        np.sign(x[1] - x[3]) * ((x[1] - x[3]) ** 2)


class Head(nengo.Network):
    def __init__(self, lips_position_offset, n_neurons=100, length_radius=1.2,
                 angle_radius=1.6, tau=0.3, head_sensitivity=1.3,
                 eye_x_sensitivity=2.0, eye_y_sensitivity=2.0, label=None,
                 seed=None,
                 add_to_container=None):
        """
        Class that represents the head movement of the robot. Given the position
        the robot is supposed to face, it will move it's eyes to look there
        while also rotating the whole head.

        The timescales involved here will have to be similar to what a human
        could achieve, i.e. similar head and eye movement speed

        Goals:
        *    move eyes so that they snap onto the target
        *    head rotates towards the target
        *    eyes still face the target even while the head rotates

        ========================================================================

        :param lips_position_offset: The position of the lips relative to the
        origin of the system (center of the head)
        :type lips_position_offset:numpy.ndarray
        :param n_neurons:The standard number of neurons used in each ensemble
        or ensemble array (some require a multiple of that)
        :type n_neurons:int
        :param length_radius:The radius of ensembles when computing lengths
        :type length_radius:float
        :param angle_radius:The radius of ensembles when computing angles
        :type angle_radius:float
        :param tau:Post-synaptic time constant (PSTC) to use for filtering.
        :type tau:float
        :param head_sensitivity:Reaction time constant for head rotation
        :type head_sensitivity:float
        :param eye_x_sensitivity:Reaction time constant for horizontal eye
        movement
        :type eye_x_sensitivity:float
        :param eye_y_sensitivity:Reaction time constant for vertical eye
        movement
        :type eye_y_sensitivity:float
        :param label:A descriptive label for the network
        :type label:string
        :param seed:Random number seed that will be fed to the random number
        generator. Setting this seed makes the creation of the model a
        deterministic process; however, each new ensemble in the network
        advances the random number generator, so if the network creation
        code changes, the entire model changes.
        :type seed:int
        :param add_to_container:Determines if this Network will be added to
        the current container. Defaults to true iff currently with a Network.
        :type add_to_container:bool
        """

        # TODO Connect external error to motor/sensor (they must decay
        # TODO realistically if not updated)

        # TODO Use self.done

        # TODO Add speech functionality
        super(Head, self).__init__(label, seed, add_to_container)
        # region Variable assignment
        self.n_neurons = n_neurons
        self.length_radius = length_radius
        self.angle_radius = angle_radius
        self.lips_position_offset = lips_position_offset
        self.tau = tau
        self.head_sensitivity = head_sensitivity
        self.eye_x_sensitivity = eye_x_sensitivity
        self.eye_y_sensitivity = eye_y_sensitivity
        # endregion
        # region Type checking and casting; bounds checking
        if type(lips_position_offset) != np.ndarray:
            self.lips_position_offset = np.asarray(lips_position_offset)

        assert self.lips_position_offset.size == 3, "Position vector should " \
                                                    "have 3 dimensions"

        if not all(-self.length_radius <= x <= self.length_radius for x in
                   self.lips_position_offset):
            warnings.warn(
                "Lip position vector seems to contain values that cannot be "
                "represented because of the currently selected length_radius")
        # endregion
        with self:
            # region input
            self.target_position = nengo.Ensemble(2 * self.n_neurons,
                                                  dimensions=2,
                                                  radius=self.length_radius)
            self.external_head_error = nengo.Ensemble(
                self.n_neurons, dimensions=1,
                radius=self.angle_radius)
            self.external_eye_error = nengo.Ensemble(
                self.n_neurons, dimensions=1,
                radius=self.angle_radius)
            # endregion
            # region output
            self.lips_position = nengo.Ensemble(
                3 * self.n_neurons, dimensions=3,
                radius=self.length_radius)
            self.head_motor = nengo.Ensemble(
                self.n_neurons, dimensions=1,
                radius=1)
            self.eye_motor = nengo.Ensemble(
                2 * self.n_neurons, dimensions=2,
                radius=self.angle_radius)
            self.done = nengo.Ensemble(
                self.n_neurons, dimensions=1,
                radius=self.angle_radius)
            # endregion
            # region control
            self.enable = nengo.Ensemble(
                self.n_neurons, dimensions=1,
                radius=self.angle_radius)
            # endregion
            # region lip offset
            _lips_position_offset = nengo.Node(
                self.lips_position_offset.ravel(), label="Lip offset")
            # endregion
            # region Head rotation
            # Error computation
            self.head_error = nengo.Ensemble(n_neurons=self.n_neurons,
                                             dimensions=1,
                                             radius=self.angle_radius,
                                             label="Head error")

            self.head_controller = nengo.Ensemble(n_neurons=2 * self.n_neurons,
                                                  dimensions=2,
                                                  radius=self.angle_radius)

            self.current_head = nengo.Ensemble(n_neurons=self.n_neurons,
                                               dimensions=1,
                                               radius=self.angle_radius)
            # Connections between the current --> controller
            # and target --> controller

            nengo.Connection(pre=self.current_head,
                             post=self.head_controller[0])
            nengo.Connection(pre=self.target_position[0],
                             post=self.head_controller[1], synapse=0.01)

            nengo.Connection(pre=self.head_controller, post=self.head_error,
                             function=h_error)

            # Connections that feedback into current
            nengo.Connection(pre=self.head_error, post=self.current_head,
                             transform=[[self.head_sensitivity * self.tau]],
                             synapse=self.tau)
            nengo.Connection(pre=self.current_head, post=self.current_head,
                             transform=[[1]], synapse=self.tau)
            # endregion
            # region Eye movement
            self.eye_error = nengo.Ensemble(n_neurons=self.n_neurons,
                                            dimensions=2,
                                            radius=self.angle_radius,
                                            label="Eye error")

            self.eye_controller = nengo.Ensemble(n_neurons=6 * self.n_neurons,
                                                 dimensions=5,
                                                 radius=self.angle_radius)

            self.current_eye = nengo.Ensemble(n_neurons=self.n_neurons,
                                              dimensions=2,
                                              radius=self.angle_radius)

            # Feed current head position in the eye controller to compute the
            # proper error
            nengo.Connection(self.current_head, self.eye_controller[4])

            # Connections for eye controller from target and current eye
            # positions
            nengo.Connection(self.target_position[0], self.eye_controller[0])
            nengo.Connection(self.target_position[1], self.eye_controller[1])

            nengo.Connection(self.current_eye[0], self.eye_controller[2])
            nengo.Connection(self.current_eye[1], self.eye_controller[3])

            nengo.Connection(self.eye_controller, self.eye_error,
                             function=e_error)

            # Feedback from eye error
            nengo.Connection(
                self.eye_error, self.current_eye,
                transform=[[self.eye_x_sensitivity * self.tau, 0],
                           [0, self.eye_y_sensitivity * self.tau]],
                synapse=self.tau)

            # Current eye position integrator
            nengo.Connection(self.current_eye, self.current_eye,
                             synapse=self.tau)
            # endregion
            # region Compute the final position of the lips
            self.rotation_transformation = MatrixMultiplication(
                n_neurons=self.n_neurons, radius=self.length_radius,
                label="Rotation transform")

            _combo = nengo.Ensemble(n_neurons=self.n_neurons, dimensions=1,
                                    label="Relay", radius=self.angle_radius)

            nengo.Connection(self.target_position[0], _combo)

            nengo.Connection(_combo,
                             self.rotation_transformation.in_A[0],
                             function=lambda x: np.cos(x))

            nengo.Connection(_combo,
                             self.rotation_transformation.in_A[4],
                             function=lambda x: np.cos(x))

            nengo.Connection(_combo,
                             self.rotation_transformation.in_A[1],
                             function=lambda x: np.sin(x))

            nengo.Connection(_combo,
                             self.rotation_transformation.in_A[3],
                             function=lambda x: -np.sin(x))

            nengo.Connection(_combo,
                             self.rotation_transformation.in_A[8],
                             function=lambda x: 1)

            nengo.Connection(_lips_position_offset,
                             self.rotation_transformation.in_B)

            # This vector will be used when trying to shush the crowd
            nengo.Connection(self.rotation_transformation.output,
                             self.lips_position)
            # endregion
            # region Motor control

            # Head motor
            self.head_motor_control = nengo.Ensemble(
                n_neurons=self.n_neurons, dimensions=1, radius=1)
            nengo.Connection(self.head_error, self.head_motor_control,
                             transform=[[1. / self.angle_radius]],
                             synapse=self.tau)
            nengo.Connection(self.head_motor_control, self.head_motor)

            # Eye motors
            self.eye_motor_control = nengo.Ensemble(
                n_neurons=2 * self.n_neurons, dimensions=2, radius=1)

            nengo.Connection(
                self.eye_error, self.eye_motor_control,
                transform=[[1. / self.angle_radius, 0],
                           [0, 1. / self.angle_radius]],
                synapse=self.tau)

            nengo.Connection(self.eye_motor_control, self.eye_motor)

            # endregion
            # region Inhibitory gating which enables or disables the module
            nengo.Connection(
                self.enable, self.head_motor_control.neurons,
                transform=[[-2.5]] * self.head_motor_control.n_neurons)
            nengo.Connection(
                self.enable, self.eye_motor_control.neurons,
                transform=[[-2.5]] * self.eye_motor_control.n_neurons)
            nengo.Connection(
                self.enable, self.eye_controller.neurons,
                transform=[[-2.5]] * self.eye_controller.n_neurons)
            nengo.Connection(
                self.enable, self.head_controller.neurons,
                transform=[[-2.5]] * self.head_controller.n_neurons)
            # endregion
