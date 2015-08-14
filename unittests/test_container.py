__author__ = 'Petrut Bogdan'

from unittest import TestCase
from robot_interface.container import Container, ContainerThread
from time import sleep


class TestContainer(TestCase):
    def test_add(self):
        self.container = Container()
        to_add = [[0, 1], [-1, 2], [15, 4]]
        for tup in to_add:
            self.container.add(key=tup[0], value=tup[1])
        sleep(.5)
        for tup in to_add:
            self.assertIn(tup[0], self.container.dictionary.keys(),
                          str(tup[0]) + " not in keys")
            self.assertIn(tup[1], self.container.dictionary.values(),
                          str(tup[1]) + " not in values")

    def test_update_with_default_callback(self):
        out = []
        self.container = Container(
            default_callback=lambda x, y: out.append(y + 1))
        to_add = [[0, 1], [-1, 2], [15, 4]]
        for tup in to_add:
            self.container.add(key=tup[0], value=tup[1])

        for tup in to_add:
            self.container.update(key=tup[0], value=tup[1])
        sleep(.5)

        for tup in to_add:
            self.assertIn(tup[1] + 1, out,
                          str(tup[1]) + " not in lambda produced values")

    def test_update_with_callback_overwriting_default_callback(self):
        out = []
        self.container = Container(
            default_callback=lambda x, y: out.append(y + 1))
        to_add = [[0, 1], [-1, 2], [15, 4]]
        for tup in to_add:
            self.container.add(key=tup[0], value=tup[1])

        for tup in to_add:
            self.container.update(key=tup[0], value=tup[1])
        sleep(.5)

        for tup in to_add:
            self.assertIn(tup[1] + 1, out,
                          str(tup[1]) + " not in lambda produced values")

    def test_update(self):
        out = []
        self.container = Container(default_callback=lambda x, y: y - 1)
        to_add = [[0, 1], [-1, 2], [15, 4]]
        for tup in to_add:
            self.container.add(key=tup[0], value=tup[1])

        for tup in to_add:
            self.container.update(key=tup[0], value=tup[1],
                                  callback=lambda x, y: out.append(y + 1))
        sleep(.5)

        for tup in to_add:
            self.assertIn(tup[1] + 1, out,
                          str(tup[1]) + " not in lambda produced values")

    def test_thread(self):
        out = []
        self.container = Container(
            default_callback=lambda x, y: out.append(y + 1))
        self.container_thread = ContainerThread(self.container)
        self.container_thread.start()
        to_add = [[0, 1], [-1, 2], [15, 4]]
        for tup in to_add:
            self.container_thread.container.add(key=tup[0], value=tup[1])

        for tup in to_add:
            self.container_thread.container.update(key=tup[0], value=tup[1])
        self.container_thread.stop()
        sleep(.5)

        for tup in to_add:
            self.assertIn(tup[1] + 1, out,
                          str(tup[1]) + " not in lambda produced values")

    def test_callable_check(self):
        with self.assertRaises(AssertionError):
            self.container = Container(3)

    def test_getitem(self):
        self.container = Container()
        to_add = {0: 1, -1: 2, 15: 4}
        for key in to_add.iterkeys():
            self.container.add(key=key, value=to_add[key])
        for key in to_add.iterkeys():
            self.assertEqual(to_add[key], self.container[key],
                             str(to_add[key]) + " not in values")
