# Copyright 2026 Loreum Digital Inc
# SPDX-License-Identifier: Apache-2.0
"""Save/Restore exceptions"""

from retiqo.exceptions.base import RTIException


class SaveInProgress(RTIException):
    """Save operation is in progress"""


class RestoreInProgress(RTIException):
    """Restore operation is in progress"""


class SaveNotInitiated(RTIException):
    """Save was not initiated"""


class RestoreNotRequested(RTIException):
    """Restore was not requested"""


class SpecifiedSaveLabelDoesNotExist(RTIException):
    """Specified save label does not exist"""


class CouldNotRestore(RTIException):
    """Could not restore"""


class UnableToPerformSave(RTIException):
    """Unable to perform save"""

