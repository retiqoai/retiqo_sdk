# Copyright 2026 Loreum Digital Inc
# SPDX-License-Identifier: Apache-2.0
"""
BaseSession - handles sending/receiving method calls
"""
import asyncio
from typing import List, Optional, Any
from retiqo.streams.base import BaseConstants, Base
from retiqo.streams.marshaller import Marshaller, MarshallerException
from retiqo.transport.async_handler import AsyncHandler
from retiqo.transport.transport_provider import TransportProvider
from retiqo.streams.pdu.pdu_type import PDU_S_Type


class BaseSession:
    """Base session for RTI communication"""

    VERSION = 1

    def __init__(self, transport_provider: TransportProvider):
        """Initialize base session"""
        self._is_session_open = False
        self._handler: Optional[AsyncHandler] = None
        self._sequence = 0
        self._handler = AsyncHandler(transport_provider)

    def get_handler(self) -> Optional[AsyncHandler]:
        """Get async handler"""
        return self._handler

    async def open(self) -> bool:
        """Open session"""
        if not self._is_session_open:
            if self._handler:
                self._is_session_open = await self._handler.open()
        return self._is_session_open

    async def close(self) -> bool:
        """Close session"""
        if self._is_session_open:
            if self._handler:
                await self._handler.close()
                self._is_session_open = False
        return True

    def is_open(self) -> bool:
        """Check if session is open"""
        return self._is_session_open

    def _get_next_seq(self) -> int:
        """Get next sequence number"""
        self._sequence = (self._sequence + 1) & 0x7FFF
        return self._sequence

    async def send_recv(
        self, method_id: int, obj_in: Optional[Any], tc_in: int, tc_out: int
    ) -> Optional[List[Any]]:
        """Send request and receive response"""
        obj_out = None

        if not self._is_session_open:
            raise IOError("Provider session not available")

        if not self._handler:
            raise IOError("Handler not available")

        current_seq = self._get_next_seq()

        # Pack request
        if tc_in == BaseConstants.TC_VOID:
            request_bytes = Marshaller.pack_void(current_seq, method_id, tc_in, tc_out)
        else:
            request_bytes = Marshaller.pack_object(current_seq, method_id, tc_in, tc_out, obj_in)

        if not request_bytes:
            raise MarshallerException("Failed to pack request")

        # Add PDU header
        pdu_packet = bytearray(len(request_bytes) + 1)
        pdu_packet[0] = PDU_S_Type.PDU_S_InvokeReq
        pdu_packet[1:] = request_bytes

        # Add 8-byte length header (server expects: [8-byte length] + [PDU data])
        packet_length = len(pdu_packet)
        final_packet = bytearray(8 + packet_length)
        Base.insert_long(final_packet, 0, packet_length)
        final_packet[8:] = pdu_packet

        # Send and receive
        if not self._handler:
            raise IOError("Handler not available")
        
        # Use send_recv to handle request-response matching
        response_bytes = await self._handler.send_recv(bytes(final_packet), timeout=120.0)

        if response_bytes:
            # Parse response - server sends: [8-byte length] + [PDU data]
            if len(response_bytes) < 9:
                raise MarshallerException("Invalid response: too short (need at least 8-byte length header)")

            # Extract length header (first 8 bytes)
            packet_length = Base.extract_long(response_bytes, 0)
            if packet_length > len(response_bytes) - 8:
                raise MarshallerException(f"Invalid response: packet length {packet_length} exceeds available data")

            # Extract PDU data (skip 8-byte length header)
            pdu_data = response_bytes[8:8+packet_length]
            
            if len(pdu_data) < 1:
                raise MarshallerException("Invalid response: no PDU data")

            pdu = pdu_data[0]
            if pdu != PDU_S_Type.PDU_S_InvokeRes:
                raise MarshallerException(f"Invalid PDU: expected {PDU_S_Type.PDU_S_InvokeRes}, got {pdu}")

            # Parse response data
            from retiqo.streams.deserializing_stream import DeserializingStream

            # Response format: [PDU (1 byte)] [seq (2 bytes)] [result (2 bytes)] [object data...]
            if len(pdu_data) < 5:
                raise MarshallerException("Invalid response: PDU data too short")

            stream = DeserializingStream(pdu_data[1:])  # Skip PDU byte
            seq_number = stream.read_short()
            result = stream.read_short()

            if seq_number != current_seq:
                raise MarshallerException(
                    f"Method execution returned incorrect sequence: {seq_number}. Current sequence: {current_seq}"
                )

            if result != BaseConstants.RZ_OK:
                raise MarshallerException(f"Method execution returned error: {result}")

            if tc_out != BaseConstants.TC_VOID:
                if stream.remaining() > 0:
                    obj_out = stream.read_object()

        return obj_out

    async def send_object_recv_object(
        self, method_id: int, obj_in: Optional[Any], is_primitive_obj_in: bool = False
    ) -> Optional[List[Any]]:
        """Send object and receive object"""
        tc_in = Marshaller.get_obj_type(obj_in)
        if is_primitive_obj_in:
            tc_in |= BaseConstants.TC_FLAG_PRIMITIVE
        return await self.send_recv(method_id, obj_in, tc_in, BaseConstants.TC_OBJECT)

    async def send_object_recv_void(
        self, method_id: int, obj_in: Optional[Any], is_primitive_obj_in: bool = False
    ) -> None:
        """Send object and receive void"""
        tc_in = Marshaller.get_obj_type(obj_in)
        if is_primitive_obj_in:
            tc_in |= BaseConstants.TC_FLAG_PRIMITIVE
        await self.send_recv(method_id, obj_in, tc_in, BaseConstants.TC_VOID)

    async def send_void_recv_object(self, method_id: int) -> Optional[List[Any]]:
        """Send void and receive object"""
        return await self.send_recv(method_id, None, BaseConstants.TC_VOID, BaseConstants.TC_OBJECT)

    async def send_void_recv_void(self, method_id: int) -> None:
        """Send void and receive void"""
        await self.send_recv(method_id, None, BaseConstants.TC_VOID, BaseConstants.TC_VOID)

