# Copyright 2026 Loreum Digital Inc
# SPDX-License-Identifier: Apache-2.0
"""Interaction-related exceptions"""

from retiqo.exceptions.base import RTIException


class InteractionClassNotDefined(RTIException):
    """Interaction class is not defined"""


class InteractionClassNotKnown(RTIException):
    """Interaction class is not known"""


class InteractionClassNotPublished(RTIException):
    """Interaction class is not published"""


class InteractionClassNotSubscribed(RTIException):
    """Interaction class is not subscribed"""


class InteractionParameterNotDefined(RTIException):
    """Interaction parameter is not defined"""


class InteractionParameterNotKnown(RTIException):
    """Interaction parameter is not known"""

