__author__ = 'Petrut Bogdan'

import nengo
import numpy as np


class ControlSignal(nengo.Node):
    def __init__(self, container, size_out, label=None):
        """
        A node that controls the operation of the robot simulation by providing
        inputs to action selection and execution.

        :param container: The object that receives information from the node
        :type container: Container
        :param size_out: The dimensionality of the output
        :type size_out: int > 0
        :param label: The name of the node
        :type label: str
        :return: A control signal node
        :rtype: ControlSignal
        """
        self.container = container
        super(ControlSignal, self).__init__(output=self.control_signal_output,
                                            size_out=size_out,
                                            label=label)
        self.container.add(self, np.asarray([0]*size_out))

    def control_signal_output(self, time):
        """
        Function that is called every time tick for outputting values from the
        node.

        :param time: The current simulation time
        :type time: float
        :return: An array of size size_out
        :rtype: np.ndarray
        :raises: KeyError if control signal output not assigned in container
            before simulation starts
        """
        # TODO Make transmit period be adjustable
        return self.container[self]
