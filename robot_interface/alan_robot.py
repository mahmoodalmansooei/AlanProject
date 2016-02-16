__author__ = 'Petrut Bogdan'

from robot_control.robot import Robot
from simulation_control import SimulationControl
import nengo_spinnaker
import numpy as np


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
        :param simulation_parameters: Parameters of the Robot Network. See
            :class:`.Robot` for a list of the parameters and what
            they each represent.
        :type simulation_parameters: dict
        """
        self.robot = Robot()

        self.simulation_control = SimulationControl(
            nengo_spinnaker.Simulator(self.robot, period=period,
                                      **simulation_parameters), run_time)

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
        """
        Getter for controls container

        :return: Container filled with all the controls feeding into the robot
        :rtype: Container
        """
        return self.robot.controls

    @property
    def sensors(self):
        """
        Getter for sensors container

        :return: Container filled with all the sensors feeding into the robot
        :rtype: Container
        """
        return self.robot.sensors

    @property
    def motors(self):
        """
        Getter for motors container

        :return: Container filled with all the motors in the robot
        :rtype: Container
        """
        return self.robot.motors

    @property
    def servos(self):
        """
        Getter for motors container

        :return: Container filled with all the motors in the robot
        :rtype: Container
        """
        return self.robot.servos

    @staticmethod
    def contents(container):
        """
        Returns a list of all the keys in the container

        :return: a list of all the keys in the container
        :rtype: list
        """
        return container.dictionary.keys()

    @staticmethod
    def labels(container):
        for k in container.dictionary.keys():
            yield k.label

    @staticmethod
    def key_with_label_in_container(label, container):
        for k in container.dictionary.keys():
            if k.label == label:
                return k

    def silence(self, position=np.asarray([.4, .8, 1])):
        """
        Method that causes the robot to make a silencing gesture
        :param position:
        :type position:
        :return:
        :rtype:
        """
        # retrieve control signal responsible for position
        silence = AlanRobot.key_with_label_in_container("silence",
                                                        self.controls)
        self.controls.update(silence, position)

        # retrieve control signal responsible for direction
        direction = AlanRobot.key_with_label_in_container("direction",
                                                          self.controls)

        # choose a random direction (either left or right)
        self.controls.update(direction, np.asarray(
            [.7, .7]) if np.random.rand() > .5 else np.asarray([-.7, .7]))

        # retrieve control signal responsible for action selection
        action = AlanRobot.key_with_label_in_container("action",
                                                       self.controls)
        self.controls.update(action, np.asarray([0., 1., 0.]))

    def gesture(self):
        """
        Method that causes the robot to gesture
        :return:
        :rtype:
        """
        # retrieve control signal responsible for direction
        direction = AlanRobot.key_with_label_in_container("direction",
                                                          self.controls)

        # choose a random direction (left, right or both)
        possible_direction = [np.asarray([1., 0.]), np.asarray([.7, .7]), np.asarray([-.7, .7])]
        self.controls.update(direction, possible_direction[np.random.randint(0, len(possible_direction))])

        # retrieve control signal responsible for action selection
        action = AlanRobot.key_with_label_in_container("action",
                                                       self.controls)
        self.controls.update(action, np.asarray([1., 0., 0.]))

    def idle(self):
        """
        Method that causes the robot to idle
        :return:
        """
         # retrieve control signal responsible for action selection
        action = AlanRobot.key_with_label_in_container("action",
                                                       self.controls)
        self.controls.update(action, np.asarray([0., 0., 1.]))