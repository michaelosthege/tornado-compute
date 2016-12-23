from __future__ import absolute_import
from __future__ import print_function

# Here you can also import things like keras/tensorflow/theano, because this script is loaded only from the computation process!
import time, logging
import keras, numpy
import urllib.request
import os, sys
import keras_vgg_buddy as buddy

class Pipeline(object):
    """Takes care of running computations."""
    def __init__(self, weights_path="vgg16.hdf5", download_from="https://docs.google.com/uc?id=0Bz7KyqmuGsilT0J5dmRCM0ROVHc&export=download"):
        """Prepare computation pipeline by loading the keras model

        Parameters
        ----------
        weights_path : str
            filename or path to the trained keras model of VGG-16
            
        download_from : str
            fallback-url to download the VGG-16 weights
        """
        # 
        self.VGG = self.get_vgg(weights_path, download_from)
        return

    def get_vgg(self, weights_path, download_from):
        # make sure that we have the weights file
        if (not os.path.exists(weights_path)):
            logging.info("No VGG-16 weights found at {0}".format(weights_path))
            logging.info("Downloading VGG-16 from {0}".format(download_from))
            urllib.request.urlretrieve(download_from, weights_path)
            logging.info("Download of VGG-16 complete")
        # load the model
        vgg = buddy.get_model(224, 224, weights_path)
        vgg.compile(optimizer='adam', loss='mse')
        return vgg

    def predict(self, url):
        ############## Prepare input
        # download the image
        filename = "temp" + os.path.splitext(url)[1]
        urllib.request.urlretrieve(url, filename)
        # load the image
        input = buddy.load_and_preprocess_image(filename, 224, True)
        ############## Predict
        input_batch = numpy.array([input])
        prediction = self.VGG.predict(input_batch)[0]
        ############## Return the ImageNet class label
        predicted_class = numpy.argmax(prediction)
        return buddy.IMAGENET_CLASSES[predicted_class]


