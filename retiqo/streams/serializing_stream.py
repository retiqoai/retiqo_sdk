# Copyright 2026 Loreum Digital Inc
# SPDX-License-Identifier: Apache-2.0
"""
SerializingStream - for serializing data to byte arrays
"""
import io
from typing import List, Any, Optional
from retiqo.streams.base import Base, BaseConstants


class SerializingStream:
    """Stream for serializing data"""

    def __init__(self, stream_out: Optional[io.BytesIO] = None):
        """Initialize serializing stream"""
        self._buffer = bytearray()
        self._constants = BaseConstants()
        self.stream_out = stream_out or io.BytesIO()

    def write_tc(self, tc: int) -> None:
        """Write type code"""
        self._buffer.append(tc & 0xFF)

    def write_boolean(self, value: bool) -> None:
        """Write boolean"""
        self.write_tc(BaseConstants.TC_BOOLEAN)
        Base.insert_boolean(self._buffer, len(self._buffer), value)
        self._buffer.append(1 if value else 0)

    def write_byte(self, value: int) -> None:
        """Write byte"""
        self.write_tc(BaseConstants.TC_BYTE)
        self._buffer.append(value & 0xFF)

    def write_short(self, value: int) -> None:
        """Write short"""
        self.write_tc(BaseConstants.TC_SHORT)
        pos = len(self._buffer)
        self._buffer.extend(b"\x00\x00")
        Base.insert_short(self._buffer, pos, value)

    def write_int(self, value: int) -> None:
        """Write int"""
        self.write_tc(BaseConstants.TC_INT)
        pos = len(self._buffer)
        self._buffer.extend(b"\x00\x00\x00\x00")
        Base.insert_int(self._buffer, pos, value)

    def write_long(self, value: int) -> None:
        """Write long"""
        self.write_tc(BaseConstants.TC_LONG)
        pos = len(self._buffer)
        self._buffer.extend(b"\x00\x00\x00\x00\x00\x00\x00\x00")
        Base.insert_long(self._buffer, pos, value)

    def write_string(self, value: str) -> None:
        """Write string"""
        self.write_tc(BaseConstants.TC_STRING)
        utf8_bytes = value.encode("utf-8")
        # Strings are written as UTF-8 byte arrays:
        # 1. Writes length as raw int (no TC_INT)
        # 2. Writes bytes directly (no type codes)
        pos = len(self._buffer)
        self._buffer.extend(b"\x00\x00\x00\x00")
        Base.insert_int(self._buffer, pos, len(utf8_bytes))
        # Write bytes directly (no TC_BYTE prefix)
        self._buffer.extend(utf8_bytes)

    def write_bytes(self, value: bytes) -> None:
        """Write bytes (TC_BYTE | TC_FLAG_ARRAY should already be written by caller)"""
        # Byte arrays are written as:
        # 1. Length as raw int (no TC_INT)
        # 2. Bytes directly (no type codes)
        length = len(value)
        pos = len(self._buffer)
        self._buffer.extend(b"\x00\x00\x00\x00")
        Base.insert_int(self._buffer, pos, length)
        self._buffer.extend(value)

    def write_int_array(self, values: List[int]) -> None:
        """Write int array (TC_INT | TC_FLAG_ARRAY should already be written by caller)"""
        # Int arrays are written as:
        # 1. Length as raw int (no TC_INT)
        # 2. Each element as raw int (no TC_INT type code)
        length = len(values)
        pos = len(self._buffer)
        self._buffer.extend(b"\x00\x00\x00\x00")
        Base.insert_int(self._buffer, pos, length)
        # Write each element as raw int (no TC_INT type code)
        for value in values:
            pos = len(self._buffer)
            self._buffer.extend(b"\x00\x00\x00\x00")
            Base.insert_int(self._buffer, pos, value)

    def write_vector(self, elements: List[Any]) -> None:
        """Write vector (TC_VECTOR should already be written by caller)"""
        # TC_VECTOR is written by the caller, and the length has no TC_INT prefix
        # So we just write the length as raw int bytes (4 bytes, big-endian)
        length = len(elements)
        pos = len(self._buffer)
        self._buffer.extend(b"\x00\x00\x00\x00")
        Base.insert_int(self._buffer, pos, length)
        # Elements will be written by caller

    def write_object(self, obj: Any) -> None:
        """Write object (delegates to Marshaller)"""
        from retiqo.streams.marshaller import Marshaller
        Marshaller.write_object(self, obj)

    def flush(self) -> None:
        """Flush the stream (no-op for in-memory buffer)"""
        # For in-memory buffer, flush is a no-op
        # Data is already in _buffer
        pass

    def to_bytes(self) -> bytes:
        """Get serialized bytes"""
        return bytes(self._buffer)

    def reset(self) -> None:
        """Reset the stream"""
        self._buffer = bytearray()

