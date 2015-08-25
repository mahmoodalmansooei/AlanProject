..  _robot_control_readme:

Robot control
=============


.. toctree::

    Classes in the control package <robot_control>

Head description
----------------

The head is designed to have 3 degrees of freedom: the neck with 1 DOF, and the
eyes with 2 DOF. As a result, the control system takes in a tuple of values
representing the position the head needs to face towards as radians.

The control system has the following behaviour: be default the head is at
position (0,0), which means the head is orientated to look straight ahead, with
the eyes in the middle of their sockets. When it is issued a new position, the
neck and eyes start rotating at the same time, the eyes snap onto the target
and the neck continues rotating until the whole head is facing the target.

Example available :ref:`here <head_movement_demo>`.

API documentation: :class:`~robot_control.robot.Robot`.

Arm description
---------------

Each arm consists of 3 DOF: shoulder (1 DOF), elbow (1DOF), and finger (1DOF).
This is obviously not enough mobility to be able to reach all arbitrary 3D
positions, as a result a naive approximation is used. The shoulder's job is to
tilt the plane described by the shoulder, elbow and finger so that the target
position lies on this plane. Then the elbow rotates to try and point the lower
arm in the direction of the target.

.. warning::

   The current implementation uses a neural approximation of the
   :func:`numpy.arctan2` method. This is a highly discontinuous function which
   has difficulties in being represented in neurons. As a result, some positions
   will make the function oscillate between two opposite functions quickly.

   This behaviour will be amended in future.

API documentation: :class:`~robot_control.arm.Arm`.

Action selection and execution description
------------------------------------------

Action selection and execution is achieved with the use of a basal ganglia
(`Stewart, Bekolay, & Eliasmith, 2012 <http://journal.frontiersin.org/article/10.3389/fnins.2012.00002/full>`_)
and thalamus Nengo implementation.
The basal ganglia's action selection relies on inhibitory connections,
thus the selected action is the one which isn't inhibited.
The output from the basal ganglia is fed into
the thalamus, which activates only the action (or actions) which is selected.

The basal ganglia's action selection relies on inhibitory connections,
thus the selected action is the one which isn't inhibited. The output from the basal ganglia is fed into
the thalamus, which activates only the action (or actions) which is selected.

The current implementation allows to select any combination of 3 actions
(move head, move left hand, move right hand), though selecting all 3 actions
turns out to be quite noisy (might want to avoid). Modifying the standard
implementation to allow this type of selection means that not selecting any actions
is equivalent to selecting all of them at once.


Example available :ref:`here <action_selection_demo>`.

API documentation: :class:`~robot_control.action.ActionSelectionExecution`.

Using the classes
-----------------

The entire control system for the robot is contained within the robot.py module. 
In order to obtain useful behaviour from this class some inputs
and outputs have been integrated into the network and need to be set or acted upon
using the provided API.

The structure of the robot control system is show in figure below.

.. image:: http://i.imgur.com/QU2lF4T.png
   :alt: Robot module hierarchy

The inputs to the system are:

*   A. signal that controls whether the finger on the right hand should be lifted.


*   B. an arbitrary position in 3D space where the left hand will move towards if not asked to follow the lips.


*   C. analogous target position for the right hand.


*   D. a 2 dimensional input that controls whether the hand should target the lips (first dimension corresponds to the left hand, the second to the right hand).


*   E. a 3 dimensional input that selects the actions that can be performed. An unselected action is disabled, and thus any change in the inputs such as target are ignored. **Note:** not selecting any action to be executed is equivalent to selecting all actions.


*   F. a 2 dimensional input in the range [-pi/2, pi/2] representing the position which the head and eyes need to face.


*   G. signal that controls whether the finger on the left hand should be lifted.


The outputs are the motors and the done signal.

Some extra inputs are required into the system to make the movement accurate: feedback from motors.
