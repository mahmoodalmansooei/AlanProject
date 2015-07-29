__author__ = 'Petrut Bogdan'

import nengo
import numpy as np
from robot_utils.matrix_multiplication import MatrixMultiplication

_scalar = np.asarray(np.zeros((1, 1)))
_vector = np.asarray(np.zeros((1, 3)))


class ActionSelectionExecution(nengo.Network):
    def __init__(self, dimensions, n_neurons=100, tau=0.01, radius=1.7,
                 label=None, seed=None, add_to_container=None):
        """
        Actions:
        *   move head [0]
        *   move arm  [1]
        Params:
        *   finger on/off
        *   target = lips / general
        :param dimensions:
        :type dimensions:
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
        self.dimensions = dimensions
        self.n_neurons = n_neurons
        self.tau = tau
        self.radius = radius
        # endregion
        with self:
            # region inputs
            # ------------------------------------------------------------------
            # Exterior decided hand target position
            self.hand_position = nengo.Ensemble(5 * self.n_neurons, 3,
                                                radius=self.radius)

            # Input actions from outside
            self.actions = nengo.networks.EnsembleArray(self.n_neurons,
                                                        dimensions)
            # Exterior decided head target position
            self.head_position = nengo.Ensemble(4 * self.n_neurons, 2,
                                                radius=self.radius)

            # Lip position should come from the Head module, thus closing the
            # Cortex -> Basal ganglia -> Thalamus loop
            self.lip_position = nengo.Ensemble(5 * self.n_neurons, 3,
                                               radius=self.radius)
            # ------------------------------------------------------------------
            # endregion
            # region controls
            # ------------------------------------------------------------------
            # Control for the finger
            self.finger_enable = nengo.Ensemble(self.n_neurons, dimensions=1)

            # Control for the lips (passes head computed lip position
            # to the arm)
            self.lip_enable = nengo.Ensemble(3 * self.n_neurons, dimensions=1)
            # ------------------------------------------------------------------
            # endregion
            # region outputs
            # ------------------------------------------------------------------
            self.head_enable = nengo.Ensemble(self.n_neurons, 1)

            self.arm_enable = nengo.Ensemble(self.n_neurons, 1)
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
                             self.arm_enable, synapse=0.01,
                             transform=[[-1]])
            self.one = nengo.Node(output=1)

            nengo.Connection(self.one, self.head_enable, synapse=0.01)
            nengo.Connection(self.one, self.arm_enable, synapse=0.01)
            # ------------------------------------------------------------------
            # endregion
            # region Hand target selection and output
            # Basal ganglia selects between the sources of the target
            self.hand_position_selector = nengo.networks.BasalGanglia(
                dimensions=2, n_neurons_per_ensemble=self.n_neurons,
                net=nengo.Network("Hand target position selector"))

            # Inputs to the ganglia. In standard python code:
            # if lip_enable:
            #   arm_target_position = lip_position
            # else:
            #   arm_target_position = hand_position
            nengo.Connection(self.lip_enable,
                             self.hand_position_selector.input[0])
            nengo.Connection(self.lip_enable,
                             self.hand_position_selector.input[1],
                             function=lambda x: 1 - x)

            self.hand_position_computer = nengo.networks.Thalamus(
                dimensions=2, n_neurons_per_ensemble=2 * self.n_neurons,
                net=nengo.Network("Hand target position computer"))

            nengo.Connection(self.hand_position_selector.output,
                             self.hand_position_computer.input)

            self.lip_mm = nengo.Ensemble(6 * self.n_neurons, 4,
                                         radius=1.7)
            nengo.Connection(self.lip_position, self.lip_mm[0:3])
            nengo.Connection(self.hand_position_computer.output[0],
                             self.lip_mm[3])

            self.hand_mm = nengo.Ensemble(6 * self.n_neurons, 4,
                                          radius=1.7)
            nengo.Connection(self.hand_position, self.hand_mm[0:3])
            nengo.Connection(self.hand_position_computer.output[1],
                             self.hand_mm[3])

            self.arm_target_position = nengo.Ensemble(6 * self.n_neurons, 3,
                                                      radius=1.7)

            nengo.Connection(self.lip_mm, self.arm_target_position,
                             synapse=self.tau,
                             function=lambda x: [x[0] * x[3], x[1] * x[3],
                                                 x[2] * x[3]])
            nengo.Connection(self.hand_mm, self.arm_target_position,
                             synapse=self.tau,
                             function=lambda x: [x[0] * x[3], x[1] * x[3],
                                                 x[2] * x[3]])

            # endregion


if __name__ == "__main__":
    selection = ActionSelectionExecution(2)
