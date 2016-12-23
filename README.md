# Summary
Sample application for building a tornado-powered webservice that runs blocking calls sequentially on a second process. Handlers of the webservice remain asynchronous, therefore many requests can be accepted in parallel.

# Requirements
Scheduling and interaction between the first (frontend) and second (computation backend) process is done with the [`dualprocessing` module](https://github.com/michaelosthege/dualprocessing).

```bash
pip install dualprocessing
```

# Scenario
+ you want to accepts many requests in parallel
+ backend calls are slow (fine for the client, but unacceptable for the server)
+ backend calls are blocking
+ backend calls return picklable values
+ backend calls are first-in-first-out
+ there exists only one instance of the backend thing that is called
+ all calls must happen on the same thread/process
+ thing import and instance creation is slow (common for deep learning frameworks)

# Solution
Before the service is started, a Broker is created. It will run a user-provided constructor on a new thread to create one instance of the Processor (thing).

It uses a pipe to wait for incoming calls.
Each call is indentified by a unique key. When a it comes in, it is passed through the pipe to the backend computation process. The loop at the other end of the pipe sequentially does the (blocking) calls, while the main thread asynchronously waits for the response to be returned through the pipe.

**Processor.py**: user-provided class that will live on the second process

**Service.py**: runs the webserver and remains responsive at all times

**Broker**: handles process creation and asynchronous scheduling/execution

# ToDo
+ implement handling of really long-running jobs (where the client must ask for the result) like described here: http://farazdagi.com/blog/2014/rest-long-running-jobs/