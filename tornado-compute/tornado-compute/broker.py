from __future__ import absolute_import
from __future__ import print_function

import multiprocessing, asyncio, logging, concurrent.futures, time, uuid, sys, typing

class AsyncCall(object):
    def __init__(self, targetMethod:str, *args, **kwargs):
        self.TargetMethod = targetMethod
        self.Key = str(uuid.uuid4())
        self.Kwargs = kwargs
        return

class AsyncResponse(object):
    def __init__(self, key:str, success:bool, result:object):
        self.Key = key
        self.Success = success
        self.Result = result
        return


class ComputationBroker(object):
    """Handles scheduling and running of computations on a second process."""

    def __init__(self, processorConstructor):
        """Starts a second thread for calling methods on the instance created through processorConstructor."""
        self.FinishedTasks = {}
        childEnd, self.__ParentEnd__ = multiprocessing.connection.Pipe()
        self.__ComputationProcess__ = multiprocessing.Process(target=self.__start__, args=(childEnd,processorConstructor), name="ComputationProcess")
        self.__ComputationProcess__.start()
        self.ThreadExecuter = concurrent.futures.ThreadPoolExecutor(256)
        self.ThreadExecuter.submit(self.__receive__)
        return

    @classmethod
    def __start__(self, pipeEnd:multiprocessing.connection.PipeConnection, processorConstructor:typing.Callable):
        """Instantiates processorConstructor and executes calls on the instance of the processor.

        Called from the second process and listens for incoming calls through the pipe.

        Sends return values of executed calls back through the pipe.
        """
        logging.info("Broker: process started")
        # we're now on the second process, so we can create the processor
        processor = processorConstructor()
        logging.info("Broker: processor initialized")
        # endlessly loop
        while True:
            # get input key
            call, = pipeEnd.recv()
            # process input synchronously
            logging.info("{0} processing".format(call.Key))
            # execute the said method on the processor
            response = AsyncResponse(call.Key, False, None)
            try:
                returned = processor.__getattribute__(call.TargetMethod)(**call.Kwargs)
                response.Result = returned
                response.Success = True
            except:
                response.Success = False
                response.Result = sys.exc_info()[1]
            pipeEnd.send((response,))
            # continue looping
        # will never return
        return

    def processAsync(self, call:AsyncCall):
        """(asynchronous) Uses a new thread to schedule a call and wait for its return value. Completion of the thread is awaited asynchronously.
        
        Example:

        @asyncio.coroutine
        def myfunc():
            call = broker.AsyncCall("uppercase", text="blabla")
            asyncResponse = yield compuBroker.processAsync(call)
            print(asyncResponse.Sucess)
            print(asyncResponse.Result)
            
        """
        return self.ThreadExecuter.submit(self.processSynchronous, call)
        
    def __receive__(self):
        """Continuously listen for tasks being completed."""
        while (True):
            time.sleep(0.005)
            # receive all computations that have finished
            while self.__ParentEnd__.poll():
                response, = self.__ParentEnd__.recv()
                self.FinishedTasks[response.Key] = response
        return
    
    def processSynchronous(self, call:AsyncCall):
        """(blocking) Schedules a call and checks for a result every 50 ms."""
        logging.info("{0} scheduled".format(call.Key))
        # add the key to the queue
        self.__ParentEnd__.send((call,))
        # wait for the completion by the subprocess
        while call.Key not in self.FinishedTasks:
            time.sleep(0.05)
        result = self.FinishedTasks.pop(call.Key)
        logging.info("{0} complete".format(call.Key))
        return result

    

    