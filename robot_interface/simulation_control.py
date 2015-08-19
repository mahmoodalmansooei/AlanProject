__author__ = 'Petrut Bogdan'

import logging
import threading

logger = logging.getLogger(__name__)


class SimulationControl(threading.Thread):
    def __init__(self, simulator, run_time=None):
        """
        A class that controls the simulation. It provides start and stop control
        over the simulation.
        :param simulator: A neural simulator (e.g. nengo Simulator or
        nengo_spinnaker Simulator)
        :type simulator: Simulator
        :param run_time: Time in seconds
        :type run_time: int
        :return:
        :rtype:
        """
        super(SimulationControl, self).__init__(name="SimulationControl Thread")
        self.simulator = simulator
        self.run_time = run_time

    def run(self):
        logger.log(logging.DEBUG, "Running the simulation in the " + self.name)

        if hasattr(self.simulator, '__exit__'):
            with self.simulator:
                self.simulator.run(self.run_time)
        else:
            self.simulator.run(self.run_time)

    def stop(self):
        """Stop a continuously running simulation or cut short a fixed
        length simulation"""
        logger.log(logging.DEBUG, "Stopping the " + self.name)
        if hasattr(self.simulator, 'stop'):
            self.simulator.stop()
