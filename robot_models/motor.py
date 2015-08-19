__author__ = 'Petrut Bogdan'

import nengo


class Motor(nengo.Node):
    """
        A motor is a type of node that sends live information back for
        processing.
    """
    def __init__(self, container, sampling_period=100, dt=0.001, label=None):
        """

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
        self.sampling_period = sampling_period * dt  # seconds
        self.previous_time = - self.sampling_period
        self.container = container
        super(Motor, self).__init__(output=self.motor_output, size_in=1,
                                    label=label)

    def motor_output(self, time, value):
        """
        Function that is called every time tick for outputting a value from the
        node, but only updates the motor's value once every period * dt seconds.

        Time is used for outputting with a specific frequency.

        :param time: The current simulation time
        :type time: float
        :param value: The current value of the motor node
        :type value: floats
        """
        if time - self.previous_time >= self.sampling_period:
            self.previous_time = time
            self.container.update(self, value)
