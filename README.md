## Primitive profiler

The purpose of this script is to detect the requirements for D3M primitives, in order to construct machine learning pipelines appropriately.

How to run the script:

* Pull an image with the D3M primitives installed:

`docker pull registry.datadrivendiscovery.org/jpl/docker_images/complete:ubuntu-xenial-python36-v2018.1.5`

* Run the image mounting a volume and copy the script on it

`docker run -it -v "path_to_volume":/home registry.datadrivendiscovery.org/jpl/docker_images/complete:ubuntu-xenial-python36-v2018.1.5

* Run the script (after accessing the "home" folder)

`python3.6 profiler.py`

A json text with the requirements will appear in your console.

Contributors:
Chin Wang Cheong, Daniel Garijo