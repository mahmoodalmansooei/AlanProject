__author__ = 'Petrut Bogdan'

import nengo


class Motor(nengo.Node):
    def __init__(self, sampling_period=100, dt=1000., label=None):
        self.sampling_period = sampling_period / dt  # ms
        self.previous_time = - self.sampling_period
        super(Motor, self).__init__(output=self.motor_output, size_in=1,
                                    label=label)

    def motor_output(self, t, x):
        if t - self.previous_time >= self.sampling_period:
            self.previous_time = t
            print self.label, t, x
