# Copyright 2026 Loreum Digital Inc
# SPDX-License-Identifier: Apache-2.0
"""Consensus-related exceptions"""

from retiqo.exceptions.base import RTIException


class ConsensusLabelNotAnnounced(RTIException):
    """Consensus label was not announced"""


class ConsensusLabelOutstanding(RTIException):
    """Consensus label is outstanding"""


class ConsensusPointLabelWasNotAnnounced(RTIException):
    """Consensus point label was not announced"""

