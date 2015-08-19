__author__ = 'Petrut Bogdan'

from robot_control.robot import Robot
from simulation_control import SimulationControl
import nengo_spinnaker


class AlanRobot(object):
    def __init__(self, run_time=None, period=None, **simulation_parameters):
        """
        This object is an interface for controlling the Robot simulation.
        :param run_time: How long to run the simulation for in seconds
        :type run_time: int
        :param period:  Duration of one period of the simulator. This determines
            how much memory will be allocated to store
            precomputed and probed data.
        :type period: float or None
        :param simulation_parameters: Parameters of the Robot Network. See Robot
            docs for a list of the parameters and what they each represent.
        :type simulation_parameters: dict
        :return: An AlanRobot object
        :rtype: AlanRobot
        """
        if simulation_parameters:
            self.robot = Robot(simulation_parameters)
        else:
            self.robot = Robot()

        self.simulation_control = SimulationControl(
            nengo_spinnaker.Simulator(self.robot, period=period), run_time)

    def start_simulation(self):
        """
        Start the simulation
        """
        self.simulation_control.start()

    def stop_simulation(self):
        """
        Stop the simulation. This will be the last action.
        """
        self.simulation_control.stop()

    def enable_robot(self):
        """
        By default, the robot will start with all motor abilities disabled.
        Calling this method will allow the robot to send motor information.
        """
        self.robot.enable(True)

    def disable_robot(self):
        """
        Disable the robot's motor capabilities.
        """
        self.robot.enable(False)

    @property
    def controls(self):
        return self.robot.controls

    @property
    def sensors(self):
        return self.robot.sensors

    @property
    def motors(self):
        return self.robot.motors

    @staticmethod
    def contents(container):
        return container.dictionary.keys()
