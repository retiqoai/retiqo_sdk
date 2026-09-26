# Copyright 2026 Loreum Digital Inc
# SPDX-License-Identifier: Apache-2.0
"""
Device provisioning utilities
"""
import asyncio
import websockets
import json
from typing import Tuple, Optional
from retiqo.ws.message import ProvisioningRequest, ProvisioningResult


async def provision_device(server_url: str, app_id: str, device_id: str) -> Tuple[str, bytes]:
    """
    Provision a device and return (device_address, private_key)
    
    Device generates its own private key and sends the public key (address) to the host.
    Device also generates sealed secret in its enclave and sends it to the host.
    The host stores the address and sealed secret and returns the address in the response.
    
    Args:
        server_url: WebSocket server URL (e.g., "ws://localhost:8080/ws")
        app_id: Application ID
        device_id: Device ID
        
    Returns:
        Tuple of (device_address_hex, private_key_bytes)
        
    Raises:
        Exception: If provisioning fails
    """
    from retiqo.crypto.ec_key import ECKey
    
    websocket = None
    try:
        # Generate device key pair on client side
        ec_key = ECKey()
        private_key = ec_key.private_key_bytes
        device_address = ec_key.address.hex()
        
        # Generate sealed secret in enclave (if enclave is available)
        # For now, we'll generate a placeholder - in production, this should be generated in the enclave
        sealed_secret_hex = None
        try:
            # TODO: Initialize enclave and call InitializeKeys to generate sealed secret
            # For now, we'll skip this and make it optional
            # sealed_secret = generate_sealed_secret_in_enclave()
            # sealed_secret_hex = sealed_secret.hex()
            pass
        except Exception as e:
            # Enclave not available or initialization failed - sealed secret is optional for now
            print(f"Warning: Could not generate sealed secret: {e}")
        
        # Connect to WebSocket for provisioning
        websocket = await websockets.connect(server_url, open_timeout=10)
        
        # Send provisioning request with device address (public key) and sealed secret
        provision_request = ProvisioningRequest(app_id, device_id)
        provision_request.data.deviceAddress = device_address
        if sealed_secret_hex:
            provision_request.data.sealedSecret = sealed_secret_hex
        request_json = json.dumps(provision_request.to_dict())
        await websocket.send(request_json.encode('utf-8'))
        
        # Wait for provisioning response
        response = await websocket.recv()
        if isinstance(response, bytes):
            response_str = response.decode('utf-8')
        elif isinstance(response, str):
            response_str = response
        else:
            raise Exception("Unexpected response type from provisioning")
        
        result_dict = json.loads(response_str)
        
        # Check if it's an error result
        if result_dict.get("type") == "error":
            error_data = result_dict.get("data", {})
            error_status = error_data.get("status", 0)
            error_desc = error_data.get("description", "Unknown error")
            raise Exception(f"Provisioning failed: {error_desc} (status: {error_status})")
        
        provision_result = ProvisioningResult.from_dict(result_dict)
        
        if provision_result.status != 0:
            raise Exception(f"Provisioning failed: {provision_result.description}")
        
        # Verify the address returned by host matches what we sent
        # Try both camelCase and lowercase (server may return either)
        returned_address = provision_result.data.get("devAddress") or provision_result.data.get("devaddress")
        
        if not returned_address:
            raise Exception(f"Provisioning result missing device address. Data: {provision_result.data}")
        
        if returned_address.lower() != device_address.lower():
            raise Exception(f"Device address mismatch. Expected: {device_address}, Got: {returned_address}")
        
        # Return the address and private key (private key was generated on device, not from server)
        return (device_address, private_key)
    finally:
        if websocket:
            try:
                await websocket.close()
            except Exception:
                pass

