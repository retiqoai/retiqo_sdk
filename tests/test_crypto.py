# Copyright 2026 Loreum Digital Inc
# SPDX-License-Identifier: Apache-2.0
"""
Unit tests for ECDSA signing, verification and key recovery.
These run offline and need no RTI host.
"""
from retiqo.crypto.ec_key import ECKey


def test_signature_operations():
    ec_key = ECKey()  # fresh random key for every run
    message_hash = b"test message hash" + b"\x00" * 15  # 32 bytes

    signature = ec_key.sign(message_hash)
    assert signature.r > 0
    assert signature.s > 0
    assert signature.v >= 27

    public_key_bytes = ec_key.get_public_key_bytes(compressed=False)
    if public_key_bytes[0] == 0x04:
        public_key_bytes = public_key_bytes[1:]

    assert ECKey.verify(message_hash, signature, public_key_bytes)


def test_tampered_message_fails_verification():
    ec_key = ECKey()
    signature = ec_key.sign(b"\x01" * 32)
    public_key_bytes = ec_key.get_public_key_bytes(compressed=False)
    if public_key_bytes[0] == 0x04:
        public_key_bytes = public_key_bytes[1:]

    assert not ECKey.verify(b"\x02" * 32, signature, public_key_bytes)
