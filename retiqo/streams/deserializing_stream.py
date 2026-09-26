# Copyright 2026 Loreum Digital Inc
# SPDX-License-Identifier: Apache-2.0
"""
DeserializingStream - for deserializing data from byte arrays
"""
from typing import List, Any, Optional
from retiqo.streams.base import Base, BaseConstants


class DeserializingStream:
    """Stream for deserializing data"""

    def __init__(self, data: bytes):
        """Initialize deserializing stream"""
        self._data = data
        self._pos = 0
        self._constants = BaseConstants()

    def read_tc(self) -> int:
        """Read type code"""
        if self._pos >= len(self._data):
            raise IndexError("End of stream")
        tc = self._data[self._pos]
        self._pos += 1
        return tc

    def read_boolean(self) -> bool:
        """Read boolean (type code should already be read by read_object)"""
        # The type code has already been read by the caller; read the value only
        if self._pos >= len(self._data):
            raise IndexError("End of stream")
        value = Base.extract_boolean(self._data, self._pos)
        self._pos += BaseConstants.SIZEOF_BOOLEAN
        return value

    def read_byte(self) -> int:
        """Read byte (without type code)"""
        if self._pos >= len(self._data):
            raise IndexError("End of stream")
        value = Base.extract_byte(self._data, self._pos)
        self._pos += BaseConstants.SIZEOF_BYTE
        return value

    def read_short(self) -> int:
        """Read short (without type code)"""
        if self._pos + BaseConstants.SIZEOF_SHORT > len(self._data):
            raise IndexError("End of stream")
        value = Base.extract_short(self._data, self._pos)
        self._pos += BaseConstants.SIZEOF_SHORT
        return value

    def read_int(self) -> int:
        """Read int (without type code)"""
        if self._pos + BaseConstants.SIZEOF_INT > len(self._data):
            raise IndexError("End of stream")
        value = Base.extract_int(self._data, self._pos)
        self._pos += BaseConstants.SIZEOF_INT
        return value

    def read_long(self) -> int:
        """Read long (type code should already be read by read_object)"""
        # The type code has already been read by the caller; read the value only
        if self._pos + BaseConstants.SIZEOF_LONG > len(self._data):
            raise IndexError("End of stream")
        value = Base.extract_long(self._data, self._pos)
        self._pos += BaseConstants.SIZEOF_LONG
        return value

    def read_string(self) -> str:
        """Read string (type code should already be read by read_object)"""
        # Strings are read as UTF-8 byte arrays:
        # 1. Reads length as raw int (no TC_INT)
        # 2. Raw bytes (no type codes)
        length = Base.extract_int(self._data, self._pos)
        self._pos += BaseConstants.SIZEOF_INT
        # Read bytes directly (no TC_BYTE prefix - readByte() in readByteArray() reads raw bytes)
        utf8_bytes = self._data[self._pos : self._pos + length]
        self._pos += length
        return utf8_bytes.decode("utf-8")

    def read_bytes(self) -> bytes:
        """Read bytes (TC_BYTE | TC_FLAG_ARRAY should already be read by caller)"""
        # Byte arrays are read as:
        # 1. Length as raw int (no TC_INT)
        # 2. Raw bytes (no type codes)
        length = Base.extract_int(self._data, self._pos)
        self._pos += BaseConstants.SIZEOF_INT
        value = self._data[self._pos : self._pos + length]
        self._pos += length
        return value

    def read_int_array(self) -> List[int]:
        """Read int array (TC_INT | TC_FLAG_ARRAY should already be read by caller)"""
        # Int arrays are read as:
        # 1. Length as raw int (no TC_INT)
        # 2. Each element as raw int (no type code)
        length = Base.extract_int(self._data, self._pos)
        self._pos += BaseConstants.SIZEOF_INT
        result = []
        for _ in range(length):
            # readInt() reads raw int (no type code) - just Base.extractInt()
            value = Base.extract_int(self._data, self._pos)
            self._pos += BaseConstants.SIZEOF_INT
            result.append(value)
        return result

    def read_vector(self) -> List[Any]:
        """Read vector"""
        tc = self.read_tc()
        if tc != BaseConstants.TC_VECTOR:
            raise ValueError(f"Expected TC_VECTOR, got {tc}")
        length = self.read_int()
        return []  # Elements will be read by caller

    def read_object(self) -> Any:
        """Read object (delegates to Marshaller)"""
        from retiqo.streams.marshaller import Marshaller
        return Marshaller.read_object(self)

    def remaining(self) -> int:
        """Get remaining bytes"""
        return len(self._data) - self._pos

    def position(self) -> int:
        """Get current position"""
        return self._pos

    def set_position(self, pos: int) -> None:
        """Set position"""
        self._pos = pos

