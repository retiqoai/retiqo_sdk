# Copyright 2026 Loreum Digital Inc
# SPDX-License-Identifier: Apache-2.0
"""
Region implementation - represents a region in routing space
"""
from typing import List, Optional, Any
from retiqo.exceptions import ArrayIndexOutOfBounds
from retiqo.streams.base import Base, BaseConstants


class Extent:
    """Represents a single extent within a region"""

    def __init__(self, number_of_dimensions: int = None, byte_array: bytes = None):
        """Initialize extent with number of dimensions or from byte array"""
        if byte_array is not None:
            # Deserialize from byte array
            self._deserialize_from_byte_array(byte_array)
        elif number_of_dimensions is not None:
            # Initialize with number of dimensions
            self._number_of_dimensions = number_of_dimensions
            self._lower_bounds = [0] * number_of_dimensions
            self._upper_bounds = [0] * number_of_dimensions
            self._lower_bounds_committed = [0] * number_of_dimensions
            self._upper_bounds_committed = [0] * number_of_dimensions

            # Initialize to full range
            for j in range(number_of_dimensions):
                self._lower_bounds_committed[j] = -(2**63)  # minimum int64 sentinel
                self._upper_bounds_committed[j] = 2**63 - 1  # Long.MAX_VALUE
                self._lower_bounds[j] = -(2**63)
                self._upper_bounds[j] = 2**63 - 1
        else:
            raise ValueError("Either number_of_dimensions or byte_array must be provided")
    
    def _deserialize_from_byte_array(self, byte_array: bytes) -> None:
        """Deserialize extent from byte array"""
        from retiqo.streams.base import Base, BaseConstants
        
        if len(byte_array) < BaseConstants.SIZEOF_INT * 4:
            raise ValueError(f"Byte array too short: {len(byte_array)} < {BaseConstants.SIZEOF_INT * 4}")
        
        pos = 0
        
        # Read lowerBounds: int (length) + longs (values)
        len_lower = Base.extract_int(byte_array, pos)
        pos += BaseConstants.SIZEOF_INT
        if len_lower < 0 or len_lower > 1000:
            raise ValueError(f"Invalid lowerBounds length: {len_lower}")
        
        self._lower_bounds = []
        for i in range(len_lower):
            self._lower_bounds.append(Base.extract_long(byte_array, pos))
            pos += BaseConstants.SIZEOF_LONG
        
        # Read upperBounds: int (length) + longs (values)
        len_upper = Base.extract_int(byte_array, pos)
        pos += BaseConstants.SIZEOF_INT
        if len_upper < 0 or len_upper > 1000 or len_upper != len_lower:
            raise ValueError(f"Invalid upperBounds length: {len_upper} (expected {len_lower})")
        
        self._upper_bounds = []
        for i in range(len_upper):
            self._upper_bounds.append(Base.extract_long(byte_array, pos))
            pos += BaseConstants.SIZEOF_LONG
        
        # Read lowerBoundsCommited: int (length) + longs (values)
        len_lower_committed = Base.extract_int(byte_array, pos)
        pos += BaseConstants.SIZEOF_INT
        if len_lower_committed < 0 or len_lower_committed > 1000 or len_lower_committed != len_lower:
            raise ValueError(f"Invalid lowerBoundsCommited length: {len_lower_committed} (expected {len_lower})")
        
        self._lower_bounds_committed = []
        for i in range(len_lower_committed):
            self._lower_bounds_committed.append(Base.extract_long(byte_array, pos))
            pos += BaseConstants.SIZEOF_LONG
        
        # Read upperBoundsCommited: int (length) + longs (values)
        len_upper_committed = Base.extract_int(byte_array, pos)
        pos += BaseConstants.SIZEOF_INT
        if len_upper_committed < 0 or len_upper_committed > 1000 or len_upper_committed != len_lower:
            raise ValueError(f"Invalid upperBoundsCommited length: {len_upper_committed} (expected {len_lower})")
        
        self._upper_bounds_committed = []
        for i in range(len_upper_committed):
            self._upper_bounds_committed.append(Base.extract_long(byte_array, pos))
            pos += BaseConstants.SIZEOF_LONG
        
        self._number_of_dimensions = len_lower

    def get_lower_bound(self, dimension: int) -> int:
        """Get lower bound for dimension (returns the committed bound)"""
        if dimension < 0 or dimension >= self._number_of_dimensions:
            raise ArrayIndexOutOfBounds(
                f"Dimension {dimension} out of bounds (0-{self._number_of_dimensions - 1})"
            )
        # Ensure committed bounds array is initialized
        if self._lower_bounds_committed is None or len(self._lower_bounds_committed) != len(self._lower_bounds):
            # Initialize committed bounds from uncommitted bounds
            self._lower_bounds_committed = list(self._lower_bounds)
            self._upper_bounds_committed = list(self._upper_bounds)
        # Return the committed bound
        return self._lower_bounds_committed[dimension]

    def get_upper_bound(self, dimension: int) -> int:
        """Get upper bound for dimension (returns the committed bound)"""
        if dimension < 0 or dimension >= self._number_of_dimensions:
            raise ArrayIndexOutOfBounds(
                f"Dimension {dimension} out of bounds (0-{self._number_of_dimensions - 1})"
            )
        # Ensure committed bounds array is initialized
        if self._upper_bounds_committed is None or len(self._upper_bounds_committed) != len(self._upper_bounds):
            # Initialize committed bounds from uncommitted bounds
            self._lower_bounds_committed = list(self._lower_bounds)
            self._upper_bounds_committed = list(self._upper_bounds)
        # Return the committed bound
        return self._upper_bounds_committed[dimension]

    def set_lower_bound(self, dimension: int, value: int) -> None:
        """Set lower bound for dimension"""
        if dimension < 0 or dimension >= self._number_of_dimensions:
            raise ArrayIndexOutOfBounds(
                f"Dimension {dimension} out of bounds (0-{self._number_of_dimensions - 1})"
            )
        self._lower_bounds[dimension] = value

    def set_upper_bound(self, dimension: int, value: int) -> None:
        """Set upper bound for dimension"""
        if dimension < 0 or dimension >= self._number_of_dimensions:
            raise ArrayIndexOutOfBounds(
                f"Dimension {dimension} out of bounds (0-{self._number_of_dimensions - 1})"
            )
        self._upper_bounds[dimension] = value

    def commit(self, number_of_dimensions: int) -> None:
        """Commit current bounds"""
        for i in range(number_of_dimensions):
            if i < len(self._lower_bounds) and i < len(self._upper_bounds):
                self._lower_bounds_committed[i] = self._lower_bounds[i]
                self._upper_bounds_committed[i] = self._upper_bounds[i]

    def get_lower_bound_uncommitted(self, dimension: int) -> int:
        """Get uncommitted lower bound"""
        if dimension < 0 or dimension >= len(self._lower_bounds):
            raise ArrayIndexOutOfBounds(
                f"Dimension {dimension} out of bounds for lowerBounds"
            )
        return self._lower_bounds[dimension]

    def get_upper_bound_uncommitted(self, dimension: int) -> int:
        """Get uncommitted upper bound"""
        if dimension < 0 or dimension >= len(self._upper_bounds):
            raise ArrayIndexOutOfBounds(
                f"Dimension {dimension} out of bounds for upperBounds"
            )
        return self._upper_bounds[dimension]

    def get_byte_array(self) -> bytes:
        """Get byte array representation for serialization"""
        # Format: [lowerBounds.length (int), lowerBounds[] (long[]),
        #          upperBounds.length (int), upperBounds[] (long[]),
        #          lowerBoundsCommited.length (int), lowerBoundsCommited[] (long[]),
        #          upperBoundsCommited.length (int), upperBoundsCommited[] (long[])]
        # All using little-endian byte order
        
        # Validate arrays are initialized
        if (self._lower_bounds is None or self._upper_bounds is None or
            self._lower_bounds_committed is None or self._upper_bounds_committed is None):
            raise ValueError("Extent arrays not initialized")
        
        # All arrays should have the same size (numberOfDimensions)
        num_dims = len(self._lower_bounds)
        if (len(self._upper_bounds) != num_dims or
            len(self._lower_bounds_committed) != num_dims or
            len(self._upper_bounds_committed) != num_dims):
            raise ValueError(
                f"Extent arrays have inconsistent sizes: lowerBounds={len(self._lower_bounds)}, "
                f"upperBounds={len(self._upper_bounds)}, "
                f"lowerBoundsCommited={len(self._lower_bounds_committed)}, "
                f"upperBoundsCommited={len(self._upper_bounds_committed)}"
            )
        
        # Calculate required size: 4 ints (for lengths) + longs for all arrays
        total_longs = (num_dims * 4)  # 4 arrays, each with num_dims longs
        required_size = BaseConstants.SIZEOF_INT * 4 + BaseConstants.SIZEOF_LONG * total_longs
        
        if required_size <= 0 or num_dims < 0:
            raise ValueError(
                f"Invalid size calculation: numDims={num_dims}, "
                f"totalLongs={total_longs}, requiredSize={required_size}"
            )
        
        buffer = bytearray(required_size)
        pos = 0
        
        # Write lowerBounds: int (length) + longs (values)
        pos = Base.insert_int(buffer, pos, len(self._lower_bounds))
        for i in range(len(self._lower_bounds)):
            pos = Base.insert_long(buffer, pos, self._lower_bounds[i])
        
        # Write upperBounds: int (length) + longs (values)
        pos = Base.insert_int(buffer, pos, len(self._upper_bounds))
        for i in range(len(self._upper_bounds)):
            pos = Base.insert_long(buffer, pos, self._upper_bounds[i])
        
        # Write lowerBoundsCommited: int (length) + longs (values)
        pos = Base.insert_int(buffer, pos, len(self._lower_bounds_committed))
        for i in range(len(self._lower_bounds_committed)):
            pos = Base.insert_long(buffer, pos, self._lower_bounds_committed[i])
        
        # Write upperBoundsCommited: int (length) + longs (values)
        pos = Base.insert_int(buffer, pos, len(self._upper_bounds_committed))
        for i in range(len(self._upper_bounds_committed)):
            pos = Base.insert_long(buffer, pos, self._upper_bounds_committed[i])
        
        return bytes(buffer)


class Region:
    """Represents a region in routing space"""

    def __init__(self, routing_space_handle: int, number_of_extents: int, number_of_dimensions: int):
        """Initialize region"""
        self._routing_space_handle = routing_space_handle
        self._number_of_extents = number_of_extents
        self._number_of_dimensions = number_of_dimensions
        self._extents: List[Extent] = []
        self._handle = -1

        # Create extents
        for i in range(number_of_extents):
            self._extents.append(Extent(number_of_dimensions))

    def get_handle(self) -> int:
        """Get region handle"""
        return self._handle

    def set_handle(self, handle: int) -> None:
        """Set region handle"""
        self._handle = handle

    def get_number_of_extents(self) -> int:
        """Get number of extents"""
        return self._number_of_extents

    def get_space_handle(self) -> int:
        """Get routing space handle"""
        return self._routing_space_handle

    def get_handle(self) -> int:
        """Get region handle"""
        return self._handle

    def set_handle(self, handle: int) -> None:
        """Set region handle"""
        self._handle = handle

    def _convert_dimension_handle_to_array_index(self, extent_index: int, dimension_handle: int) -> int:
        """Convert dimension handle to 0-based array index"""
        if extent_index < 0 or extent_index >= len(self._extents):
            raise ArrayIndexOutOfBounds(
                f"convertDimensionHandleToArrayIndex: invalid extentIndex={extent_index}"
            )
        
        extent = self._extents[extent_index]
        array_size = self._number_of_dimensions
        
        if array_size <= 0:
            raise ArrayIndexOutOfBounds(
                f"convertDimensionHandleToArrayIndex: arraySize={array_size} is invalid"
            )
        
        if dimension_handle < 0:
            raise ArrayIndexOutOfBounds(
                f"convertDimensionHandleToArrayIndex: dimensionHandle={dimension_handle} "
                f"is negative (arraySize={array_size}, routingSpaceHandle={self._routing_space_handle})"
            )
        
        # Strategy for mapping dimension handles to array indices:
        # 1. If routing space handle is 0 (default routing space), dimension handles are 0-based
        # 2. If routing space handle is not 0, dimension handles typically start from 1
        #    (handle 1 -> index 0, handle 2 -> index 1, etc.)
        # 3. However, if the handle is already a valid array index (0 to arraySize-1), use it directly
        
        if self._routing_space_handle == 0:
            # Default routing space: handles are 0-based, use handle directly
            mapped_index = dimension_handle
        else:
            # Other routing spaces: handles typically start from 1
            # But if handle is already a valid index (0 to arraySize-1), use it directly
            # Otherwise, map handle 1 -> index 0, handle 2 -> index 1, etc.
            if dimension_handle < array_size:
                # Handle is already a valid array index, use it directly
                mapped_index = dimension_handle
            else:
                # Handle is >= arraySize, so it's likely a non-0-based handle
                # Map handle 1 -> index 0, handle 2 -> index 1, etc.
                mapped_index = dimension_handle - 1
        
        # Validate the mapped index
        if mapped_index < 0:
            raise ArrayIndexOutOfBounds(
                f"convertDimensionHandleToArrayIndex: dimensionHandle={dimension_handle} "
                f"mapped to negative index {mapped_index} "
                f"(arraySize={array_size}, routingSpaceHandle={self._routing_space_handle})"
            )
        
        if mapped_index >= array_size:
            raise ArrayIndexOutOfBounds(
                f"convertDimensionHandleToArrayIndex: dimensionHandle={dimension_handle} "
                f"cannot be mapped to valid array index (mapped={mapped_index}, "
                f"arraySize={array_size}, routingSpaceHandle={self._routing_space_handle})"
            )
        
        return mapped_index

    def get_range_lower_bound(self, extent_index: int, dimension_handle: int) -> int:
        """Get lower bound of extent along dimension"""
        if extent_index < 0 or extent_index >= len(self._extents):
            raise ArrayIndexOutOfBounds(
                f"Extent index {extent_index} out of bounds (0-{len(self._extents) - 1})"
            )
        array_index = self._convert_dimension_handle_to_array_index(extent_index, dimension_handle)
        return self._extents[extent_index].get_lower_bound(array_index)

    def get_range_upper_bound(self, extent_index: int, dimension_handle: int) -> int:
        """Get upper bound of extent along dimension"""
        if extent_index < 0 or extent_index >= len(self._extents):
            raise ArrayIndexOutOfBounds(
                f"Extent index {extent_index} out of bounds (0-{len(self._extents) - 1})"
            )
        array_index = self._convert_dimension_handle_to_array_index(extent_index, dimension_handle)
        return self._extents[extent_index].get_upper_bound(array_index)

    def set_range_lower_bound(
        self, extent_index: int, dimension_handle: int, new_lower_bound: int
    ) -> None:
        """Set lower bound of extent along dimension"""
        if extent_index < 0 or extent_index >= len(self._extents):
            raise ArrayIndexOutOfBounds(
                f"Extent index {extent_index} out of bounds (0-{len(self._extents) - 1})"
            )
        array_index = self._convert_dimension_handle_to_array_index(extent_index, dimension_handle)
        self._extents[extent_index].set_lower_bound(array_index, new_lower_bound)

    def set_range_upper_bound(
        self, extent_index: int, dimension_handle: int, new_upper_bound: int
    ) -> None:
        """Set upper bound of extent along dimension"""
        if extent_index < 0 or extent_index >= len(self._extents):
            raise ArrayIndexOutOfBounds(
                f"Extent index {extent_index} out of bounds (0-{len(self._extents) - 1})"
            )
        array_index = self._convert_dimension_handle_to_array_index(extent_index, dimension_handle)
        self._extents[extent_index].set_upper_bound(array_index, new_upper_bound)

    def modify_bounds(self) -> None:
        """Commit current bounds (modify operation)"""
        for extent in self._extents:
            extent.commit(self._number_of_dimensions)

    def get_vector(self) -> List[Any]:
        """Get vector representation for serialization"""
        # Format: [routingSpaceHandle, numberOfDimensions, handle, ...extents as bytes]
        result = [
            self._routing_space_handle,
            self._number_of_dimensions,
            self._handle
        ]
        # Auto-commit bounds if they haven't been committed yet
        # A bound is uncommitted when its committed value is still the minimum sentinel but a value has been set
        for j, extent in enumerate(self._extents):
            # Check if committed bounds need to be updated
            needs_commit = False
            if extent._lower_bounds_committed is not None and len(extent._lower_bounds_committed) > 0:
                for k in range(len(extent._lower_bounds_committed)):
                    # If committed bound is still at initial value but uncommitted bound has been changed
                    if (extent._lower_bounds_committed[k] == -(2**63) and
                        extent._lower_bounds[k] != -(2**63)):
                        needs_commit = True
                        break
            elif extent._lower_bounds is not None and len(extent._lower_bounds) > 0:
                # Committed bounds arrays not initialized, initialize and commit
                needs_commit = True
            
            if needs_commit:
                # Auto-commit bounds if they're not set but uncommitted bounds have values
                extent.commit(self._number_of_dimensions)
        
        # Add extents as byte arrays
        # Each extent is serialized to its byte array form
        for extent in self._extents:
            result.append(extent.get_byte_array())
        return result

    def is_overlap(self, other: "Region") -> bool:
        """Check if this region overlaps with another region"""
        if other is None:
            return False

        # Check if same routing space
        if self._routing_space_handle != other._routing_space_handle:
            return False

        # Check if same number of extents
        if len(self._extents) != len(other._extents):
            return False

        # Check each extent
        for i in range(len(self._extents)):
            extent1 = self._extents[i]
            extent2 = other._extents[i]

            if extent1 is None or extent2 is None:
                return False

            # Check each dimension
            for j in range(self._number_of_dimensions):
                lower1 = extent1.get_lower_bound_uncommitted(j)
                upper1 = extent1.get_upper_bound_uncommitted(j)
                lower2 = extent2.get_lower_bound_uncommitted(j)
                upper2 = extent2.get_upper_bound_uncommitted(j)

                # Two intervals [a, b] and [c, d] overlap if: b >= c && d >= a
                # They DON'T overlap if: b < c || d < a
                if upper1 < lower2 or lower1 > upper2:
                    return False  # No overlap on this dimension

        return True  # All extents and dimensions overlap

