# Copyright 2026 Loreum Digital Inc
# SPDX-License-Identifier: Apache-2.0
"""
AsyncHandler - async I/O handler for transport
"""
import asyncio
from typing import Optional, Dict
from retiqo.transport.transport_provider import TransportProvider


class AsyncHandler:
    """Async handler for transport I/O"""

    def __init__(self, transport_provider: TransportProvider):
        """Initialize async handler"""
        self._provider = transport_provider
        self._is_closed = False
        self._pending_requests: Dict[int, asyncio.Future] = {}
        self._callback_queue: asyncio.Queue = asyncio.Queue()
        self._sequence = 0
        import uuid
        self._handler_id = str(uuid.uuid4())[:8]  # Unique ID for debugging
        self._message_router_task: Optional[asyncio.Task] = None

    async def open(self) -> bool:
        """Open handler"""
        if self._provider:
            # Check if provider is already connected
            if hasattr(self._provider, 'is_connected') and self._provider.is_connected():
                # Start message router task
                self._start_message_router()
                return True
            # If provider has a connect method, call it (should take no args now)
            if hasattr(self._provider, 'connect'):
                import inspect
                sig = inspect.signature(self._provider.connect)
                # Connect should take no args (provisioning is separate)
                if len(sig.parameters) == 0:
                    await self._provider.connect()
                    # Start message router task after connection
                    self._start_message_router()
                # Otherwise assume it's already connected (was called externally)
                else:
                    self._start_message_router()
            return True
        return False
    
    def _start_message_router(self) -> None:
        """Start background task to route messages to callbacks or pending requests"""
        if self._message_router_task is None:
            self._message_router_task = asyncio.create_task(self._message_router_loop())
    
    async def _message_router_loop(self) -> None:
        """Background loop to continuously route messages from provider to callbacks or pending requests"""
        while not self._is_closed and self._provider:
            try:
                # Read from provider with timeout
                raw_response = await asyncio.wait_for(self._provider.recv(), timeout=1.0)
                
                # Server sends: [8-byte length] + [PDU data]
                if len(raw_response) < 9:
                    continue  # Invalid response, skip
                
                # Extract length header
                from retiqo.streams.base import Base
                packet_length = Base.extract_long(raw_response, 0)
                if packet_length > len(raw_response) - 8:
                    continue  # Invalid packet length, skip
                
                # Extract PDU data (skip 8-byte length header)
                pdu_data = raw_response[8:8+packet_length]
                
                # Parse sequence number from PDU data
                if len(pdu_data) < 5:
                    continue  # Invalid PDU data, skip
                
                from retiqo.streams.deserializing_stream import DeserializingStream
                resp_stream = DeserializingStream(pdu_data[1:])  # Skip PDU byte
                resp_seq = resp_stream.read_short()
                
                # Check if this matches a pending request
                if resp_seq in self._pending_requests:
                    # Route to pending request
                    future = self._pending_requests[resp_seq]
                    if not future.done():
                        future.set_result(raw_response)
                else:
                    # No matching request - it's a callback
                    self._handle_callback(raw_response)
            except asyncio.TimeoutError:
                # Timeout is expected - continue polling
                continue
            except Exception as e:
                # Handle "Not connected" errors gracefully - provider may be disconnecting
                if "Not connected" in str(e) or "not connected" in str(e).lower():
                    if not self._is_closed:
                        # Provider disconnected unexpectedly - exit loop
                        break
                    # Already closed, just exit
                    break
                if not self._is_closed:
                    print(f"Error in message router loop: {e}")
                    import traceback
                    traceback.print_exc()
                # Continue anyway
                continue

    async def close(self) -> None:
        """Close handler"""
        self._is_closed = True
        # Cancel message router task
        if self._message_router_task:
            self._message_router_task.cancel()
            try:
                await self._message_router_task
            except asyncio.CancelledError:
                pass
            self._message_router_task = None
        if self._provider:
            await self._provider.disconnect()

    def is_closed(self) -> bool:
        """Check if closed"""
        return self._is_closed

    async def send_recv(self, data: bytes, timeout: float = 120.0) -> Optional[bytes]:
        """Send data and wait for response"""
        if self._is_closed:
            raise IOError("Handler is closed")

        if not self._provider:
            raise IOError("Provider not available")

        # Extract sequence number from request (skip 8-byte length header)
        # Request format: [8-byte length] + [PDU (1 byte)] + [seq (2 bytes)] + [method_id (1 byte)] + [object data...]
        if len(data) < 12:
            raise IOError(f"Invalid request: too short ({len(data)} bytes)")

        from retiqo.streams.deserializing_stream import DeserializingStream
        # Skip 8-byte length header and PDU byte
        stream = DeserializingStream(data[9:])  # Skip [8-byte length] + [PDU byte]
        request_seq = stream.read_short()

        # Create future for response
        future = asyncio.Future()
        self._pending_requests[request_seq] = future

        try:
            # Send data
            await self._provider.send(data)

            # Poll for response by reading from provider and matching sequence numbers
            start_time = asyncio.get_event_loop().time() if hasattr(asyncio.get_event_loop(), 'time') else None
            import time
            if start_time is None:
                start_time = time.time()
            
            while True:
                # Check timeout
                elapsed = (asyncio.get_event_loop().time() if hasattr(asyncio.get_event_loop(), 'time') else time.time()) - start_time
                if elapsed >= timeout:
                    raise IOError("Timeout waiting for response")
                
                # Try to get response with short timeout to allow checking
                try:
                    raw_response = await asyncio.wait_for(self._provider.recv(), timeout=min(0.1, timeout - elapsed))
                    
                    # Server sends: [8-byte length] + [PDU data]
                    if len(raw_response) < 9:
                        continue  # Invalid response, skip
                    
                    # Extract length header
                    from retiqo.streams.base import Base
                    packet_length = Base.extract_long(raw_response, 0)
                    if packet_length > len(raw_response) - 8:
                        continue  # Invalid packet length, skip
                    
                    # Extract PDU data (skip 8-byte length header)
                    pdu_data = raw_response[8:8+packet_length]
                    
                    # Parse sequence number from PDU data
                    if len(pdu_data) < 5:
                        continue  # Invalid PDU data, skip
                    
                    from retiqo.streams.deserializing_stream import DeserializingStream
                    resp_stream = DeserializingStream(pdu_data[1:])  # Skip PDU byte
                    resp_seq = resp_stream.read_short()
                    
                    # Check if this matches our request
                    if resp_seq == request_seq:
                        # Found matching response
                        return raw_response
                    elif resp_seq in self._pending_requests:
                        # It's for another pending request - set its future
                        other_future = self._pending_requests[resp_seq]
                        if not other_future.done():
                            other_future.set_result(raw_response)
                        # Continue waiting for our response
                        continue
                    else:
                        # It's a callback - handle it and continue waiting
                        self._handle_callback(raw_response)
                        continue
                except asyncio.TimeoutError:
                    # Short timeout expired, check if future was set (shouldn't happen in this design)
                    if future.done():
                        return future.result()
                    # Continue polling
                    continue
        except asyncio.TimeoutError:
            self._pending_requests.pop(request_seq, None)
            raise IOError("Timeout waiting for response")
        finally:
            self._pending_requests.pop(request_seq, None)

    def _get_next_sequence(self) -> int:
        """Get next sequence number"""
        self._sequence = (self._sequence + 1) & 0x7FFF
        return self._sequence

    def _handle_response(self, data: bytes, request_id: int) -> None:
        """Handle incoming response"""
        if request_id in self._pending_requests:
            future = self._pending_requests[request_id]
            if not future.done():
                future.set_result(data)

    async def recv_callback(self, timeout: Optional[float] = None) -> Optional[bytes]:
        """Receive callback (non-blocking)"""
        try:
            if timeout:
                return await asyncio.wait_for(self._callback_queue.get(), timeout=timeout)
            else:
                return await self._callback_queue.get()
        except asyncio.TimeoutError:
            return None

    def _handle_callback(self, data: bytes) -> None:
        """Handle incoming callback"""
        self._callback_queue.put_nowait(data)

    async def send(self, data: bytes) -> None:
        """Send data (delegates to provider)"""
        if self._provider:
            await self._provider.send(data)
        else:
            raise IOError("Provider not available")

    async def recv(self, timeout: Optional[float] = None) -> bytes:
        """Receive data and match to pending request"""
        if self._provider:
            # Get raw bytes from provider
            response_bytes = await self._provider.recv()
            
            # Parse sequence number from response
            # Response format: [PDU (1 byte)] [seq (2 bytes)] [result (2 bytes)] [object data...]
            if len(response_bytes) < 5:
                raise IOError("Invalid response: too short")
            
            from retiqo.streams.deserializing_stream import DeserializingStream
            stream = DeserializingStream(response_bytes[1:])  # Skip PDU byte
            seq_number = stream.read_short()
            
            # Match to pending request
            if seq_number in self._pending_requests:
                future = self._pending_requests[seq_number]
                if not future.done():
                    future.set_result(response_bytes)
                    # Wait a bit for the future to be set
                    await asyncio.sleep(0)
                    return response_bytes
                else:
                    # Future already done, return the response
                    return response_bytes
            else:
                # No matching request, treat as callback
                self._handle_callback(response_bytes)
                # Recursively wait for the next response that matches
                return await self.recv(timeout)
        else:
            raise IOError("Provider not available")

