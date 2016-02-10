__author__ = 'Petrut Bogdan'
import threading
import thread


class Container(object):
    def __init__(self, default_callback=None):
        """
        Container is an object that keeps track of different keys and
        potentially triggers a callback when the value is changed.

        Can be run in a ContainerThread.

        :param default_callback: a default callback for all the elements in the
            container
        :type default_callback: callable
        """
        self.default_callback = default_callback
        if default_callback:
            assert callable(default_callback)

        self.dictionary = dict()

    def add(self, key, value):
        """
        Add the key to the container with an initial value

        :param key: The :py:mod:`.robot_models` object to track
        :type key: class from :py:mod:`.robot_models`
        :param value: The value associated with the key
        :type value: float
        """
        self.dictionary[key] = value

    def update(self, key, value, callback=None):
        """
        This method should only be used to update inputs (i.e. sensors and
        control signals), not outputs such as motors.

        :param key: The :py:mod:`.robot_models` object to track
        :type key: class from :py:mod:`.robot_models`
        :param value: The value associated with the key
        :type value: numpy.ndarray
        :param callback: The method to be called when a value is updated. Leave
            as None to use default callback.
        :type callback: callable
        """
        callback = callback if callback else self.default_callback
        self.dictionary[key] = value
        if callback:
            thread.start_new_thread(callback, (key, value))

    def set_default_callback(self, callback):
        """
        Assigns a default callback to the container.

        :param callback: The default method to be called when a value is updated
        :type callback: callable
        """
        self.default_callback = callback
        if callback:
            assert callable(callback)

    def __getitem__(self, item):
        """
            See documentation for :py:meth:`~object.__getitem__` in Python
            docs.
        """
        return self.dictionary[item]


class ContainerThread(threading.Thread):
    """
        ContainerThread offers the possibility to run a container
        in a completely different thread.
    """
    def __init__(self, container):
        """

        :param container: The container to run in a different thread
        :type container: Container
        """
        super(ContainerThread, self).__init__(name="ContainerThread")
        self.stopped = False
        self.container = container

    def run(self):
        """Run the thread that holds values in a container and uses callbacks
        on updated values."""
        print "Running thread", self.name, "..."
        while not self.stopped:
            pass

        print "Stopped thread", self.name, "."

    def stop(self):
        """Stop the thread from running."""
        self.stopped = True
