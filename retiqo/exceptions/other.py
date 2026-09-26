# Copyright 2026 Loreum Digital Inc
# SPDX-License-Identifier: Apache-2.0
"""Other RTI exceptions"""

from retiqo.exceptions.base import RTIException


class InvalidResignAction(RTIException):
    """Invalid resign action"""


class InvalidStateChannelTime(RTIException):
    """Invalid state channel time"""


class NameNotFound(RTIException):
    """Name not found"""


class EventNotKnown(RTIException):
    """Event is not known"""


class CouldNotDiscover(RTIException):
    """Could not discover"""


class CouldNotDecode(RTIException):
    """Could not decode"""


class DeleteRightNotHeld(RTIException):
    """Delete right is not held"""


class TooManyActors(RTIException):
    """Too many actors"""


class UnimplementedService(RTIException):
    """Service is not implemented"""


class AsynchronousDeliveryAlreadyEnabled(RTIException):
    """Asynchronous delivery is already enabled"""


class AsynchronousDeliveryAlreadyDisabled(RTIException):
    """Asynchronous delivery is already disabled"""

