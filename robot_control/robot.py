from robot_utils.dot_product import DotProduct

__author__ = 'Petrut Bogdan'

import nengo
import numpy as np
from robot_interface.container import Container
from robot_models.servo import Servo
from robot_models.control_signal import ControlSignal

LEFT = np.array([0.7, 0.7])
RIGHT = np.array([0.7, -0.7])


class Robot(nengo.Network):
    def __init__(self, motor_gain=2.0, label=None, seed=None,
                 add_to_container=None):
        """

        :param label: Name of the model. Defaults to None.
        :type label: str
        :param seed: Random number seed that will be fed to the random
            number generator. Setting this seed makes the creation of the
            model a deterministic process; however, each new ensemble
            in the network advances the random number generator, so if
            the network creation code changes, the entire model changes.
        :type seed: int
        :param add_to_container: Determines if this Network will be added to
            the current container. Defaults to true iff currently with a Network
        :type add_to_container: bool
        """
        super(Robot, self).__init__(label, seed, add_to_container)
        n_neurons = 100
        tau = 0.1
        self.motor_gain = motor_gain

        def error(vector):
            return np.sign(vector[0] - vector[1]) * ((vector[0] - vector[1]) ** 2)

        self.servos = Container()
        self.controls = Container()

        with self:
            # Inputs
            self.action = ControlSignal(container=self.controls, size_out=2, label='action')
            self.direction = ControlSignal(container=self.controls, size_out=2, label='direction')
            self.sound = nengo.Node(lambda t: np.sin(t))
            self.silence = ControlSignal(container=self.controls, size_out=3, label='silence')

            # Initialisation
            self.controls.update(self.action, np.asarray([1., 0.]))
            self.controls.update(self.direction, np.asarray([.7, .7]))
            self.controls.update(self.silence, np.asarray([.3, .7, 1]))

            # Hidden layer
            self.left_current_position = nengo.networks.EnsembleArray(n_neurons, 3)
            self.right_current_position = nengo.networks.EnsembleArray(n_neurons, 3)

            self.left_target_position = nengo.networks.EnsembleArray(n_neurons, 3)
            self.right_target_position = nengo.networks.EnsembleArray(n_neurons, 3)

            self.left_error = nengo.networks.EnsembleArray(5 * n_neurons, n_ensembles=3, ens_dimensions=2, radius=1.3)
            self.right_error = nengo.networks.EnsembleArray(5 * n_neurons, n_ensembles=3, ens_dimensions=2, radius=1.3)

            nengo.Connection(self.left_target_position.output, self.left_error.input[[0, 2, 4]])
            nengo.Connection(self.left_current_position.output, self.left_error.input[[1, 3, 5]])

            nengo.Connection(self.right_target_position.output, self.right_error.input[[0, 2, 4]])
            nengo.Connection(self.right_current_position.output, self.right_error.input[[1, 3, 5]])

            nengo.Connection(self.silence, self.left_target_position.input)
            nengo.Connection(self.silence, self.right_target_position.input)

            # Feedback
            left_error = self.left_error.add_output("error", error)
            right_error = self.right_error.add_output("error", error)

            nengo.Connection(left_error, self.left_current_position.input, synapse=tau)
            nengo.Connection(right_error, self.right_current_position.input, synapse=tau)

            nengo.Connection(self.left_current_position.output, self.left_current_position.input, synapse=tau)
            nengo.Connection(self.right_current_position.output, self.right_current_position.input, synapse=tau)

            # Output
            self.left_motors = nengo.Node(size_in=3)
            self.right_motors = nengo.Node(size_in=3)

            nengo.Connection(left_error, self.left_motors, synapse=tau, transform=np.eye(3) * self.motor_gain)
            nengo.Connection(right_error, self.right_motors, synapse=tau, transform=np.eye(3) * self.motor_gain)

            self.left_servos = Servo(container=self.servos, size_in=3, label="left_servos")
            self.right_servos = Servo(container=self.servos, size_in=3, label="right_servos")

            nengo.Connection(self.left_current_position.output, self.left_servos, synapse=.5)
            nengo.Connection(self.right_current_position.output, self.right_servos, synapse=.5)

            # Action selection
            # The 2 actions are: silence and gesture
            # Gesture inhibits a target function (goes idle)
            # Silence inhibits sound and give a target position of its own
            self.bg = nengo.networks.BasalGanglia(2)
            nengo.Connection(self.action, self.bg.input)

            # Sound connections
            self.rhythm = nengo.Ensemble(n_neurons, 1)
            nengo.Connection(self.sound, self.rhythm)

            nengo.Connection(self.rhythm, self.left_error.input[[0]], transform=[[-.5]]) # TODO apply sub-unit transfrom
            nengo.Connection(self.rhythm, self.right_error.input[[0]], transform=[[.5]])

            # If silencing, inhibit rhythm
            nengo.Connection(self.bg.output[0], self.rhythm.neurons, transform=[[1]] * self.rhythm.n_neurons)

            # When silencing, provide a target function (in degrees) for each of the the joints
            # Done. Provided from the "outside"

            # When gesturing, inhibit the target function (will return to idling position)
            for ensemble in self.left_target_position.all_ensembles:
                nengo.Connection(self.bg.output[1], ensemble.neurons, transform=[[1]] * ensemble.n_neurons)

            for ensemble in self.right_target_position.all_ensembles:
                nengo.Connection(self.bg.output[1], ensemble.neurons, transform=[[1]] * ensemble.n_neurons)

            # Select an arm for silencing / gesturing

            self.left_dp = DotProduct()
            self.right_dp = DotProduct()

            self.left = nengo.Node(output=LEFT)
            self.right = nengo.Node(output=RIGHT)

            nengo.Connection(self.direction, self.left_dp.in_A)
            nengo.Connection(self.left, self.left_dp.in_B)

            nengo.Connection(self.direction, self.right_dp.in_A)
            nengo.Connection(self.right, self.right_dp.in_B)

            L = nengo.Ensemble(100, 1)
            R = nengo.Ensemble(100, 1)
            nengo.Connection(self.left_dp.output, L)
            nengo.Connection(self.right_dp.output, R)

            self.arm_selector = nengo.networks.BasalGanglia(2)

            nengo.Connection(L, self.arm_selector.input[0], function=lambda x: np.abs(x))
            nengo.Connection(R, self.arm_selector.input[1], function=lambda x: np.abs(x))

            # Basal ganglia will now inhibit the opposing arm
            for ensemble in self.left_target_position.all_ensembles:
                nengo.Connection(self.arm_selector.output[1], ensemble.neurons, transform=[[1]] * ensemble.n_neurons)

            for ensemble in self.right_target_position.all_ensembles:
                nengo.Connection(self.arm_selector.output[0], ensemble.neurons, transform=[[1]] * ensemble.n_neurons)

if __name__ == "__main__":
    r = Robot()
