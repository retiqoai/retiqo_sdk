# Copyright 2026 Loreum Digital Inc
# SPDX-License-Identifier: Apache-2.0
"""
SuppliedParameters - interaction parameters to send
"""
from typing import Dict, Optional
from retiqo.rti.attribute_handle_set import AttributeHandleSet


class SuppliedParameters:
    """Supplied parameters for interactions"""

    def __init__(self):
        """Initialize empty supplied parameters"""
        self._values: Dict[int, bytes] = {}

    def add(self, parameter_handle: int, value: bytes) -> None:
        """Add a parameter value"""
        self._values[parameter_handle] = value

    def get(self, parameter_handle: int) -> Optional[bytes]:
        """Get a parameter value"""
        return self._values.get(parameter_handle)

    def get_handles(self) -> AttributeHandleSet:
        """Get all parameter handles"""
        from retiqo.rti.attribute_handle_set import AttributeHandleSetFactory

        return AttributeHandleSetFactory.create(list(self._values.keys()))

    def size(self) -> int:
        """Get the number of parameters"""
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


class SuppliedParametersFactory:
    """Factory for creating SuppliedParameters instances"""

    @staticmethod
    def create() -> SuppliedParameters:
        """Create a new SuppliedParameters"""
        return SuppliedParameters()

