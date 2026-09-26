# Copyright 2026 Loreum Digital Inc
# SPDX-License-Identifier: Apache-2.0
"""
SuppliedAttributes - attribute values to send
"""
from typing import Dict, Optional
from retiqo.rti.attribute_handle_set import AttributeHandleSet


class SuppliedAttributes:
    """Supplied attribute values for updates"""

    def __init__(self):
        """Initialize empty supplied attributes"""
        self._values: Dict[int, bytes] = {}

    def add(self, attribute_handle: int, value: bytes) -> None:
        """Add an attribute value"""
        self._values[attribute_handle] = value

    def get(self, attribute_handle: int) -> Optional[bytes]:
        """Get an attribute value"""
        return self._values.get(attribute_handle)

    def get_handles(self) -> AttributeHandleSet:
        """Get all attribute handles"""
        from retiqo.rti.attribute_handle_set import AttributeHandleSetFactory

        return AttributeHandleSetFactory.create(list(self._values.keys()))

    def size(self) -> int:
        """Get the number of attributes"""
        return len(self._values)

    def __iter__(self):
        """Iterator over (handle, value) pairs"""
        return iter(self._values.items())

    def get_vector(self) -> list:
        """Get vector representation for serialization
        Format: [count, handle1, value1, handle2, value2, ...]
        """
        result = [len(self._values)]
        for handle, value in self._values.items():
            result.append(handle)
            result.append(value)
        return result


class SuppliedAttributesFactory:
    """Factory for creating SuppliedAttributes instances"""

    @staticmethod
    def create() -> SuppliedAttributes:
        """Create a new SuppliedAttributes"""
        return SuppliedAttributes()

