from __future__ import absolute_import
from __future__ import print_function

import tornado.web
import tornado.gen
import asyncio
import ComputationBroker
import uuid
import logging
logging.basicConfig(level=logging.DEBUG)

broker = None


class Computor(tornado.web.RequestHandler):
    """Computor API"""
    @tornado.gen.coroutine
    def get(self):
        key = str(uuid.uuid4())                     # unique key that identified the computation task
        logging.info("{0} accepted".format(key))
        result = yield broker.processAsync(key)     # asynchronously waits until the second process finishes computation
        self.write(result)


endpoints = {
    r"/": Computor
}


if __name__ == '__main__':
    print("Starting computation broker...")
    broker = ComputationBroker.ComputationBroker()

    print("Starting service...")
    app = tornado.web.Application([(route, cls) for route,cls in endpoints.items()])
    port = 2017
    app.listen(port)
    print("Service is running publicly. at http://{0}:{1}/".format("[host-IP]", port))

    print("WARNING: Do not use multiple tabs in the same browser to test! The browser will delay sending of the second request until the first one returned!")
    print("Reference: http://www.tornadoweb.org/en/stable/faq.html")
        
    tornado.ioloop.IOLoop.current().start()

    print("Ended.")