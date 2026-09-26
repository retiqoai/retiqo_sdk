# Copyright 2026 Loreum Digital Inc
# SPDX-License-Identifier: Apache-2.0
"""
Marshaller - serialization utilities
"""
from typing import Any, List, Optional
from retiqo.streams.base import Base, BaseConstants
from retiqo.streams.serializing_stream import SerializingStream
from retiqo.streams.deserializing_stream import DeserializingStream
import io


class MarshallerException(Exception):
    """Marshaller exception"""

    def __init__(self, message: str = ""):
        super().__init__(message)
        self.message = message


class Marshaller:
    """Marshaller for serialization"""

    @staticmethod
    def get_obj_type(obj: Any) -> int:
        """Get object type code"""
        if obj is None:
            return BaseConstants.TC_NULL

        # Check for special wrapper classes that force vector serialization
        # (used for method parameters that need vector instead of int array)
        # _VectorParam wrapper has _items attribute - treat as vector
        if hasattr(obj, '_items') and not isinstance(obj, list):
            return BaseConstants.TC_VECTOR

        if isinstance(obj, bool):
            return BaseConstants.TC_BOOLEAN
        elif isinstance(obj, int):
            # Integers are always encoded as TC_INT, regardless of value (never TC_BYTE)
            if -(2**31) <= obj <= 2**31 - 1:
                return BaseConstants.TC_INT
            else:
                return BaseConstants.TC_LONG
        elif isinstance(obj, str):
            return BaseConstants.TC_STRING
        elif isinstance(obj, list):
            # Check if it's a homogeneous list of integers (int array array)
            # Int lists are encoded as TC_INT | TC_FLAG_ARRAY, not TC_VECTOR
            if len(obj) > 0 and all(isinstance(x, int) for x in obj):
                return BaseConstants.TC_INT | BaseConstants.TC_FLAG_ARRAY
            return BaseConstants.TC_VECTOR
        elif isinstance(obj, bytes):
            return BaseConstants.TC_BYTE | BaseConstants.TC_FLAG_ARRAY
        elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes)):
            # For iterable objects (like _VectorParam), treat as vector
            return BaseConstants.TC_VECTOR
        else:
            return BaseConstants.TC_UNKNOWN

    @staticmethod
    def pack_object(sequence_number: int, method_id: int, tc_in: int, tc_out: int, obj: Any) -> bytes:
        """Pack object for transmission"""
        from retiqo.streams.serializing_stream import SerializingStream

        s_out = SerializingStream()

        # Write object
        s_out.write_object(obj)

        obj_bytes = s_out.to_bytes()

        if obj_bytes:
            # Create packet: sequence (2 bytes) + method_id (1 byte) + tc_in (1 byte) + tc_out (1 byte) + object data
            # The invoke request always includes tcIn and tcOut
            packet = bytearray(BaseConstants.SIZEOF_SHORT + BaseConstants.SIZEOF_BYTE + BaseConstants.SIZEOF_BYTE + BaseConstants.SIZEOF_BYTE + len(obj_bytes))
            k = 0
            k = Base.insert_short(packet, k, sequence_number)
            k = Base.insert_byte(packet, k, method_id)
            k = Base.insert_byte(packet, k, tc_in)
            k = Base.insert_byte(packet, k, tc_out)
            packet[k:] = obj_bytes
            return bytes(packet)

        return b""

    @staticmethod
    def pack_void(sequence_number: int, method_id: int, tc_in: int, tc_out: int) -> bytes:
        """Pack void (no object) for transmission"""
        # The invoke request includes tcIn and tcOut even for void calls
        packet = bytearray(BaseConstants.SIZEOF_SHORT + BaseConstants.SIZEOF_BYTE + BaseConstants.SIZEOF_BYTE + BaseConstants.SIZEOF_BYTE)
        k = 0
        k = Base.insert_short(packet, k, sequence_number)
        k = Base.insert_byte(packet, k, method_id)
        k = Base.insert_byte(packet, k, tc_in)
        k = Base.insert_byte(packet, k, tc_out)
        return bytes(packet)

    @staticmethod
    def write_object(stream: SerializingStream, obj: Any) -> None:
        """Write object to serializing stream"""
        obj_type = Marshaller.get_obj_type(obj)

        if obj_type == BaseConstants.TC_NULL:
            stream.write_tc(BaseConstants.TC_NULL)
        elif obj_type == BaseConstants.TC_BOOLEAN:
            stream.write_boolean(obj)
        elif obj_type == BaseConstants.TC_BYTE:
            stream.write_byte(obj)
        elif obj_type == BaseConstants.TC_SHORT:
            stream.write_short(obj)
        elif obj_type == BaseConstants.TC_INT:
            stream.write_int(obj)
        elif obj_type == BaseConstants.TC_LONG:
            stream.write_long(obj)
        elif obj_type == BaseConstants.TC_STRING:
            stream.write_string(obj)
        elif obj_type == BaseConstants.TC_VECTOR:
            # Write TC_VECTOR first, then the vector contents
            stream.write_tc(BaseConstants.TC_VECTOR)
            # Handle special wrapper classes that force vector serialization
            if hasattr(obj, '_items'):
                # _VectorParam wrapper - unwrap to get the actual items
                items = obj._items
            else:
                items = obj
            stream.write_vector(items)
            for element in items:
                Marshaller.write_object(stream, element)
        elif obj_type == (BaseConstants.TC_INT | BaseConstants.TC_FLAG_ARRAY):
            # Write TC_INT | TC_FLAG_ARRAY first, then the array contents
            stream.write_tc(BaseConstants.TC_INT | BaseConstants.TC_FLAG_ARRAY)
            stream.write_int_array(obj)
        elif obj_type == (BaseConstants.TC_BYTE | BaseConstants.TC_FLAG_ARRAY):
            # Write TC_BYTE | TC_FLAG_ARRAY first, then the array contents
            stream.write_tc(BaseConstants.TC_BYTE | BaseConstants.TC_FLAG_ARRAY)
            stream.write_bytes(obj)
        else:
            raise MarshallerException(f"Unsupported object type: {obj_type}")

    @staticmethod
    def read_object(stream: DeserializingStream) -> Any:
        """Read object from deserializing stream"""
        tc = stream.read_tc()

        if tc == BaseConstants.TC_NULL:
            return None
        elif tc == BaseConstants.TC_BOOLEAN:
            return stream.read_boolean()
        elif tc == BaseConstants.TC_BYTE:
            return stream.read_byte()
        elif tc == BaseConstants.TC_SHORT:
            return stream.read_short()
        elif tc == BaseConstants.TC_INT:
            return stream.read_int()
        elif tc == BaseConstants.TC_LONG:
            return stream.read_long()
        elif tc == BaseConstants.TC_STRING:
            return stream.read_string()
        elif tc == BaseConstants.TC_VECTOR:
            length = stream.read_int()
            result = []
            for _ in range(length):
                result.append(Marshaller.read_object(stream))
            return result
        elif tc == (BaseConstants.TC_INT | BaseConstants.TC_FLAG_ARRAY):
            # Int array: read length, then read each int (with TC_INT type code)
            return stream.read_int_array()
        elif tc == (BaseConstants.TC_BYTE | BaseConstants.TC_FLAG_ARRAY):
            return stream.read_bytes()
        elif tc == (BaseConstants.TC_STRING | BaseConstants.TC_FLAG_ARRAY):
            # String array: read length, then read each string
            # String arrays: length, then each element as a string
            # readString() calls readByteArray(), which reads length + bytes (no type code)
            length = stream.read_int()
            result = []
            for _ in range(length):
                # readString() doesn't read a type code - it directly reads the byte array
                result.append(stream.read_string())
            return result
        else:
            raise MarshallerException(f"Unsupported type code: {tc}")

