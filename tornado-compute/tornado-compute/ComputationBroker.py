from __future__ import absolute_import
from __future__ import print_function

import multiprocessing, asyncio, logging, concurrent.futures, time

def start(pipeEnd:multiprocessing.connection.PipeConnection):
    """Imports computation script and sequentially (blockingly) runs computations that arrive through the pipe.

    Sends computation results back through the pipe.

    This method should be called from the spawned secondary process.
    """
    logging.info("Broker: process started")
    # import processing library from this subprocess only
    import Processor
    processor = Processor.Processor()
    logging.info("Broker: processor initialized")
    # endlessly loop
    while True:
        # get input key
        key, = pipeEnd.recv()
        if (key is not None):
            # process input synchronously
            logging.info("{0} processing".format(key))
            result = processor.process(key)
            pipeEnd.send((key,result))
        # continue looping
    # will never return
    return


class ComputationBroker(object):
    """Handles scheduling and running of computations on a second process."""

    def __init__(self):
        self._FinishedTasks = {}
        childEnd, self.ParentEnd = multiprocessing.connection.Pipe()
        self._ComputationProcess = multiprocessing.Process(target=start, args=(childEnd,), name="ComputationProcess")
        self._ComputationProcess.start()
        self.executor = concurrent.futures.ThreadPoolExecutor(256)
        return

    def processAsync(self, key):
        """(asynchronous) Uses a new thread to schedule a computation and wait for its result. Completion of the thread is awaited asynchronously."""
        return self.executor.submit(self.processSynchronous, key)
        
    
    def processSynchronous(self, key):
        """(blocking) Schedules a computation and checks for a result every 5 ms."""
        logging.info("{0} scheduled".format(key))
        # add the key to the queue
        self.ParentEnd.send((key,))
        # wait for the completion by the subprocess
        while key not in self._FinishedTasks:
            time.sleep(0.005)
            # receive all computations that have finished
            while self.ParentEnd.poll():
                key, result = self.ParentEnd.recv()
                self._FinishedTasks[key] = result
        result = self._FinishedTasks.pop(key)
        logging.info("{0} complete".format(key))
        return result

    

    