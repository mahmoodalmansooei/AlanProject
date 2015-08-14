__author__ = 'Petrut Bogdan'

import nengo


class Motor(nengo.Node):
    def __init__(self, container, sampling_period=100, dt=0.001, label=None):
        """
        A motor is a type of node that sends live information back for
        processing. This is different from a standard node because it only
        sends information at a certain frequency, not at every change due to
        limitations in the communication channel.
        :param container: The object that receives information from the motor
        :type container: Container
        :param sampling_period: The period with which the motor sends information
        :type sampling_period: float or int
        :param dt: The time step in seconds
        :type dt: float
        :param label: The name of the motor
        :type label: str
        :return: A motor node
        :rtype: Motor
        """
        self.sampling_period = sampling_period * dt  # ms
        self.previous_time = - self.sampling_period
        self.container = container
        super(Motor, self).__init__(output=self.motor_output, size_in=1,
                                    label=label)

    def motor_output(self, time, values):
        """
        Function that is called every time tick for outputting values from the
        node.
        :param time: The current simulation time
        :type time: float
        :param values: The current values of the motor node (number of values
        depends on the dimensionality of the node)
        :type values: array of floats
        :return: None
        :rtype:
        """
        if time - self.previous_time >= self.sampling_period:
            self.previous_time = time
            self.container.update(self, values)
