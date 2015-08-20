__author__ = 'Petrut Bogdan'

import nengo
import numpy as np
from arm import Arm, ArmType
from head import Head
from action import ActionSelectionExecution
from robot_interface.container import Container
from robot_models.motor import Motor
from robot_models.sensor import Sensor
from robot_models.control_signal import ControlSignal


class Robot(nengo.Network):
    def __init__(self, n_neurons=100, radius=1.7,
                 idle_left_hand_position=np.asarray([[.3, .5, -.7]]),
                 idle_right_hand_position=np.asarray([[.3, .5, -.7]]),
                 gamma=0, shoulder_width=.3, neck_length=.2,
                 upper_arm_length=.5, lower_arm_length=.5, lip_distance=.2,
                 tau=0.2,
                 shoulder_sensitivity=2., elbow_sensitivity=2.,
                 finger_sensitivity=1.0, sampling_period=100, dt=0.001,
                 initial_actions=np.array([1, 0, 0]),
                 initial_lip_enable=np.array([0, 0]),
                 initial_left_finger_enable=np.array([1]),
                 initial_right_finger_enable=np.array([1]),
                 initial_head_position=np.array([0, 0]),
                 external_feedback=False, label=None, seed=None,
                 add_to_container=None):
        """
        This class encapsulates all of the components that control a robot.
        In this case: two :py:class:`.Arm` s, a :py:class:`.Head` ,
        and a block that could be loosely defined as a
        cortex-basal ganglia-thalamus loop (the
        :py:class:`.ActionSelectionExecution` block).

        :param n_neurons: The number of neurons.
        :type n_neurons: int
        :param radius: The range of values that can be represented
        :type radius: float
        :param idle_left_hand_position: The target position for the left hand
            when not given a specific target
        :type idle_left_hand_position: numpy.ndarray
        :param idle_right_hand_position: The target position for the right hand
            when not given a specific target
        :type idle_right_hand_position: numpy.ndarray
        :param gamma: The "forward" incline of the upper arm
        :type gamma: float
        :param shoulder_width: The distance from the base of the neck to the
            shoulder.
        :type shoulder_width: float
        :param neck_length: The distance from the base of the neck to the
            center of the head.
        :type neck_length: float
        :param upper_arm_length: The distance from the shoulder to the elbow.
        :type upper_arm_length: float
        :param lower_arm_length: The distance from the elbow to the finger.
        :type lower_arm_length: float
        :param lip_distance: The distance from the center of the head to
            the lips.
        :type lip_distance: float
        :param tau: post synaptic time constant
        :type tau: float
        :param shoulder_sensitivity: how much to scale the motor output by
        :type shoulder_sensitivity: float
        :param elbow_sensitivity: how much to scale the motor output by
        :type elbow_sensitivity: float
        :param finger_sensitivity: how much to scale the motor output by
        :type finger_sensitivity: float
        :param sampling_period: The period which dictates how often the
            motors react to changes.
        :type sampling_period: float
        :param dt: timestep
        :type dt: float
        :param initial_actions:
        :type initial_actions: numpy.ndarray
        :param initial_lip_enable:
        :type initial_lip_enable: numpy.ndarray
        :param initial_left_finger_enable:
        :type initial_left_finger_enable: numpy.ndarray
        :param initial_right_finger_enable:
        :type initial_right_finger_enable: numpy.ndarray
        :param initial_head_position:
        :type initial_head_position: numpy.ndarray
        :param external_feedback: Selects if the system should allow for
            external feedback from sensors.
        :type external_feedback: bool
        :param label: Name of the model. Defaults to None.
        :type label: str
        :param seed: Random number seed that will be fed to the random
            number generator. Setting this seed makes the creation of the
            model a deterministic process; however, each new ensemble
            in the network advances the random number generator, so if
            the network creation code changes, the entire model changes.
        :type seed: int
        :param add_to_container: Determines if this Network will be added to
            the current container. Defaults to true iff currently with a Network
        :type add_to_container: bool
        """
        super(Robot, self).__init__(label, seed, add_to_container)
        # region Variable assignment
        self.finger_sensitivity = finger_sensitivity
        self.elbow_sensitivity = elbow_sensitivity
        self.shoulder_sensitivity = shoulder_sensitivity
        self.tau = tau
        self.shoulder_width = shoulder_width
        self.shoulder_position = np.asarray([shoulder_width, 0, -neck_length])
        self.idle_position = idle_left_hand_position
        self.radius = radius
        self.n_neurons = n_neurons
        self.elbow_position = np.asarray([upper_arm_length, 0, 0])
        self.gamma = gamma
        self.hand_position = np.asarray([0, lower_arm_length, 0])
        self.lip_position = np.asarray([0, lip_distance, 0])
        # endregion
        # Create a container in which to organise all the motors, sensors
        # and control signals
        self.motor_container = Container()
        self.sensor_container = Container()
        self.control_container = Container()
        self.killswitch_container = Container()
        with self:
            # region Control signals for the simulation
            self.actions = ControlSignal(self.control_container, size_out=3,
                                         label="Actions control signal")
            self.lip_enable = ControlSignal(self.control_container, size_out=2,
                                            label="Lip enable control signal")
            self.right_hand_position = ControlSignal(
                self.control_container, size_out=3,
                label="Right hand position control signal")
            self.left_hand_position = ControlSignal(
                self.control_container, size_out=3,
                label="Left hand position control signal")
            self.right_finger_enable = ControlSignal(
                self.control_container, size_out=1,
                label="Right finger enable control signal")
            self.left_finger_enable = ControlSignal(
                self.control_container, size_out=1,
                label="Left finger enable control signal")
            self.head_position = ControlSignal(
                self.control_container, size_out=2,
                label="Head position control signal")
            # endregion
            self.killswitch = ControlSignal(self.killswitch_container,
                                            size_out=1,
                                            label="Killswitch")
        # region Node outputs set to their initial values
        self.control_container.add(self.actions, initial_actions.ravel())
        self.control_container.add(self.lip_enable, initial_lip_enable.ravel())
        self.control_container.add(self.right_hand_position,
                                   idle_right_hand_position.ravel())
        self.control_container.add(self.left_hand_position,
                                   idle_left_hand_position.ravel())
        self.control_container.add(self.right_finger_enable,
                                   initial_right_finger_enable.ravel())
        self.control_container.add(self.left_finger_enable,
                                   initial_left_finger_enable.ravel())
        self.control_container.add(self.head_position,
                                   initial_head_position.ravel())
        self.killswitch_container.add(self.killswitch, 1)
        # endregion
        with self:
            # region Sensors
            self.head_sensor = Sensor(self.sensor_container,
                                      label="Head sensor")
            self.eye_x_sensor = Sensor(self.sensor_container,
                                       label="Eye x sensor")
            self.eye_y_sensor = Sensor(self.sensor_container,
                                       label="Eye y sensor")
            self.right_shoulder_sensor = Sensor(self.sensor_container,
                                                label="Right shoulder sensor")
            self.right_elbow_sensor = Sensor(self.sensor_container,
                                             label="Right elbow sensor")
            self.right_finger_sensor = Sensor(self.sensor_container,
                                              label="Right finger sensor")
            self.left_shoulder_sensor = Sensor(self.sensor_container,
                                               label="Left shoulder sensor")
            self.left_elbow_sensor = Sensor(self.sensor_container,
                                            label="Left elbow sensor")
            self.left_finger_sensor = Sensor(self.sensor_container,
                                             label="Left finger sensor")
            # endregion
            # region Motors
            self.head_motor = Motor(self.motor_container,
                                    sampling_period, dt,
                                    label="Head motor")
            self.eye_x_motor = Motor(self.motor_container,
                                     sampling_period, dt,
                                     label="Eye x motor")
            self.eye_y_motor = Motor(self.motor_container,
                                     sampling_period, dt,
                                     label="Eye y motor")
            self.right_shoulder_motor = Motor(self.motor_container,
                                              sampling_period, dt,
                                              label="Right shoulder motor")
            self.right_elbow_motor = Motor(self.motor_container,
                                           sampling_period, dt,
                                           label="Right elbow motor")
            self.right_finger_motor = Motor(self.motor_container,
                                            sampling_period, dt,
                                            label="Right finger motor")
            self.left_shoulder_motor = Motor(self.motor_container,
                                             sampling_period, dt,
                                             label="Left shoulder motor")
            self.left_elbow_motor = Motor(self.motor_container,
                                          sampling_period, dt,
                                          label="Left elbow motor")
            self.left_finger_motor = Motor(self.motor_container,
                                           sampling_period, dt,
                                           label="Left finger motor")
            # endregion
            # region Links
            self.right_arm = Arm(self.shoulder_position, self.elbow_position,
                                 self.hand_position, self.gamma,
                                 arm_type=ArmType.RIGHT,
                                 n_neurons=self.n_neurons,
                                 external_feedback=external_feedback,
                                 seed=seed,
                                 label="Right arm controller")
            self.left_arm = Arm(self.shoulder_position, self.elbow_position,
                                self.hand_position, self.gamma,
                                arm_type=ArmType.LEFT,
                                n_neurons=self.n_neurons,
                                external_feedback=external_feedback,
                                seed=seed,
                                label="Left arm controller")
            self.head = Head(self.lip_position, seed=seed,
                             external_feedback=external_feedback,
                             label="Head controller")
            self.action = ActionSelectionExecution(
                seed=seed, label="Action selection and execution")
            # endregion
            # Lip position available in action selection and execution
            nengo.Connection(self.head.lips_position, self.action.lip_position)

            # Action enables arm and head
            nengo.Connection(self.action.right_arm_enable,
                             self.right_arm.enable)
            nengo.Connection(self.action.left_arm_enable, self.left_arm.enable)
            nengo.Connection(self.action.head_enable, self.head.enable)

            nengo.Connection(self.killswitch, self.action.killswitch)

            # Targets propagated to concerned components
            nengo.Connection(self.action.right_arm_target_position,
                             self.right_arm.target_position.input)
            nengo.Connection(self.action.left_arm_target_position,
                             self.left_arm.target_position.input,
                             transform=[[-1, 0, 0],
                                        [0, 1, 0],
                                        [0, 0, 1]])
            nengo.Connection(self.action.head_position,
                             self.head.target_position.input)

            # Arm finger enabling propagation
            nengo.Connection(self.action.right_finger_enable,
                             self.right_arm.action_enable)
            nengo.Connection(self.action.left_finger_enable,
                             self.left_arm.action_enable)

            # region Motor connection
            nengo.Connection(self.head.head_motor, self.head_motor)
            nengo.Connection(self.head.eye_motor[0], self.eye_x_motor)
            nengo.Connection(self.head.eye_motor[1], self.eye_y_motor)

            nengo.Connection(self.right_arm.shoulder_motor,
                             self.right_shoulder_motor)
            nengo.Connection(self.right_arm.elbow_motor, self.right_elbow_motor)
            nengo.Connection(self.right_arm.finger_motor,
                             self.right_finger_motor)

            nengo.Connection(self.left_arm.shoulder_motor,
                             self.left_shoulder_motor)
            nengo.Connection(self.left_arm.elbow_motor, self.left_elbow_motor)
            nengo.Connection(self.left_arm.finger_motor,
                             self.left_finger_motor)
            # endregion
            # region Control signals
            self.everything_done = nengo.Ensemble(self.n_neurons, 1)
            nengo.Connection(self.head.done, self.everything_done,
                             transform=[[.4]],
                             synapse=self.tau)
            nengo.Connection(self.right_arm.done, self.everything_done,
                             transform=[[.4]],
                             synapse=self.tau)
            nengo.Connection(self.left_arm.done, self.everything_done,
                             transform=[[.4]],
                             synapse=self.tau)
            self.done = nengo.Node(size_in=1)
            nengo.Connection(self.everything_done, self.done)
            # endregion
            # region Connect control signals
            nengo.Connection(self.actions, self.action.actions.input)
            nengo.Connection(self.lip_enable, self.action.lip_enable)
            nengo.Connection(self.right_hand_position,
                             self.action.right_hand_position)
            nengo.Connection(self.left_hand_position,
                             self.action.left_hand_position)
            nengo.Connection(self.right_finger_enable,
                             self.action.right_finger_enable)
            nengo.Connection(self.left_finger_enable,
                             self.action.left_finger_enable)
            nengo.Connection(self.head_position, self.action.head_position)
            # endregion
            # region Connect sensors
            # Head
            nengo.Connection(self.head_sensor, self.head.external_head_error)
            nengo.Connection(self.eye_x_sensor, self.head.external_eye_x_error)
            nengo.Connection(self.eye_y_sensor, self.head.external_eye_y_error)

            # Right arm
            nengo.Connection(self.right_shoulder_sensor,
                             self.right_arm.external_shoulder_error)
            nengo.Connection(self.right_elbow_sensor,
                             self.right_arm.external_elbow_error)
            nengo.Connection(self.right_finger_sensor,
                             self.right_arm.external_finger_error)

            # Left arm
            nengo.Connection(self.left_shoulder_sensor,
                             self.left_arm.external_shoulder_error)
            nengo.Connection(self.left_elbow_sensor,
                             self.left_arm.external_elbow_error)
            nengo.Connection(self.left_finger_sensor,
                             self.left_arm.external_finger_error)
            # endregion

    def enable(self, is_enabled):
        """
        Enable or disable all the motors in the robot.

        :param is_enabled: Parameter which selects whether to enable or disable
            the motors.
        :type is_enabled: bool
        """
        if is_enabled:
            self.killswitch_container.update(self.killswitch, 0)
        else:
            self.killswitch_container.update(self.killswitch, 1)

    @property
    def sensors(self):
        """
        Property that returns the container with all the sensors within the
        robot

        :return: container with all the sensors within the
            robot
        :rtype: Container
        """
        return self.sensor_container

    @property
    def motors(self):
        """
        Property that returns the container with all the motors within the
        robot

        :return: the container with all the motors within the
            robot
        :rtype: Container
        """
        return self.motor_container

    @property
    def controls(self):
        """
        Property that returns the container with all the controls within the
        robot

        :return: container with all the controls within the
            robot
        :rtype: Container
        """
        return self.control_container

if __name__== "__main__":
    r = Robot()