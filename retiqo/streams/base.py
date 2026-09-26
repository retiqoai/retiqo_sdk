# Copyright 2026 Loreum Digital Inc
# SPDX-License-Identifier: Apache-2.0
"""
Base utilities for binary serialization
"""
import struct
from typing import List


class BaseConstants:
    """Constants for serialization"""

    # Sizes of primitives
    SIZEOF_BOOLEAN = 1
    SIZEOF_BYTE = 1
    SIZEOF_CHAR = 2
    SIZEOF_SHORT = 2
    SIZEOF_INT = 4
    SIZEOF_LONG = 8

    # Remote method call results
    RZ_OK = 0x0000
    RZ_FAILED = 0x0001
    RZ_FAILED_OUTOFMEMORY = 0x0002
    RZ_FAILED_HDRSEND = 0x0003
    RZ_FAILED_WRONGFORMATREAD = 0x0004
    RZ_FAILED_CLASSNOTFOUND = 0x0005
    RZ_FAILED_ILLEGALACCESS = 0x0006
    RZ_FAILED_INSTANTIATION = 0x0007
    RZ_FAILED_NOSUCHMETHOD = 0x0008
    RZ_FAILED_INVOCATIONTARGET = 0x0009
    RZ_FAILED_IO = 0x000A
    RZ_FAILED_FINDINSTANCE = 0x000B
    RZ_FAILED_EMPTYVECTOR = 0x000C
    RZ_FAILED_INVALIDRETURNTYPE = 0x000D
    RZ_FAILED_INVALIDLOGIN = 0x000E
    RZ_FAILED_SESSIONNOTFOUND = 0x000F
    RZ_FAILED_PROXYSESSIONEX = 0x0012
    RZ_FAILED_SESSIONGENEX = 0x0013

    # Type codes
    TC_NULL = 0x00
    TC_VOID = 0x01
    TC_BOOLEAN = 0x02
    TC_BYTE = 0x03
    TC_CHAR = 0x04
    TC_SHORT = 0x05
    TC_INT = 0x06
    TC_LONG = 0x07
    TC_STRING = 0x08
    TC_VECTOR = 0x0B
    TC_OBJECT = 0x0F
    TC_UNKNOWN = 0xFF

    TC_FLAG_ARRAY = 0x10
    TC_FLAG_PRIMITIVE = 0x20
    TC_FLAG_OBJ = 0x40

    LEN_SESSION_ID = 16
    LEN_HEADER = 2 * SIZEOF_SHORT + SIZEOF_BYTE

    LEN_PDU_S_CONNECT_REQ = 1 + 1
    LEN_PDU_S_CONNECT_RES = LEN_HEADER
    LEN_PDU_S_DISCONNECT_REQ = 1 + LEN_SESSION_ID + SIZEOF_LONG
    LEN_PDU_S_DISCONNECT_RES = LEN_HEADER
    LEN_PDU_S_CREATEINSTANCE_REQ = 1 + LEN_SESSION_ID + 1 + SIZEOF_SHORT + SIZEOF_LONG
    LEN_PDU_S_CREATEINSTANCE_RES = LEN_HEADER
    LEN_PDU_S_DESTROYINSTANCE_REQ = 1 + LEN_SESSION_ID + 1 + SIZEOF_LONG
    LEN_PDU_S_DESTROYINSTANCE_RES = LEN_HEADER
    LEN_PDU_S_INVOKE_REQ = 1 + SIZEOF_SHORT + 3 * SIZEOF_BYTE
    LEN_PDU_S_KEEPALIVE = 1 + SIZEOF_SHORT


class Base:
    """Base utilities for serialization"""

    @staticmethod
    def insert_byte(buffer: bytearray, pos: int, value: int) -> int:
        """Insert byte into buffer"""
        buffer[pos] = value & 0xFF
        return pos + 1

    @staticmethod
    def insert_boolean(buffer: bytearray, pos: int, value: bool) -> int:
        """Insert boolean into buffer"""
        buffer[pos] = 1 if value else 0
        return pos + 1

    @staticmethod
    def insert_short(buffer: bytearray, pos: int, value: int) -> int:
        """Insert short (2 bytes, little-endian) into buffer"""
        # Little-endian: low byte first
        struct.pack_into("<H", buffer, pos, value & 0xFFFF)
        return pos + 2

    @staticmethod
    def insert_int(buffer: bytearray, pos: int, value: int) -> int:
        """Insert int (4 bytes, little-endian) into buffer"""
        # Little-endian: low byte first
        # This is LITTLE-ENDIAN (LSB first)!
        struct.pack_into("<I", buffer, pos, value & 0xFFFFFFFF)
        return pos + 4

    @staticmethod
    def insert_long(buffer: bytearray, pos: int, value: int) -> int:
        """Insert long (8 bytes, little-endian) into buffer"""
        # Little-endian: low byte first
        # This is LITTLE-ENDIAN, not big-endian!
        # Signed 64-bit, so use '<q'
        # Mask to ensure we only use the lower 64 bits (handles Python's arbitrary precision ints)
        value = value & 0xFFFFFFFFFFFFFFFF
        # Convert to signed: if the MSB is set, it's negative in two's complement
        if value >= 2**63:
            value = value - 2**64
        struct.pack_into("<q", buffer, pos, value)
        return pos + 8

    @staticmethod
    def extract_byte(buffer: bytes, pos: int) -> int:
        """Extract byte from buffer"""
        return buffer[pos] & 0xFF

    @staticmethod
    def extract_boolean(buffer: bytes, pos: int) -> bool:
        """Extract boolean from buffer"""
        return buffer[pos] != 0

    @staticmethod
    def extract_short(buffer: bytes, pos: int) -> int:
        """Extract short (2 bytes, little-endian) from buffer"""
        # Little-endian: low byte first
        return struct.unpack_from("<H", buffer, pos)[0]

    @staticmethod
    def extract_int(buffer: bytes, pos: int) -> int:
        """Extract int (4 bytes, little-endian) from buffer"""
        # Little-endian: low byte first
        # This is LITTLE-ENDIAN (LSB first)!
        return struct.unpack_from("<I", buffer, pos)[0]

    @staticmethod
    def extract_long(buffer: bytes, pos: int) -> int:
        """Extract long (8 bytes, little-endian) from buffer"""
        # Little-endian: low byte first
        # This is LITTLE-ENDIAN, not big-endian!
        return struct.unpack_from("<Q", buffer, pos)[0]

    @staticmethod
    def to_hex_string(data: bytes) -> str:
        """Convert bytes to hex string"""
        return data.hex().upper()

