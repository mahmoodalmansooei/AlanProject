..  _robot_interface_readme:

Interface
=========


The interface acts as a wrapper around the neural simulation.
It controls when the simulations starts, but it can also interrupt it while
running; it controls whether the robot is allowed to move or not; and,
critically, it allows to control the parameters of the simulation by modifying
the values input by the sensors and control signals and the acting upon the
values output by the motors.

The interface relies heavily on :ref:`models <robot_models_readme>` to inject
and extract information from the simulation running on SpiNNaker.

.. toctree::

    Classes in the interface package <robot_interface>
