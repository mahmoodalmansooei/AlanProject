__author__ = 'Petrut Bogdan'

import nengo


class Sensor(nengo.Node):
    def __init__(self, container, label=None):
        """
        A sensor is a type of node that inputs values into a simulation. It
        could represent the feedback value from a motor.

        :param container: The object that receives information from the sensor
        :type container: Container
        :param label: The name of the sensor
        :type label: str
        :return: A sensor node
        :rtype: Sensor
        """
        self.container = container
        self.container.add(self, 0.)
        super(Sensor, self).__init__(output=self.sensor_output, size_out=1,
                                     label=label)

    def sensor_output(self, time):
        """
        Function that is called every time tick for outputting values from the
        node.

        :param time: The current simulation time
        :type time: float
        :return: Value of the sensor (as stored in container)
        :rtype: float
        """
        # TODO Make transmit period be adjustable
        return self.container[self]
