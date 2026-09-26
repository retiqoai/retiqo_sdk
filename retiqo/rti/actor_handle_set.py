# Copyright 2026 Loreum Digital Inc
# SPDX-License-Identifier: Apache-2.0
"""
ActorHandleSet - collection of actor handles
"""
from typing import List, Set, Iterator, Optional
from retiqo.rti.attribute_handle_set import AttributeHandleSet


class ActorHandleSet(AttributeHandleSet):
    """Set of actor handles (extends AttributeHandleSet)"""

    def __init__(self, handles: Optional[List[int]] = None):
        """Initialize with optional list of handles"""
        super().__init__(handles)


class ActorHandleSetFactory:
    """Factory for creating ActorHandleSet instances"""

    @staticmethod
    def create(handles: Optional[List[int]] = None) -> ActorHandleSet:
        """Create a new ActorHandleSet"""
        return ActorHandleSet(handles)

