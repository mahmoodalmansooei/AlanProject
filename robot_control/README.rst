Robot control
=============

..  _robot_control_readme:

The control system for the robot consists of several independent modules, with some level of interconnection:

*   head controller

*   arm controller (one for each arm)

*   action selection (could be considered a meta-controller)

Head
----

Arm
---

Action selection
----------------


Using the classes
-----------------

The entire control system for the robot is contained within the robot.py module. 
In order to obtain useful behaviour from this class some inputs and outputs need to be connected to the system, as
can be seen in the following diagram.

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
