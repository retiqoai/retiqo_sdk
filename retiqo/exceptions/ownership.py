# Copyright 2026 Loreum Digital Inc
# SPDX-License-Identifier: Apache-2.0
"""Ownership-related exceptions"""

from retiqo.exceptions.base import RTIException


class OwnershipAcquisitionPending(RTIException):
    """Ownership acquisition is pending"""


class AttributeAlreadyOwned(RTIException):
    """Attribute is already owned"""


class AttributeAlreadyBeingAcquired(RTIException):
    """Attribute is already being acquired"""


class AttributeAlreadyBeingDivested(RTIException):
    """Attribute is already being divested"""


class AttributeAcquisitionWasNotRequested(RTIException):
    """Attribute acquisition was not requested"""


class AttributeAcquisitionWasNotCanceled(RTIException):
    """Attribute acquisition was not canceled"""


class AttributeDivestitureWasNotRequested(RTIException):
    """Attribute divestiture was not requested"""


class ActorWasNotAskedToReleaseAttribute(RTIException):
    """Actor was not asked to release attribute"""

