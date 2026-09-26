# Copyright 2026 Loreum Digital Inc
# SPDX-License-Identifier: Apache-2.0
"""
ReflectedAttributes - attribute values received from other actors
"""
from typing import Dict, Optional
from retiqo.rti.attribute_handle_set import AttributeHandleSet


class ReflectedAttributes:
    """Reflected attribute values"""

    def __init__(self):
        """Initialize empty reflected attributes"""
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

    def get_attribute_handle(self, index: int) -> int:
        """Get attribute handle at index"""
        handles = list(self._values.keys())
        if index < 0 or index >= len(handles):
            raise IndexError(f"Index {index} out of range")
        return handles[index]

    def get_value_reference(self, index: int) -> bytes:
        """Get value reference at index (not a copy)"""
        handles = list(self._values.keys())
        if index < 0 or index >= len(handles):
            raise IndexError(f"Index {index} out of range")
        return self._values[handles[index]]

    @classmethod
    def from_vector(cls, vector: list) -> "ReflectedAttributes":
        """Create from vector format [count, handle1, value1, region1, handle2, value2, region2, ...]
        
        Each attribute occupies three consecutive slots after the count:
            handle = vector[i + 1]
            value = vector[i + 2]
            region = vector[i + 3]  (region is currently ignored)
        """
        instance = cls()
        if vector and len(vector) > 0:
            count = vector[0] if isinstance(vector[0], int) else 0
            # Step through the (handle, value, region) triples
            for i in range(0, 3 * count, 3):
                handle_idx = i + 1
                value_idx = i + 2
                # region_idx = i + 3 (we ignore region for now)
                
                if handle_idx < len(vector) and value_idx < len(vector):
                    handle = vector[handle_idx]
                    value = vector[value_idx]
                    
                    # Ensure handle is an int
                    if not isinstance(handle, int):
                        handle = int(handle) if handle else 0
                    
                    # Ensure value is bytes
                    if not isinstance(value, bytes):
                        if isinstance(value, list):
                            # Convert list of ints to bytes
                            value = bytes(value)
                        elif value:
                            value = bytes(value) if isinstance(value, (bytes, bytearray)) else str(value).encode('utf-8')
                        else:
                            value = b""
                    
                    instance.add(handle, value)
        return instance

