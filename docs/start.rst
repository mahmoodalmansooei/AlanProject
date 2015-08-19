Getting started
===============

Requirements
------------

Running the software requires a `Python 2.7 <https://www.python.org/download/releases/2.7/>`_ interpreter.
This means it should run on all operating systems.

Running such a large simulation with a real-time constraint requires the use of the ^^SpiNNaker^^ platform.
As a result, the software in its current state does not support running the simulation via the provided
interface on host, but running only the simulation on host


Windows specific
^^^^^^^^^^^^^^^^

Windows users need to install the  `Microsoft Visual C++ Compiler for Python 2.7 <http://www.microsoft.com/en-gb/download/details.aspx?id=44266>`_
which is used when installing the ``numpy`` package.


Installation
------------

The easiest way to install everything is to clone the Alan Project repository, then run ``setup.py``. This
will install all required dependencies automatically.

.. note::

    The use of a ``virtualenv`` is recommended.

.. warning::

    The current ``pip`` installation of ``nengo`` and ``nengo_spinnaker`` are broken. It might be sensible to install them manually from their respective repositories_.

.. _repositories: https://github.com/nengo/nengo


.. code:: bash

    git clone https://github.com/pabogdan/AlanProject
    cd AlanProject
    python setup.py develop

The last step is to run the following script. This step will guide you through setting up a configuration file for
communicating to a SpiNNaker board.

.. code::

    nengo_spinnaker_setup

Optional
^^^^^^^^

Installing the ``scipy`` package would increase the accuracy of the basal ganglia in the neural
simulation. This needs to be installed separately if desired.

Installing the ``nengo_gui`` package would allow for running graphically interactive neural simulations
with the possibility of viewing live output from it. There are two types of installations available for
it: using pip

.. code-block:: bash

    [sudo] pip install nengo_gui

or manual installation from their Git repository

.. code-block:: bash

    git clone https://github.com/nengo/nengo_gui
    cd nengo_gui
    python setup.py develop

For ``nengo_gui`` usage information visit their Github repository.

Basic usage
-----------
This section will only focus on usage of the simulation through the provided interface. For an
in-depth look into how to run your own or modify existing nengo spiking neural network simulations,
visit their documentation_ webpages.

.. _documentation: https://pythonhosted.org/nengo/

Nengo simulation
^^^^^^^^^^^^^^^^

The starting point for the control system is the Robot class, which is a stand-alone, complete and
modular ``nengo.Network``.

.. code-block:: python
    :linenos:

    import nengo
    from robot_control.robot import Robot

    model = nengo.Network()

    with model:
        robot = Robot()

At this point, the simulation has not started yet, only the object has been built. In order to start
the simulation we need to either run the above in ``nengo_gui`` or create a simulator.

.. code-block:: python
    :linenos:

    sim = nengo.Simulator(model)
    sim.run(10)

.. note::

    Running the above code in ``nengo_gui`` would also expose the inputs and outputs of the system.


The same general process goes for running simulations on SpiNNaker, with one of the small differences
being that the ``Simulator`` object that needs creating lives inside ``nengo_spinnaker``

.. note::

    A more detailed description of the neuromorphic control system is available at the following pages:

    .. toctree::
        :maxdepth: 2

        Robot control<../robot_control/README>

    The following are utilities for creating control systems in a spiking neural network setting. Not all of them
    might have been used in the current implementation.

    .. toctree::
        :maxdepth: 2

        SNN utilities <../robot_utils/README>


Simulation interface
^^^^^^^^^^^^^^^^^^^^

The purpose of this interface is to allow people with no experience working with neural simulations using ``Nengo`` to
abstract that part software and just use a few API calls to achieve their goals.

For example, the following snippet of code is sufficient to place a neural simulation on a SpiNNaker board,

.. code-block:: python
    :linenos:

    from robot_interface.alan_robot import AlanRobot # Import the package

    robot = AlanRobot(run_time=5, period=10) # Create an instance of the robot
    robot.start_simulation() # Start the neural simulation
    robot.enable_robot() # By default, the robot's motors can't be driven,
                         # so this call enables the robot's motors



