..  _robot_models_readme:

Robot models
============


Classes in the models package usually extend Nengo objects
(most commonly, Nodes). The objects exist on host to inject or
extract values into and from SpiNNaker.

In the current implementation of nengo_spinnaker, nodes transmit their value
to the SpiNNaker board as soon as they are computed, and SpiNNaker sends
output node updates approximately every 10 timesteps (in the case that a
timestep is 1ms then every 10ms).


When running a simulation using the provided interface, e.g. using the
AlanRobot class, the user can retrieve all the inputs and outputs present
in the robot. We suggest **not** adding any callbacks to input nodes as those
will severely reduce the performance of the system.

.. toctree::

    Classes in the models package <robot_models>