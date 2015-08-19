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

        :param n_neurons:
        :type n_neurons:
        :param tau:
        :type tau:
        :param label:
        :type label:
        :param seed:
        :type seed:
        :param add_to_container:
        :type add_to_container:
        :return: a new action selection and execution network
        :rtype: ActionSelectionExecution
        """
        super(ActionSelectionExecution, self).__init__(label, seed,
                                                       add_to_container)

        # region Variable assignment
        self.dimensions = 3
        self.n_neurons = n_neurons
        self.tau = tau
        self.radius = radius
        # endregion
        with self:
            # region inputs
            # ------------------------------------------------------------------
            # Exterior decided hand target position
            self.right_hand_position = nengo.Ensemble(6 * self.n_neurons, 3,
                                                      radius=self.radius)
            self.left_hand_position = nengo.Ensemble(6 * self.n_neurons, 3,
                                                     radius=self.radius)

            # Input actions from outside
            self.actions = nengo.networks.EnsembleArray(self.n_neurons,
                                                        self.dimensions)
            # Exterior decided head target position
            self.head_position = nengo.Ensemble(4 * self.n_neurons, 2,
                                                radius=self.radius)

            # Lip position should come from the Head module, thus closing the
            # Cortex -> Basal ganglia -> Thalamus loop
            self.lip_position = nengo.Ensemble(6 * self.n_neurons, 3,
                                               radius=self.radius)
            # ------------------------------------------------------------------
            # endregion
            # region controls
            # ------------------------------------------------------------------
            # Control for the finger
            self.right_finger_enable = nengo.Ensemble(self.n_neurons,
                                                      dimensions=1)
            self.left_finger_enable = nengo.Ensemble(self.n_neurons,
                                                     dimensions=1)

            # Control for the lips (passes head computed lip position
            # to the arm)
            self.lip_enable = nengo.Ensemble(4 * self.n_neurons, dimensions=2)
            # Killswitch
            self.killswitch = nengo.Ensemble(self.n_neurons, 1)

            # ------------------------------------------------------------------
            # endregion
            # region outputs
            # ------------------------------------------------------------------
            self.head_enable = nengo.Ensemble(self.n_neurons, 1)

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
                self.dimensions, n_neurons_per_ensemble=3 * self.n_neurons,
                mutual_inhib=-.4,
                net=nengo.Network("Action execution"))

            # BG -> Thalamus connection
            nengo.Connection(self.action_selection.output,
                             self.action_execution.input)
            nengo.Connection(self.actions.output, self.action_selection.input)

            # Enabling arm/head movement
            nengo.Connection(self.action_execution.output[0],
                             self.head_enable, synapse=0.01,
                             transform=[[-1]])
            nengo.Connection(self.action_execution.output[1],
                             self.left_arm_enable, synapse=0.01,
                             transform=[[-1]])
            nengo.Connection(self.action_execution.output[2],
                             self.right_arm_enable, synapse=0.01,
                             transform=[[-1]])
            self.one = nengo.Node(output=1)

            nengo.Connection(self.one, self.head_enable, synapse=0.01)
            nengo.Connection(self.one, self.left_arm_enable, synapse=0.01)
            nengo.Connection(self.one, self.right_arm_enable, synapse=0.01)
            # ------------------------------------------------------------------
            # endregion
            # region Right hand target selection and output
            # Basal ganglia selects between the sources of the target
            self.right_hand_position_selector = nengo.networks.BasalGanglia(
                dimensions=2, n_neurons_per_ensemble=self.n_neurons,
                net=nengo.Network("Right hand target position selector"))

            # Inputs to the ganglia. In standard python code:
            # if lip_enable:
            #   arm_target_position = lip_position
            # else:
            #   arm_target_position = hand_position
            nengo.Connection(self.lip_enable[1],
                             self.right_hand_position_selector.input[0])
            nengo.Connection(self.lip_enable[1],
                             self.right_hand_position_selector.input[1],
                             function=lambda x: 1 - x)

            self.right_hand_position_computer = nengo.networks.Thalamus(
                dimensions=2, n_neurons_per_ensemble=2 * self.n_neurons,
                net=nengo.Network("Right hand target position computer"))

            nengo.Connection(self.right_hand_position_selector.output,
                             self.right_hand_position_computer.input)

            self.right_lip_mm = nengo.Ensemble(self.n_neurons, 1)
            nengo.Connection(self.right_hand_position_computer.output[0],
                             self.right_lip_mm)
            # Matrix multiplication 1
            self.right_lip_multiplier = MatrixMultiplication(
                2 * self.n_neurons, matrix_A=np.zeros((1, 1)),
                matrix_B=np.zeros((1, 3)))
            nengo.Connection(self.lip_position, self.right_lip_multiplier.in_B)
            nengo.Connection(self.right_lip_mm, self.right_lip_multiplier.in_A)

            self.right_hand_mm = nengo.Ensemble(self.n_neurons, 1)
            nengo.Connection(self.right_hand_position_computer.output[1],
                             self.right_hand_mm)
            # Matrix multiplication 2
            self.right_hand_multiplier = MatrixMultiplication(
                2 * self.n_neurons, matrix_A=np.zeros((1, 1)),
                matrix_B=np.zeros((1, 3)))

            self.right_arm_target_position = nengo.Ensemble(6 * self.n_neurons,
                                                            3, radius=1.7)
            nengo.Connection(self.right_hand_position,
                             self.right_hand_multiplier.in_B)
            nengo.Connection(self.right_hand_mm,
                             self.right_hand_multiplier.in_A)

            nengo.Connection(self.right_lip_multiplier.output,
                             self.right_arm_target_position,
                             synapse=self.tau)
            nengo.Connection(self.right_hand_multiplier.output,
                             self.right_arm_target_position,
                             synapse=self.tau)
            # endregion
            # region Left hand target selection and output
            # Basal ganglia selects between the sources of the target
            self.left_hand_position_selector = nengo.networks.BasalGanglia(
                dimensions=2, n_neurons_per_ensemble=self.n_neurons,
                net=nengo.Network("Left hand target position selector"))

            # Inputs to the ganglia. In standard python code:
            # if lip_enable:
            #   arm_target_position = lip_position
            # else:
            #   arm_target_position = hand_position
            nengo.Connection(self.lip_enable[0],
                             self.left_hand_position_selector.input[0])
            nengo.Connection(self.lip_enable[0],
                             self.left_hand_position_selector.input[1],
                             function=lambda x: 1 - x)

            self.left_hand_position_computer = nengo.networks.Thalamus(
                dimensions=2, n_neurons_per_ensemble=2 * self.n_neurons,
                net=nengo.Network("Left hand target position computer"))

            nengo.Connection(self.left_hand_position_selector.output,
                             self.left_hand_position_computer.input)

            self.left_lip_mm = nengo.Ensemble(self.n_neurons, 1)
            nengo.Connection(self.left_hand_position_computer.output[0],
                             self.left_lip_mm)
            # Matrix multiplication 1
            self.left_lip_multiplier = MatrixMultiplication(
                2 * self.n_neurons, matrix_A=np.zeros((1, 1)),
                matrix_B=np.zeros((1, 3)))
            nengo.Connection(self.lip_position, self.left_lip_multiplier.in_B)
            nengo.Connection(self.left_lip_mm, self.left_lip_multiplier.in_A)

            self.left_hand_mm = nengo.Ensemble(self.n_neurons, 1)
            nengo.Connection(self.left_hand_position_computer.output[1],
                             self.left_hand_mm)
            # Matrix multiplication 2
            self.left_hand_multiplier = MatrixMultiplication(
                2 * self.n_neurons, matrix_A=np.zeros((1, 1)),
                matrix_B=np.zeros((1, 3)))

            self.left_arm_target_position = nengo.Ensemble(6 * self.n_neurons,
                                                           3, radius=1.7)
            nengo.Connection(self.left_hand_position,
                             self.left_hand_multiplier.in_B)
            nengo.Connection(self.left_hand_mm,
                             self.left_hand_multiplier.in_A)

            nengo.Connection(self.left_lip_multiplier.output,
                             self.left_arm_target_position,
                             synapse=self.tau)
            nengo.Connection(self.left_hand_multiplier.output,
                             self.left_arm_target_position,
                             synapse=self.tau)
            # endregion
            # region Killswitch
            nengo.Connection(self.killswitch, self.right_arm_enable)
            nengo.Connection(self.killswitch, self.left_arm_enable)
            nengo.Connection(self.killswitch, self.head_enable)
            # endregion
