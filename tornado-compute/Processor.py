from __future__ import absolute_import
from __future__ import print_function

# Here you can also import things like keras/tensorflow/theano, because this script is loaded only from the computation process!
import time, logging

class Processor(object):
    """Takes care of running computations."""
    def __init__(self, name):
        # prepare for computations. for example load keras models
        self.name = name
        return

    def uppercase(self, text):
        time.sleep(5) # blocking, long-running call
        return self.name + ": " + text.upper()


