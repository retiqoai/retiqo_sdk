# Copyright 2026 Loreum Digital Inc
# SPDX-License-Identifier: Apache-2.0
"""Object management exceptions"""

from retiqo.exceptions.base import RTIException


class ObjectNotKnown(RTIException):
    """Object is not known"""


class ObjectAlreadyRegistered(RTIException):
    """Object is already registered"""


class ObjectClassNotDefined(RTIException):
    """Object class is not defined"""


class ObjectClassNotKnown(RTIException):
    """Object class is not known"""


class ObjectClassNotPublished(RTIException):
    """Object class is not published"""


class ObjectClassNotSubscribed(RTIException):
    """Object class is not subscribed"""

