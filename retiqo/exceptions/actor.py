# Copyright 2026 Loreum Digital Inc
# SPDX-License-Identifier: Apache-2.0
"""Actor-related exceptions"""

from retiqo.exceptions.base import RTIException


class ActorNotExecutionMember(RTIException):
    """Actor is not a member of the execution"""


class ActorAlreadyExecutionMember(RTIException):
    """Actor is already a member of the execution"""


class ActorOwnsAttributes(RTIException):
    """Actor owns attributes and cannot perform the requested operation"""


class ActorInternalError(RTIException):
    """Internal actor error"""

