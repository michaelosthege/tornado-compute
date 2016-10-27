from __future__ import absolute_import
from __future__ import print_function

# Here you can also import things like keras/tensorflow/theano, because this script is loaded only from the computation process!
import time, logging

class Processor(object):
    """Takes care of running computations."""
    def __init__(self):
        # prepare for computations. for example load keras models
        return

    def process(self, key):
        time.sleep(5) # blocking, long-running call
        return "result of {0}".format(key)


