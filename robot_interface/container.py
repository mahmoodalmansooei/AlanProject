__author__ = 'Petrut Bogdan'
import threading
import thread


class Container(object):
    def __init__(self, default_callback=None):
        """
        Container is an object that keeps track of different keys and
        potentially triggers a callback when the value is changed.

        Designed to be run in a ContainerThread.
        :param default_callback: a default callback for all the elements in the
        container
        :type default_callback: callable
        :return: a container object
        :rtype: Container
        """
        self.default_callback = default_callback
        if default_callback:
            assert callable(default_callback)

        self.dictionary = dict()

    def add(self, key, value):
        self.dictionary[key] = value

    def update(self, key, value, callback=None):
        callback = callback if callback else self.default_callback
        self.dictionary[key] = value
        if callback:
            thread.start_new_thread(callback, (key, value))


class ContainerThread(threading.Thread):
    def __init__(self, container):
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
