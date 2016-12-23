from __future__ import absolute_import
from __future__ import print_function

import os, sys
import tornado.web
import tornado.gen
import asyncio
import dualprocessing
import logging
logging.basicConfig(level=logging.DEBUG)

computationBroker = None

class Landing(tornado.web.RequestHandler):
    """Landing page of the webservice"""
    def get(self):
        self.render('templates/index.html', endpoints=endpoints)

class VGG(tornado.web.RequestHandler):
    """POST a URL of an image to this address to run it through VGG-16."""
    def get(self):
        self.render('templates/vgg.html')

    @tornado.gen.coroutine
    def post(self):
        try:
            url = self.get_argument("url", None)
            if (not url):   # take a default red panda image
                url = "https://farm6.staticflickr.com/5571/31110991010_489970cc12_z_d.jpg"
            call = dualprocessing.AsyncCall("predict", url=url)
            response = yield computationBroker.submit_call_async(call)
            if (response.Success):
                self.write(response.Result)
            else:
                raise response.Error
        except:
            def lastExceptionString():
                exc_type, ex, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                return "{0} in {1}:{2}".format(ex, fname, exc_tb.tb_lineno)
            exmsg = lastExceptionString()
            logging.critical(exmsg)
            self.write(exmsg)

endpoints = [
    (r"/", Landing),
    (r"/vgg", VGG)
]

def makePipeline():
    """Will be executed from the secondary process. Imports and constructs the computation environment."""
    import Pipeline
    processor = Pipeline.Pipeline("vgg16_weights.h5")
    return processor

if __name__ == '__main__':
    logging.info("Starting computation broker...")
    computationBroker = dualprocessing.Broker(makePipeline)

    logging.info("Starting service...")
    app = tornado.web.Application(endpoints)
    port = 2017
    app.listen(port)
    logging.info("Service is running publicly. at http://{0}:{1}/".format("[host-IP]", port))

    logging.warn("WARNING: Do not use multiple tabs in the same browser to test! The browser will delay sending of the second request until the first one returned! (Reference: http://www.tornadoweb.org/en/stable/faq.html)")
    
    tornado.ioloop.IOLoop.current().start()

    logging.info("Ended.")

    