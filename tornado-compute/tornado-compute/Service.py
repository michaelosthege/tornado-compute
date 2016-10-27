from __future__ import absolute_import
from __future__ import print_function

import tornado.web
import tornado.gen
import asyncio
import broker
import logging
logging.basicConfig(level=logging.DEBUG)

computationBroker = None


class Computor(tornado.web.RequestHandler):
    """Computor API"""
    @tornado.gen.coroutine
    def get(self):
        call = broker.AsyncCall("uppercase", text="blabla")
        response = yield computationBroker.processAsync(call)     # asynchronously waits until the second process finishes computation
        self.write("success: {0}</br>result: {1}".format(response.Success, response.Result))


endpoints = {
    r"/": Computor
}

def makeProcessor():
    """Will be executed from the secondary process. Imports and constructs the computation environment."""
    import Processor
    processor = Processor.Processor()
    return processor

if __name__ == '__main__':
    print("Starting computation broker...")
    computationBroker = broker.ComputationBroker(makeProcessor)

    print("Starting service...")
    app = tornado.web.Application([(route, cls) for route,cls in endpoints.items()])
    port = 2017
    app.listen(port)
    print("Service is running publicly. at http://{0}:{1}/".format("[host-IP]", port))

    print("WARNING: Do not use multiple tabs in the same browser to test! The browser will delay sending of the second request until the first one returned!")
    print("Reference: http://www.tornadoweb.org/en/stable/faq.html")
        
    tornado.ioloop.IOLoop.current().start()

    print("Ended.")