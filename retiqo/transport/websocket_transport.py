# Copyright 2026 Loreum Digital Inc
# SPDX-License-Identifier: Apache-2.0
"""
WebSocketTransportProvider - WebSocket-based transport for RTI
"""
import asyncio
import websockets
import json
from typing import Optional, Callable, Dict, Any
from retiqo.ws.message import Request, Result
from retiqo.crypto.ec_key import ECKey
from retiqo.transport.transport_provider import TransportProvider


class WebSocketTransportProvider(TransportProvider):
    """WebSocket transport provider for RTI"""

    def __init__(self, server_url: str, device_address: Optional[str] = None, private_key: Optional[bytes] = None):
        """Initialize with server URL and provisioned device credentials"""
        self._server_url = server_url
        self._websocket: Optional[websockets.WebSocketClientProtocol] = None
        self._connected = False
        self._channel_id: Optional[str] = None
        self._device_address: Optional[str] = device_address
        self._private_key: Optional[bytes] = private_key
        self._recv_queue: asyncio.Queue = asyncio.Queue()  # Queue for raw bytes payloads
        self._recv_task: Optional[asyncio.Task] = None
        self._send_lock = asyncio.Lock()  # Lock to serialize sends and prevent message corruption

    async def connect(self) -> str:
        """Connect to RTI server (device must be provisioned separately)"""
        if not self._device_address or not self._private_key:
            raise Exception("Device not provisioned. Call provision_device() first or provide device_address and private_key to __init__")
        
        # Connect to WebSocket
        try:
            self._websocket = await websockets.connect(self._server_url, open_timeout=10)
            self._connected = True
        except Exception as e:
            raise Exception(f"Failed to connect WebSocket: {e}")

        # Open channel BEFORE starting receive loop (to avoid recv() conflicts)
        channel_id = await self._open_channel()
        if not channel_id:
            raise Exception(f"Failed to open channel: channel_id is None or empty. Response may not contain channelid field.")
        self._channel_id = channel_id

        # Start receive loop after channel is open
        self._recv_task = asyncio.create_task(self._recv_loop())

        return channel_id

    async def _open_channel(self) -> str:
        """Open a channel"""
        from retiqo.ws.message import OpenChannelRequest, OpenChannelResult

        request = OpenChannelRequest(timeout=120000, channel_id="")
        request.sign(ECKey.from_private(self._private_key))
        
        # Send as text (JSON)
        request_json = json.dumps(request.to_dict())
        await self._websocket.send(request_json.encode('utf-8'))
        
        # Receive binary response
        response = await self._websocket.recv()
        if isinstance(response, bytes):
            response_str = response.decode('utf-8')
        else:
            response_str = response
        
        result_dict = json.loads(response_str)
        result = OpenChannelResult.from_dict(result_dict)
        
        # Check status - the response format has status in data.status, not at top level
        # If data.status exists, use it; otherwise use result.status
        status = result.data.get("status") if result.data and "status" in result.data else result.status
        if status is not None and status != 0:
            description = result.data.get("description", "") if result.data else result.description
            raise Exception(f"Failed to open channel (status={status}): {description}")
        
        # Field names are lowercase on the wire: channelId -> channelid
        channel_id = result.data.get("channelid") or result.data.get("channelId") if result.data else None
        if not channel_id:
            # Debug: log the actual response to help diagnose the issue
            import json as json_module
            raise Exception(f"Failed to get channel_id from response. Status: {status}, Data keys: {list(result.data.keys()) if result.data else 'None'}, Full data: {json_module.dumps(result.data) if result.data else 'None'}")
        return channel_id

    async def send_request(self, request: Request) -> Result:
        """Send a request and wait for response"""
        if not self._connected or self._websocket is None:
            raise Exception("Not connected")

        # Sign request if needed
        if hasattr(request, "sign") and self._private_key:
            request.sign(ECKey.from_private(self._private_key))

        # Send as binary
        request_json = json.dumps(request.to_dict())
        await self._websocket.send(request_json.encode('utf-8'))
        
        # Receive binary response
        response = await self._websocket.recv()
        if isinstance(response, bytes):
            response_str = response.decode('utf-8')
        else:
            response_str = response
        result_dict = json.loads(response_str)
        
        # Parse result based on request type
        from retiqo.ws.message import Result
        
        return Result.from_dict(result_dict)

    async def disconnect(self) -> None:
        """Disconnect from server"""
        if self._recv_task:
            self._recv_task.cancel()
            try:
                await self._recv_task
            except asyncio.CancelledError:
                pass
            self._recv_task = None

        if self._websocket:
            if self._channel_id:
                from retiqo.ws.message import CloseChannelRequest
                request = CloseChannelRequest(self._channel_id)
                await self.send_request(request)
            await self._websocket.close()
            self._websocket = None
        self._connected = False

    def is_connected(self) -> bool:
        """Check if connected"""
        return self._connected

    async def send(self, data: bytes) -> None:
        """Send raw bytes (for RTI protocol)
        
        Uses a lock to serialize sends and prevent message boundary corruption
        when multiple sends happen concurrently.
        """
        if not self._connected or not self._websocket:
            raise Exception("Not connected")
        
        if not self._channel_id:
            raise Exception("Channel not open. channel_id is None. Call connect() first.")

        # Serialize sends to prevent message boundary corruption
        # Even though WebSocket send is async, concurrent sends can cause
        # the backend to misread message boundaries, leading to corrupted length headers
        async with self._send_lock:
            # Wrap in PayloadRequest and sign it
            from retiqo.ws.message import PayloadRequest
            from retiqo.crypto.ec_key import ECKey
            request = PayloadRequest(self._channel_id, data)
            # Sign the request with the device's private key
            if self._private_key:
                ec_key = ECKey.from_private(self._private_key)
                request.sign(ec_key)
            # Send as text (JSON)
            request_json = json.dumps(request.to_dict())
            await self._websocket.send(request_json.encode('utf-8'))

    async def recv(self) -> bytes:
        """Receive raw bytes (for RTI protocol)"""
        if not self._connected:
            raise Exception("Not connected")

        # Wait for raw bytes from receive queue
        return await self._recv_queue.get()

    def get_keep_alive_emitter(self) -> Optional[TransportProvider.KeepAlive]:
        """Get keep-alive emitter"""
        return KeepAliveImpl(self)

    async def _recv_loop(self) -> None:
        """Receive loop for WebSocket messages - extracts payload and puts raw bytes in queue"""
        try:
            while self._connected and self._websocket:
                try:
                    message = await self._websocket.recv()
                    # Server sends binary messages
                    if isinstance(message, bytes):
                        message_str = message.decode('utf-8')
                        result_dict = json.loads(message_str)
                        
                        # Check if it's a PayloadResult and extract the payload bytes
                        from retiqo.ws.message import PayloadResult
                        if result_dict.get("type") == "payload":
                            result = PayloadResult.from_dict(result_dict)
                            if result.payload:
                                # Put raw bytes directly in queue for recv() to consume
                                await self._recv_queue.put(result.payload)
                            else:
                                print(f"Warning: PayloadResult has no payload")
                        else:
                            # For other message types (provisioning, open channel, etc.), 
                            # they're handled synchronously, so we can ignore them here
                            # or put them in a separate queue if needed
                            pass
                    elif isinstance(message, str):
                        result_dict = json.loads(message)
                        from retiqo.ws.message import PayloadResult
                        if result_dict.get("type") == "payload":
                            result = PayloadResult.from_dict(result_dict)
                            if result.payload:
                                await self._recv_queue.put(result.payload)
                except websockets.exceptions.ConnectionClosed:
                    break
                except Exception as e:
                    if self._connected:
                        print(f"Error processing message in receive loop: {e}")
                        import traceback
                        traceback.print_exc()
        except asyncio.CancelledError:
            pass
        except Exception as e:
            if self._connected:
                print(f"Error in receive loop: {e}")
                import traceback
                traceback.print_exc()


class KeepAliveImpl(TransportProvider.KeepAlive):
    """Keep-alive implementation"""

    def __init__(self, provider: WebSocketTransportProvider):
        self._provider = provider

    async def emit(self) -> None:
        """Emit keep-alive"""
        if self._provider._connected:
            from retiqo.ws.message import KeepAliveRequest
            request = KeepAliveRequest()
            # Send as binary
            request_json = json.dumps(request.to_dict())
            await self._provider._websocket.send(request_json.encode('utf-8'))

