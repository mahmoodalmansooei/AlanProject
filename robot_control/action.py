__author__ = 'Petrut Bogdan'

import nengo
import numpy as np
from robot_utils.matrix_multiplication import MatrixMultiplication

_scalar = np.asarray(np.zeros((1, 1)))
_vector = np.asarray(np.zeros((1, 3)))


class ActionSelectionExecution(nengo.Network):
    def __init__(self, n_neurons=100, tau=0.01, radius=1.7,
                 label=None, seed=None, add_to_container=None):
        """
        Actions:

        *   move head [0]
        *   move left arm  [1]
        *   move right arm  [2]

        Params:

        *   finger on/off
        *   target = lips / general

        :param n_neurons: The number of neurons.
        :type n_neurons: int
        :param radius: The range of values that can be represented
        :type radius: float
        :param tau: post synaptic time constant
        :type tau: float
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
        super(ActionSelectionExecution, self).__init__(label, seed,
                                                       add_to_container)

        # region Variable assignment
        self.dimensions = 2
        self.n_neurons = n_neurons
        self.tau = tau
        self.radius = radius
        # endregion
        with self:
            # region inputs
            # ------------------------------------------------------------------
            # Exterior decided hand target position
            self.right_arm_target_position = nengo.Ensemble(6 * self.n_neurons, 3,
                                                      radius=self.radius)
            self.left_arm_target_position = nengo.Ensemble(6 * self.n_neurons, 3,
                                                     radius=self.radius)

            # Input actions from outside
            self.actions = nengo.networks.EnsembleArray(self.n_neurons,
                                                        self.dimensions)
            # endregion
            # region controls
            # ------------------------------------------------------------------
            # Control for the finger
            self.right_finger_enable = nengo.Ensemble(self.n_neurons,
                                                      dimensions=1)
            self.left_finger_enable = nengo.Ensemble(self.n_neurons,
                                                     dimensions=1)

            # Killswitch
            self.killswitch = nengo.Ensemble(self.n_neurons, 1)

            # ------------------------------------------------------------------
            # endregion
            # region outputs
            # ------------------------------------------------------------------
            self.right_arm_enable = nengo.Ensemble(self.n_neurons, 1)
            self.left_arm_enable = nengo.Ensemble(self.n_neurons, 1)
            # ------------------------------------------------------------------
            # endregion
            # region Action selection and enabling output
            # ------------------------------------------------------------------
            # Basal Ganglia
            self.action_selection = nengo.networks.BasalGanglia(
                self.dimensions, n_neurons_per_ensemble=self.n_neurons,
                net=nengo.Network("Action selection"))

            # Thalamus
            self.action_execution = nengo.networks.Thalamus(
                self.dimensions,
                n_neurons_per_ensemble=self.dimensions * self.n_neurons,
                mutual_inhib=-.4,
                net=nengo.Network("Action execution"))

            # BG -> Thalamus connection
            nengo.Connection(self.action_selection.output,
                             self.action_execution.input)
            nengo.Connection(self.actions.output, self.action_selection.input)

            # Enabling arm movement
            nengo.Connection(self.action_execution.output[0],
                             self.left_arm_enable, synapse=0.01,
                             transform=[[-1]])
            nengo.Connection(self.action_execution.output[1],
                             self.right_arm_enable, synapse=0.01,
                             transform=[[-1]])
            self.one = nengo.Node(output=1)

            nengo.Connection(self.one, self.left_arm_enable, synapse=0.01)
            nengo.Connection(self.one, self.right_arm_enable, synapse=0.01)
            # ------------------------------------------------------------------
            # endregion
            # region Killswitch
            nengo.Connection(self.killswitch, self.right_arm_enable)
            nengo.Connection(self.killswitch, self.left_arm_enable)
            # endregion
