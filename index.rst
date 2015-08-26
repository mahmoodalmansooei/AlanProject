The Alan Project
================

**The Imitation Game** will be a major contemporary art exhibition curated by Clare Gannaway at Manchester
Art Gallery, UK, March-August 2016. Inspired by Manchester\'s rich history of computer science, it will
feature eight international contemporary artists exploring the theme of machines and the imitation of life.
The exhibition will be part of the cultural programme for Manchester\'s role as **European City of Science** in
2016.

Swedish artist Tove Kjellmark is making a new artwork for The Imitation Game exhibition, opening March
2016, in the form of two **human-like robots** which will sit in leather armchairs in the gallery and converse
with each other on topics yet to be decided. They will **detect and acknowledge the presence of human
visitors** to the gallery through **movement and speech**.

The robot control system presented herein relies on a
`Nengo <http://www.nengo.ca/>`__ spiking neural network simulation running on a
torus of `SpiNNaker <http://apt.cs.manchester.ac.uk/projects/SpiNNaker/>`__
boards and communicates with a robot or robot simulation using a specially made interface
that is completely agnostic of the underlying neural implementation. In effect, the interface allows the user
to treat the neural simulation as a black box, if desired.

.. image:: http://apt.cs.manchester.ac.uk/Images/Rotating_Doughnut_S2.gif
   :alt: SpiNNaker toroidal structure visualisation
   :align: center


The simulations have some well defined goals which can be easily split up into two
categories: functional and non-functional requirements. The former are:

-  Hand movement in front of lips to realise a silencing gesture

-  Robot faces the position it is asked to face (e.g. other robot or
   interrupting person)

-  Gesture while talking (small head and hand movement)

The non-functional requirements, dealing with how the system should
work, involve:

-  Simultaneous and smooth joint movement

-  Realistic movement


.. important::
   Please report any errors or inconsistencies to our  `Github repository <https://github.com/pabogdan/AlanProject/issues>`_ .

   For assistance or questions, you can reach us at pab@cs.man.ac.uk.

.. toctree::
   :maxdepth: 2


   Getting started <docs/start>

   docs/briefs

   docs/todo

   Examples <docs/examples>

   User guide <docs/user_guide>
