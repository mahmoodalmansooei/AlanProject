Alan Project general information
================================

**The Imitation Game** will be a major contemporary art exhibition curated by Clare Gannaway at Manchester
Art Gallery, UK, March-August 2016. Inspired by Manchester\'s rich history of computer science, it will
feature eight international contemporary artists exploring the theme of machines and the imitation of life.
The exhibition will be part of the cultural programme for Manchester\'s role as **European City of Science** in
2016.

Artist Tove Kjellmark (Sweden) is making a new artwork for The Imitation Game exhibition, opening March
2016, in the form of two **human-like robots** which will sit in leather armchairs in the gallery and converse
with each other on topics yet to be decided. They will **detect and acknowledge the presence of human
visitors** to the gallery through **movement and speech**.

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

.. code:: bash

    git clone https://github.com/pabogdan/AlanProject
    cd AlanProject
    python setup.py develop

The last step is to

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

or direct and guaranteed up-to-date installation from their Git repository

.. code-block:: bash

    git clone https://github.com/nengo/nengo_gui
    cd nengo_gui
    python setup.py develop

For ``nengo_gui`` usage information visit their Github repository.

