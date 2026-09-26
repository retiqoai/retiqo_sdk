# Copyright 2026 Loreum Digital Inc
# SPDX-License-Identifier: Apache-2.0
"""
AttributeHandleSet - collection of attribute handles
"""
from typing import List, Set, Iterator, Optional


class AttributeHandleSet:
    """Set of attribute handles"""

    def __init__(self, handles: Optional[List[int]] = None):
        """Initialize with optional list of handles"""
        self._handles: Set[int] = set(handles) if handles else set()

    def add(self, handle: int) -> None:
        """Add an attribute handle"""
        self._handles.add(handle)

    def remove(self, handle: int) -> None:
        """Remove an attribute handle"""
        self._handles.discard(handle)

    def is_member(self, handle: int) -> bool:
        """Check if handle is a member"""
        return handle in self._handles

    def size(self) -> int:
        """Get the size of the set"""
        return len(self._handles)

    def empty(self) -> None:
        """Empty the set"""
        self._handles.clear()

    def handles(self) -> Iterator[int]:
        """Get iterator over handles"""
        return iter(self._handles)

    def to_list(self) -> List[int]:
        """Convert to list"""
        return list(self._handles)

    def __iter__(self) -> Iterator[int]:
        """Iterator support"""
        return iter(self._handles)

    def __len__(self) -> int:
        """Length support"""
        return len(self._handles)

    def __contains__(self, handle: int) -> bool:
        """Contains support"""
        return handle in self._handles


class AttributeHandleSetFactory:
    """Factory for creating AttributeHandleSet instances"""

    @staticmethod
    def create(handles: Optional[List[int]] = None) -> AttributeHandleSet:
        """Create a new AttributeHandleSet"""
        return AttributeHandleSet(handles)

