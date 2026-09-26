# Copyright 2026 Loreum Digital Inc
# SPDX-License-Identifier: Apache-2.0
"""
HashUtil - hashing utilities (SHA3/Keccak)
"""
import hashlib
from Crypto.Hash import keccak


class HashUtil:
    """Hashing utilities"""

    EMPTY_DATA_HASH: bytes
    EMPTY_LIST_HASH: bytes
    EMPTY_TRIE_HASH: bytes

    @staticmethod
    def _init():
        """Initialize static constants"""
        HashUtil.EMPTY_DATA_HASH = HashUtil.sha3(b"")
        # Empty list and trie hashes would need RLP encoding
        HashUtil.EMPTY_LIST_HASH = HashUtil.sha3(b"")
        HashUtil.EMPTY_TRIE_HASH = HashUtil.sha3(b"")

    @staticmethod
    def sha256(input_data: bytes) -> bytes:
        """SHA-256 hash"""
        return hashlib.sha256(input_data).digest()

    @staticmethod
    def sha3(input_data: bytes) -> bytes:
        """SHA3/Keccak-256 hash"""
        k = keccak.new(digest_bits=256)
        k.update(input_data)
        return k.digest()

    @staticmethod
    def sha3_multiple(*inputs: bytes) -> bytes:
        """SHA3 hash of multiple inputs"""
        k = keccak.new(digest_bits=256)
        for input_data in inputs:
            k.update(input_data)
        return k.digest()


# Initialize static constants
HashUtil._init()

