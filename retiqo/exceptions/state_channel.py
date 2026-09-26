# Copyright 2026 Loreum Digital Inc
# SPDX-License-Identifier: Apache-2.0
"""State Channel exceptions"""

from retiqo.exceptions.base import RTIException


class StateChannelExecutionDoesNotExist(RTIException):
    """State channel execution does not exist"""


class StateChannelExecutionAlreadyExists(RTIException):
    """State channel execution already exists"""


class ActorsCurrentlyJoined(RTIException):
    """Actors are currently joined to the state channel"""


class CouldNotOpenSCD(RTIException):
    """Could not open State Channel Definition file"""


class ErrorReadingSCD(RTIException):
    """Error reading State Channel Definition file"""

