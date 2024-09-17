# Overview

This repository contains sample Lumeo Custom Functions, to be used in Lumeo's [custom function node](https://docs.lumeo.com/docs/custom-function-node).

# How to use

1. Using the `Utils.install_import` method in a Lumeo custom function node.

You can install this package in a Lumeo custom function node, and call it's functions using the following code snippet:

> Important: The version number must match the version number in the `setup.py` file. When you make changes to the package, 
> you must also update the package version and specify it in the `Utils.install_import` method, even if you specify a git 
> branch or tag in the `git_url` parameter.
> This is required since Lumeo will not re-download the package if the specified version already exists in the container.

```python
from lumeopipeline import VideoFrame, Utils

Utils.install_import('custom_functions', version='0.1.1', git_url='https://github.com/lumeohq/custom-functions.git')
from custom_functions import display

def process_frame(frame: VideoFrame, **kwargs):
    return display.process_frame(frame, **kwargs)
```


```python
from lumeopipeline import VideoFrame, Utils

Utils.install_import('custom_functions', version='0.1.1', git_url='https://github.com/lumeohq/custom-functions.git')
from custom_functions import watermark

def process_frame(frame: VideoFrame, **kwargs):
    return watermark.process_frame(frame, **kwargs)
```

2. Using the `Custom Function Repo` node in Lumeo.



# Build your own custom functions

You can build your own custom functions and use them in one of two ways:

1. Put the entire custom function code into the [Custom Function Node](https://docs.lumeo.com/docs/custom-function-node) in Lumeo.

2. Host the custom function code in a github repository and use the `Utils.install_import` method or `Custom Function Repo` node to import and use the custom function.

While the first approach is easier to setup and iterate on while developing, the second approach allows you to version control your custom functions and reuse them across multiple pipelines.

## Setting up a Custom Function Repo

Install `lumeo` python package:
```
pip install lumeo
```
or 
```
pipx install lumeo
```

Navigate to the directory you want to create your custom function repo in, and run the following command:
```
lumeo-custom-function-create-repo <package_name>
```

This will create a new directory with the name you provided, with a basic structure for a custom function repo. You can then add your custom functions to the repo and publish to a git repository.
