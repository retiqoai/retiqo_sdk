# Copyright 2026 Loreum Digital Inc
# SPDX-License-Identifier: Apache-2.0
"""
ECKey - Elliptic Curve Key operations (secp256k1)
"""
from typing import Optional
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePrivateKey, EllipticCurvePublicKey
from cryptography.hazmat.primitives.asymmetric import utils as asym_utils
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from Crypto.Signature import DSS
from Crypto.PublicKey import ECC
from Crypto.Hash import keccak
import base64
import hashlib

try:
    from eth_keys import keys
    from eth_keys.exceptions import BadSignature
    ETH_KEYS_AVAILABLE = True
except ImportError:
    ETH_KEYS_AVAILABLE = False
    # Fallback to manual implementation if eth_keys not available


class ECDSASignature:
    """ECDSA Signature"""

    def __init__(self, r: int, s: int, v: int = 0):
        """Initialize signature with r, s, and recovery id v"""
        self.r = r
        self.s = s
        self.v = v

    def to_byte_array(self) -> bytes:
        """Convert signature to byte array (65 bytes: v + r + s) - wire format"""
        r_bytes = self.r.to_bytes(32, "big")
        s_bytes = self.s.to_bytes(32, "big")
        # Wire format: [v (1 byte), r (32 bytes), s (32 bytes)]
        return bytes([self.v]) + r_bytes + s_bytes

    def to_base64(self) -> str:
        """Convert signature to base64 string"""
        return base64.b64encode(self.to_byte_array()).decode("utf-8")

    @classmethod
    def from_base64(cls, base64_str: str) -> "ECDSASignature":
        """Create signature from base64 string"""
        data = base64.b64decode(base64_str)
        if len(data) != 65:
            raise ValueError("Invalid signature length")
        # Wire format: [v (1 byte), r (32 bytes), s (32 bytes)]
        v = data[0]
        r = int.from_bytes(data[1:33], "big")
        s = int.from_bytes(data[33:65], "big")
        return cls(r, s, v)

    @classmethod
    def from_components(cls, r_bytes: bytes, s_bytes: bytes, v: int = 0) -> "ECDSASignature":
        """Create signature from r, s components"""
        r = int.from_bytes(r_bytes, "big")
        s = int.from_bytes(s_bytes, "big")
        return cls(r, s, v)

    @classmethod
    def decode_from_der(cls, der_bytes: bytes) -> "ECDSASignature":
        """Decode signature from DER format"""
        # Simple DER parser
        if der_bytes[0] != 0x30:
            raise ValueError("Invalid DER signature format")
        
        pos = 2  # Skip 0x30 and length byte
        
        # Read r
        if der_bytes[pos] != 0x02:
            raise ValueError("Invalid DER signature format - expected INTEGER for r")
        pos += 1
        r_length = der_bytes[pos]
        pos += 1
        r_bytes = der_bytes[pos:pos + r_length]
        if r_bytes[0] == 0x00 and len(r_bytes) > 32:
            r_bytes = r_bytes[1:]
        pos += r_length
        
        # Read s
        if der_bytes[pos] != 0x02:
            raise ValueError("Invalid DER signature format - expected INTEGER for s")
        pos += 1
        s_length = der_bytes[pos]
        pos += 1
        s_bytes = der_bytes[pos:pos + s_length]
        if s_bytes[0] == 0x00 and len(s_bytes) > 32:
            s_bytes = s_bytes[1:]
        
        r = int.from_bytes(r_bytes, "big")
        s = int.from_bytes(s_bytes, "big")
        
        return cls(r, s)


class ECKey:
    """Elliptic Curve Key (secp256k1)"""

    def __init__(self, private_key: Optional[bytes] = None):
        """Initialize ECKey with optional private key
        
        Args:
            private_key: Either DER-encoded private key bytes, or raw 32-byte private key
        """
        if private_key is None:
            # Generate new key pair
            self._private_key = ec.generate_private_key(ec.SECP256K1(), default_backend())
        else:
            # Try to load as DER first, if that fails, treat as raw 32-byte key
            try:
                self._private_key = serialization.load_der_private_key(
                    private_key, password=None, backend=default_backend()
                )
            except (ValueError, TypeError):
                # Not DER format - assume it's a raw 32-byte private key
                if len(private_key) != 32:
                    raise ValueError(f"Private key must be 32 bytes, got {len(private_key)} bytes")
                # Convert raw bytes to cryptography private key
                private_value = int.from_bytes(private_key, "big")
                self._private_key = ec.derive_private_key(private_value, ec.SECP256K1(), default_backend())

        self._public_key = self._private_key.public_key()
        
        # Cache eth_keys private key for signing (if available)
        self._eth_private_key: Optional[object] = None
        if ETH_KEYS_AVAILABLE and self._private_key is not None:
            try:
                # Get raw private key bytes (32 bytes)
                priv_key_bytes = self._get_raw_private_key_bytes()
                if priv_key_bytes:
                    self._eth_private_key = keys.PrivateKey(priv_key_bytes)
            except Exception:
                pass  # Fall back to cryptography signing

    @classmethod
    def from_private(cls, private_key_bytes: bytes) -> "ECKey":
        """Create ECKey from private key bytes"""
        return cls(private_key_bytes)

    def get_private_key_bytes(self) -> bytes:
        """Get private key as bytes (DER format)"""
        return self._private_key.private_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
    
    def _get_raw_private_key_bytes(self) -> Optional[bytes]:
        """Get raw 32-byte private key for eth_keys"""
        if self._private_key is None:
            return None
        try:
            # Extract raw private key value from cryptography private key
            # This is a bit hacky but necessary to get the raw 32-byte value
            priv_key_numbers = self._private_key.private_numbers()
            priv_key_int = priv_key_numbers.private_value
            return priv_key_int.to_bytes(32, "big")
        except Exception:
            return None

    def get_public_key_bytes(self, compressed: bool = False) -> bytes:
        """Get public key as bytes"""
        return self._public_key.public_bytes(
            encoding=serialization.Encoding.X962,
            format=serialization.PublicFormat.CompressedPoint if compressed else serialization.PublicFormat.UncompressedPoint,
        )

    def do_sign(self, message_hash: bytes) -> ECDSASignature:
        """Internal signing method - signs message hash and returns signature without recovery ID"""
        if len(message_hash) != 32:
            raise ValueError(f"Expected 32 byte input to ECDSA signature, not {len(message_hash)}")
        
        if self._private_key is None:
            raise ValueError("Private key not available for signing")
        
        # Prefer eth_keys for signing if available (ensures compatibility with recovery)
        if ETH_KEYS_AVAILABLE and self._eth_private_key is not None:
            try:
                eth_sig = self._eth_private_key.sign_msg_hash(message_hash)
                # Extract r, s from eth_keys signature
                sig_bytes = eth_sig.to_bytes()
                # eth_keys signature format: r (32) + s (32) + v (1)
                r = int.from_bytes(sig_bytes[0:32], "big")
                s = int.from_bytes(sig_bytes[32:64], "big")
                # Don't canonicalize s here - eth_keys already does it
                # Return signature without recovery ID (will be set in sign() method)
                return ECDSASignature(r, s)
            except Exception:
                pass  # Fall back to cryptography
        
        # Fallback to cryptography library with prehashed signature
        # Since message_hash is already a hash, we use Prehashed to avoid double hashing
        signature_der = self._private_key.sign(
            message_hash,
            ec.ECDSA(asym_utils.Prehashed(hashes.SHA256()))
        )
        
        # Parse DER signature to get r and s
        # DER format: SEQUENCE { INTEGER r, INTEGER s }
        # We need to extract r and s from DER encoding
        return self._parse_der_signature(signature_der)

    def _parse_der_signature(self, der_signature: bytes) -> ECDSASignature:
        """Parse DER-encoded signature to extract r and s components"""
        # Simple DER parser for ECDSA signature
        # Format: 0x30 [length] 0x02 [r_length] [r_bytes] 0x02 [s_length] [s_bytes]
        if der_signature[0] != 0x30:
            raise ValueError("Invalid DER signature format")
        
        pos = 2  # Skip 0x30 and length byte
        
        # Read r
        if der_signature[pos] != 0x02:
            raise ValueError("Invalid DER signature format - expected INTEGER for r")
        pos += 1
        r_length = der_signature[pos]
        pos += 1
        r_bytes = der_signature[pos:pos + r_length]
        # Remove leading zero if present
        if r_bytes[0] == 0x00 and len(r_bytes) > 32:
            r_bytes = r_bytes[1:]
        pos += r_length
        
        # Read s
        if der_signature[pos] != 0x02:
            raise ValueError("Invalid DER signature format - expected INTEGER for s")
        pos += 1
        s_length = der_signature[pos]
        pos += 1
        s_bytes = der_signature[pos:pos + s_length]
        # Remove leading zero if present
        if s_bytes[0] == 0x00 and len(s_bytes) > 32:
            s_bytes = s_bytes[1:]
        
        # Convert to integers
        r = int.from_bytes(r_bytes, "big")
        s = int.from_bytes(s_bytes, "big")
        
        # Canonicalize s (s should be <= N/2 where N is curve order)
        # For secp256k1, N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
        N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
        HALF_N = N // 2
        if s > HALF_N:
            s = N - s
        
        return ECDSASignature(r, s)

    def sign(self, message_hash: bytes) -> ECDSASignature:
        """Sign a message hash and return signature with recovery ID"""
        if len(message_hash) != 32:
            raise ValueError(f"Expected 32 byte message hash, got {len(message_hash)}")
        
        # If we used eth_keys for signing, extract the recovery ID directly
        if ETH_KEYS_AVAILABLE and self._eth_private_key is not None:
            try:
                eth_sig = self._eth_private_key.sign_msg_hash(message_hash)
                sig_bytes = eth_sig.to_bytes()
                # eth_keys signature format: r (32) + s (32) + v (1)
                r = int.from_bytes(sig_bytes[0:32], "big")
                s = int.from_bytes(sig_bytes[32:64], "big")
                rec_id = sig_bytes[64]  # Recovery ID from eth_keys (0-3)
                # The base64 form carries v directly; key recovery expects v in range 27-34 (Ethereum format)
                # It then converts: recId = header - 27
                # So we need to use Ethereum format (27-30), not recovery ID (0-3)
                v = rec_id + 27  # Convert to Ethereum format (27-30)
                return ECDSASignature(r, s, v)
            except Exception:
                pass  # Fall back to manual recovery
        
        # Fallback: Get signature without recovery ID and find it manually
        sig = self.do_sign(message_hash)
        
        # Find recovery ID by trying all 4 possibilities
        public_key_bytes = self.get_public_key_bytes(compressed=False)
        # Remove 0x04 prefix if present
        if public_key_bytes[0] == 0x04:
            public_key_bytes = public_key_bytes[1:]
        
        rec_id = -1
        for i in range(4):
            try:
                recovered_key = self.recover_pub_bytes_from_signature(i, sig, message_hash)
                if recovered_key and recovered_key == public_key_bytes:
                    rec_id = i
                    break
            except Exception:
                continue
        
        if rec_id == -1:
            raise RuntimeError("Could not construct a recoverable key. This should never happen.")
        
        # Set recovery ID (v = rec_id + 27 for Ethereum format)
        sig.v = rec_id + 27
        return sig

    @staticmethod
    def recover_pub_bytes_from_signature(rec_id: int, sig: ECDSASignature, message_hash: bytes) -> Optional[bytes]:
        """Recover public key bytes from signature using recovery ID"""
        if not ETH_KEYS_AVAILABLE:
            raise NotImplementedError("Key recovery requires eth_keys library. Install with: pip install eth-keys")
        
        # Convert signature to eth_keys format
        # eth_keys expects signature as 65 bytes: r (32) + s (32) + v (1)
        # Create signature bytes with the recovery ID (v = rec_id + 27 for Ethereum format)
        r_bytes = sig.r.to_bytes(32, "big")
        s_bytes = sig.s.to_bytes(32, "big")
        v = rec_id + 27
        signature_bytes = r_bytes + s_bytes + bytes([v])
        
        # Create eth_keys signature object
        try:
            eth_sig = keys.Signature(signature_bytes)
        except Exception:
            return None
        
        # Recover public key
        try:
            recovered_pub_key = eth_sig.recover_public_key_from_msg_hash(message_hash)
            # Get uncompressed public key bytes
            # eth_keys.PublicKey.to_bytes() returns 64 bytes (without 0x04 prefix)
            pub_bytes = recovered_pub_key.to_bytes()
            # Ensure we return 64 bytes (eth_keys already returns without prefix)
            if len(pub_bytes) == 65 and pub_bytes[0] == 0x04:
                return pub_bytes[1:]
            elif len(pub_bytes) == 64:
                return pub_bytes
            else:
                # Unexpected format, try to normalize
                return pub_bytes[-64:] if len(pub_bytes) >= 64 else None
        except Exception:
            return None

    @staticmethod
    def verify(data: bytes, signature: ECDSASignature, pub: bytes) -> bool:
        """Verify signature against message hash using public key bytes"""
        if len(data) != 32:
            raise ValueError(f"Expected 32 byte message hash, got {len(data)}")
        
        # Try eth_keys verification first if available (more compatible)
        if ETH_KEYS_AVAILABLE:
            try:
                # Create eth_keys public key (expects 64 bytes without 0x04 prefix)
                if len(pub) == 65 and pub[0] == 0x04:
                    pub_64 = pub[1:]
                elif len(pub) == 64:
                    pub_64 = pub
                else:
                    raise ValueError(f"Invalid public key length: {len(pub)}")
                eth_pub_key = keys.PublicKey(pub_64)
                
                # Create eth_keys signature
                r_bytes = signature.r.to_bytes(32, "big")
                s_bytes = signature.s.to_bytes(32, "big")
                # Extract recovery ID from v (v = rec_id + 27, but eth_keys expects 0-3)
                if signature.v >= 27:
                    rec_id = signature.v - 27
                else:
                    rec_id = signature.v
                # eth_keys.Signature expects v in range 0-3, not 27-30
                sig_bytes = r_bytes + s_bytes + bytes([rec_id])
                eth_sig = keys.Signature(sig_bytes)
                
                # Verify using eth_keys
                return eth_pub_key.verify_msg_hash(data, eth_sig)
            except Exception:
                pass  # Fall back to cryptography
        
        # Fallback to cryptography library
        try:
            # Reconstruct public key from bytes
            # Add 0x04 prefix if not present (uncompressed format)
            if len(pub) == 64:
                pub_with_prefix = bytes([0x04]) + pub
            else:
                pub_with_prefix = pub
            
            # Create public key object
            public_key = serialization.load_der_public_key(
                serialization.Encoding.X962,
                pub_with_prefix,
                backend=default_backend()
            )
            
            # Convert signature to DER format for verification
            der_sig = ECKey._signature_to_der(signature.r, signature.s)
            
            # Verify signature with prehashed (data is already a hash)
            public_key.verify(der_sig, data, ec.ECDSA(asym_utils.Prehashed(hashes.SHA256())))
            return True
        except Exception:
            return False

    @staticmethod
    def _signature_to_der(r: int, s: int) -> bytes:
        """Convert r and s to DER-encoded signature"""
        # Convert to bytes (32 bytes each, remove leading zeros)
        r_bytes = r.to_bytes(32, "big").lstrip(b'\x00')
        s_bytes = s.to_bytes(32, "big").lstrip(b'\x00')
        
        # Ensure at least 1 byte
        if len(r_bytes) == 0:
            r_bytes = b'\x00'
        if len(s_bytes) == 0:
            s_bytes = b'\x00'
        
        # Add leading zero if high bit is set (DER requirement)
        if r_bytes[0] & 0x80:
            r_bytes = b'\x00' + r_bytes
        if s_bytes[0] & 0x80:
            s_bytes = b'\x00' + s_bytes
        
        # Build DER structure: SEQUENCE { INTEGER r, INTEGER s }
        der = bytearray()
        der.append(0x30)  # SEQUENCE
        der.append(2 + len(r_bytes) + 2 + len(s_bytes))  # Length
        der.append(0x02)  # INTEGER
        der.append(len(r_bytes))
        der.extend(r_bytes)
        der.append(0x02)  # INTEGER
        der.append(len(s_bytes))
        der.extend(s_bytes)
        
        return bytes(der)

    def verify_signature(self, data: bytes, signature: bytes) -> bool:
        """Verify DER-encoded signature"""
        # Parse DER signature
        sig = ECDSASignature.decode_from_der(signature)
        pub = self.get_public_key_bytes(compressed=False)
        if pub[0] == 0x04:
            pub = pub[1:]
        return ECKey.verify(data, sig, pub)

    def verify_signature_obj(self, data: bytes, signature: ECDSASignature) -> bool:
        """Verify signature object"""
        pub = self.get_public_key_bytes(compressed=False)
        if pub[0] == 0x04:
            pub = pub[1:]
        return ECKey.verify(data, signature, pub)

    @staticmethod
    def signature_to_key_bytes(message_hash: bytes, signature_base64: str) -> bytes:
        """Recover public key bytes from base64-encoded signature"""
        try:
            signature_bytes = base64.b64decode(signature_base64)
        except Exception as e:
            raise ValueError(f"Could not decode base64: {e}")
        
        if len(signature_bytes) < 65:
            raise ValueError(f"Signature truncated, expected 65 bytes and got {len(signature_bytes)}")
        
        # Parse signature: r (32 bytes) + s (32 bytes) + v (1 byte)
        # This matches the format from to_base64()
        r_bytes = signature_bytes[0:32]
        s_bytes = signature_bytes[32:64]
        v = signature_bytes[64]
        
        sig = ECDSASignature.from_components(r_bytes, s_bytes, v)
        return ECKey.signature_to_key_bytes_from_sig(message_hash, sig)

    @staticmethod
    def signature_to_key_bytes_from_sig(message_hash: bytes, sig: ECDSASignature) -> bytes:
        """Recover public key bytes from signature object"""
        if len(message_hash) != 32:
            raise ValueError(f"messageHash argument has length {len(message_hash)}")
        
        header = sig.v
        # The header byte: 0x1B = first key with even y, 0x1C = first key with odd y,
        #                  0x1D = second key with even y, 0x1E = second key with odd y
        if header < 27 or header > 34:
            raise ValueError(f"Header byte out of range: {header}")
        
        if header >= 31:
            header -= 4
        
        rec_id = header - 27
        # Ensure rec_id is in valid range (0-3)
        if rec_id < 0 or rec_id > 3:
            raise ValueError(f"Invalid recovery ID: {rec_id} (from header {sig.v})")
        
        key_bytes = ECKey.recover_pub_bytes_from_signature(rec_id, sig, message_hash)
        
        if key_bytes is None:
            raise ValueError("Could not recover public key from signature")
        
        return key_bytes

    @staticmethod
    def signature_to_address(message_hash: bytes, signature_base64: str) -> bytes:
        """Compute address from signature"""
        key_bytes = ECKey.signature_to_key_bytes(message_hash, signature_base64)
        return ECKey.compute_address(key_bytes)

    @staticmethod
    def signature_to_address_from_sig(message_hash: bytes, sig: ECDSASignature) -> bytes:
        """Compute address from signature object"""
        key_bytes = ECKey.signature_to_key_bytes_from_sig(message_hash, sig)
        return ECKey.compute_address(key_bytes)

    @classmethod
    def signature_to_key(cls, message_hash: bytes, signature_base64: str) -> "ECKey":
        """Recover ECKey from signature"""
        key_bytes = cls.signature_to_key_bytes(message_hash, signature_base64)
        return cls.from_public_only(key_bytes)

    @classmethod
    def signature_to_key_from_sig(cls, message_hash: bytes, sig: ECDSASignature) -> "ECKey":
        """Recover ECKey from signature object"""
        key_bytes = cls.signature_to_key_bytes_from_sig(message_hash, sig)
        return cls.from_public_only(key_bytes)

    @staticmethod
    def compute_address(public_key_bytes: bytes) -> bytes:
        """Compute Ethereum-style address from public key bytes"""
        # Remove 0x04 prefix if present
        if len(public_key_bytes) == 65 and public_key_bytes[0] == 0x04:
            public_key_bytes = public_key_bytes[1:]
        elif len(public_key_bytes) == 64:
            pass  # Already correct
        else:
            raise ValueError(f"Invalid public key length: {len(public_key_bytes)}")
        
        # Hash with Keccak-256
        k = keccak.new(digest_bits=256)
        k.update(public_key_bytes)
        hash_bytes = k.digest()
        
        # Return last 20 bytes
        return hash_bytes[-20:]

    @classmethod
    def from_public_only(cls, public_key_bytes: bytes) -> "ECKey":
        """Create ECKey from public key bytes only (no private key)"""
        # Add 0x04 prefix if not present
        if len(public_key_bytes) == 64:
            public_key_bytes = bytes([0x04]) + public_key_bytes
        
        # Load public key
        public_key = serialization.load_der_public_key(
            public_key_bytes,
            backend=default_backend()
        )
        
        instance = cls.__new__(cls)
        instance._private_key = None
        instance._public_key = public_key
        return instance

    def get_address(self) -> bytes:
        """Get Ethereum-style address (last 20 bytes of Keccak-256 hash of public key)"""
        public_key_bytes = self.get_public_key_bytes(compressed=False)
        # Remove the 0x04 prefix if present
        if public_key_bytes[0] == 0x04:
            public_key_bytes = public_key_bytes[1:]
        # Hash with Keccak-256
        k = keccak.new(digest_bits=256)
        k.update(public_key_bytes)
        hash_bytes = k.digest()
        # Return last 20 bytes
        return hash_bytes[-20:]

