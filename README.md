# Introduction
Sample application for building a [**`tornado`**](http://www.tornadoweb.org/)-powered webservice that feeds input to a [**`Keras`**](http://keras.io) model on a second process. Handlers of the webservice remain asynchronous, therefore it stays responsive.

## What this is
A primer to show you how to serve any *Keras* model as a webservice. Here we take VGG-16, but any other model works fine too.

This will show you how to deploy your neural network to a webservice **without writing a single line of C++**. Here are a few reasons why you'd **not** want to do that with C++:
+ cross-platform compatibility
+ combination with `skimage`, `sklearn` or any other Python modules
+ develop and deploy with the same language

## What this is NOT
This is not something that magically knows and does what you want. You managed to build a neural network, but to serve it in a webservice, you are expected to write a few more lines of Python.

You are in charge of the API endpoints, feeding inputs to your model and serving responses. This application will merely show you the architecture by example.



# How to get going
## What you bring to the party
This tutorial assumes that you...
+ already have a Python environment running *Keras* (preferably on GPU)
+ you want to keep using Python for deployment

Now there are some things you probably don't have installed yet. But don't worry, you can install them via `pip`:

Fortunately you can install these via `pip`:

```bash
pip install tornado
pip install dualprocessing
pip install keras_vgg_buddy
```

Why do we need these?
+ [**`tornado`**](http://www.tornadoweb.org/) is a webserver that we'll use to create the webservice. It's highly scalable and built for performance.
+ [**`dualprocessing`**](https://github.com/michaelosthege/dualprocessing) is a module I built for running a thread-blocking computation pipeline on a second process.
+ [**`keras_vgg_buddy`**](https://github.com/awentzonline/keras-vgg-buddy) is there to help with loading VGG from the weights file and converting class index to class label

Finally, **you need to provide a trained VGG-16 model** as a HDF5-file. You can download it from [here](https://drive.google.com/file/d/0Bz7KyqmuGsilT0J5dmRCM0ROVHc/view).

If you know a URL where this file can be downloaded directly, you can provide it as a parameter.



## How does it work?
Before the service is started, a `dualprocessing.Broker` is created. It will run a user-provided constructor (`makePipeline`) on a new thread to create one instance of the computation `Pipeline`.

The `Broker` uses a pipe connection to schedule calls to the computation pipeline. Each call is identified by a unique key. When a it comes in, it is passed through the pipe to the backend computation process. A loop at the other end of the pipe sequentially does the (blocking) prediction calls, while the main thread asynchronously waits for the response to be returned through the pipe.

**Pipeline.py**: user-provided class that will live on the second process

**StartService.py**: runs the webserver and remains responsive at all times

**Broker**: handles process creation and asynchronous scheduling/execution

If you're interested in the details of the [**`dualprocessing`**](https://github.com/michaelosthege/dualprocessing) module, have a look at its GitHub page.

## How do I run it?
After you have completed this checklist, just run `StartService.py` as shown below.

* [ ] installed all dependencies
* [ ] [`vgg16_weights.h5`](https://drive.google.com/file/d/0Bz7KyqmuGsilT0J5dmRCM0ROVHc/view) downloaded to project directory

```bash
python StartService.py
```

Now you can point your browser to [http://localhost:2017/vgg](http://localhost:2017/vgg). 

Alternatively you can POST a URL pointing to an image to http://localhost:2017/vgg

The first time you do this, the VGG model will be compiled to work with CUDA, so expect some delay. Subsequent requests will process within sub-second delays.

