Planned development
===================

..  _todo:

The work remaining should not interfere with the deliverables. In other words,
the current version of the software should be sufficient for the art exhibition
in Manchester.

The purpose of these planned changes is to demonstrate a working control system
without the need to physically build a robot, operating according to
specifications. Additionally, the code documented here should be understandable,
reusable and efficient, a possible basis for future development and improvement.

Refactoring work
^^^^^^^^^^^^^^^^

-   Refactor :py:class:`robot_control.robot.Robot` so that it takes as arguments a left hand,
    a right hand, a head and an action selection module, so that
    they can be independently modified by radii and lengths.

-   Refactor :py:class:`robot_control.arm.Arm` to occupy fewer SpiNNaker cores, eventually
    fitting the whole system on one 48-node SpiNNaker board without compromising
    accuracy

Expansions
^^^^^^^^^^

-   Interface the neural robot controller with ROS_

-   Explore alternative ways to compute trajectory in order to reach arbitrary
    targets in 3D space

-   The neural control system could learn from how much it undershoots or
    overshoots and adapt on the fly based on feedback from sensors
    (reinforcement learning).

-   Provide visual information to robot using a silicon sensor retina

Validation
^^^^^^^^^^

-   Using ROS_ and the neural control system, control a simulated robot using
    a publicly available robot simulation software

-   Write comprehensive, automated tests

.. _ROS: http://www.ros.org/