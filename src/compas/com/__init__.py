"""
********************************************************************************
compas.com
********************************************************************************

.. module:: compas.com

:mod:`compas.com` provides functionality for communicating with external software.


Matlab
======

.. autosummary::
    :toctree: generated/
    :nosignatures:

    MatlabClient
    MatlabEngine
    MatlabProcess
    MatlabSession

Rhino
=====

.. autosummary::
    :toctree: generated/
    :nosignatures:

    RhinoClient

ssh
===

.. autosummary::
    :toctree: generated/
    :nosignatures:

    SSH

"""


class Process(object):
    pass


class Client(object):
    pass


from .matlab_ import *
from .ssh import *
from .rhino import *

from .matlab_ import __all__ as a
from .ssh import __all__ as b
from .rhino import __all__ as c

__all__ = a + b + c
