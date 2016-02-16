__author__ = 'Petrut Bogdan'

import nengo
import numpy as np


class Servo(nengo.Node):
    def __init__(self, container, size_in=None, label=None,
                 sampling_period=15):
        """
        A motor is a type of node that sends live information back for
        processing.

        :param container: The object that receives information from the motor
        :type container: Container
        :param sampling_period: The period with which the motor sends information
        :type sampling_period: float or int
        :param dt: The time step in seconds
        :type dt: float
        :param label: The name of the motor
        :type label: str
        :return: A motor node
        :rtype: Servo
        """
        self.container = container
        self.dt = 0.001
        self.delta = 0.00
        self.sampling_period = sampling_period * self.dt
        self.previous_time = -self.sampling_period
        self.container.add(self, [0] * size_in)
        super(Servo, self).__init__(output=self.servo_output,
                                    size_in=1 if not size_in else size_in,
                                    label=label)

    def servo_output(self, time, value):
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
            update_table = np.abs(value - self.container[self]) >= self.delta
            self.previous_time = time
            if np.any(update_table):
                delta_step_value = [
                    value[i] if update_table[i] else self.container[self][i] for
                    i in range(value.size)]
                self.container.update(self, value)
