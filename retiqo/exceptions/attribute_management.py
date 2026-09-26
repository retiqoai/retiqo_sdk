# Copyright 2026 Loreum Digital Inc
# SPDX-License-Identifier: Apache-2.0
"""Attribute management exceptions"""

from retiqo.exceptions.base import RTIException


class AttributeNotDefined(RTIException):
    """Attribute is not defined"""


class AttributeNotKnown(RTIException):
    """Attribute is not known"""


class AttributeNotOwned(RTIException):
    """Attribute is not owned"""


class AttributeNotPublished(RTIException):
    """Attribute is not published"""

