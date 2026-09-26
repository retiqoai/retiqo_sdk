# Copyright 2026 Loreum Digital Inc
# SPDX-License-Identifier: Apache-2.0
"""Region-related exceptions"""

from retiqo.exceptions.base import RTIException


class RegionNotKnown(RTIException):
    """Region is not known"""


class RegionInUse(RTIException):
    """Region is in use"""


class InvalidRegionContext(RTIException):
    """Invalid region context"""


class InvalidExtents(RTIException):
    """Invalid extents"""


class DimensionNotDefined(RTIException):
    """Dimension is not defined"""


class SpaceNotDefined(RTIException):
    """Space is not defined"""

