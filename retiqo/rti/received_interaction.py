# Copyright 2026 Loreum Digital Inc
# SPDX-License-Identifier: Apache-2.0
"""
ReceivedInteraction - interaction received from other actors
"""
from typing import Dict, Optional
from retiqo.rti.attribute_handle_set import AttributeHandleSet


class ReceivedInteraction:
    """Received interaction with parameters"""

    def __init__(self, interaction_class: int):
        """Initialize with interaction class handle"""
        self._interaction_class = interaction_class
        self._parameters: Dict[int, bytes] = {}

    def get_interaction_class(self) -> int:
        """Get the interaction class handle"""
        return self._interaction_class

    def add_parameter(self, parameter_handle: int, value: bytes) -> None:
        """Add a parameter value"""
        self._parameters[parameter_handle] = value

    def get_parameter(self, parameter_handle: int) -> Optional[bytes]:
        """Get a parameter value"""
        return self._parameters.get(parameter_handle)

    def get_parameter_handles(self) -> AttributeHandleSet:
        """Get all parameter handles"""
        from retiqo.rti.attribute_handle_set import AttributeHandleSetFactory

        return AttributeHandleSetFactory.create(list(self._parameters.keys()))

    def size(self) -> int:
        """Get the number of parameters"""
        return len(self._parameters)

    def __iter__(self):
        """Iterator over (handle, value) pairs"""
        return iter(self._parameters.items())

    def get_parameter_handle(self, index: int) -> int:
        """Get parameter handle at index"""
        handles = list(self._parameters.keys())
        if index < 0 or index >= len(handles):
            raise IndexError(f"Index {index} out of range")
        return handles[index]

    def get_value_reference(self, index: int) -> bytes:
        """Get value reference at index (not a copy)"""
        handles = list(self._parameters.keys())
        if index < 0 or index >= len(handles):
            raise IndexError(f"Index {index} out of range")
        return self._parameters[handles[index]]

    @classmethod
    def from_vector(cls, vector: list) -> "ReceivedInteraction":
        """
        Create from the wire vector format:
        [count, handle1, value1, handle2, value2, ..., orderType, transportType, region]
        
        The (handle, value) pairs come first, followed by: orderType = vector[i++], transportType = vector[i++], region = vector[i]
        """
        instance = cls(0)  # Interaction class will be set separately
        if vector and len(vector) > 0:
            count = vector[0] if isinstance(vector[0], int) else 0
            # Process parameter pairs: [1]=handle1, [2]=value1, [3]=handle2, [4]=value2, ...
            # Loop until we've processed all pairs (i goes from 1 to 2*count+1, stepping by 2)
            i = 1
            while i < 2 * count + 1 and i < len(vector):
                if i + 1 < len(vector):
                    handle = vector[i]
                    value = vector[i + 1]
                    # Convert handle to int if needed
                    if handle is not None:
                        handle = int(handle) if not isinstance(handle, int) else handle
                    # Convert value to bytes if needed
                    if value is not None:
                        value = bytes(value) if not isinstance(value, bytes) else value
                        instance.add_parameter(handle, value)
                i += 2
            # After pairs: orderType, transportType, region are at indices 2*count+1, 2*count+2, 2*count+3
            # We don't store these for now, but we could if needed
        return instance

