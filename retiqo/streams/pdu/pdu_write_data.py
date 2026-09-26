# Copyright 2026 Loreum Digital Inc
# SPDX-License-Identifier: Apache-2.0
"""
PDU Write Data - for encoding response PDUs
"""
from typing import Optional, List, Any
from retiqo.streams.base import Base, BaseConstants
from retiqo.streams.pdu.pdu_type import PDU_S_Type
from retiqo.streams.serializing_stream import SerializingStream
import io


class PDU_S_WriteType:
    """Base class for write PDUs"""

    def __init__(self, pdu: int):
        """Initialize with PDU type"""
        self.pdu = pdu
        self.seq_number = 0


class PDUWriteData:
    """PDU Write Data factory"""

    @staticmethod
    def parse(data: bytes) -> Optional[PDU_S_WriteType]:
        """Parse PDU from bytes"""
        if len(data) < 1:
            return None

        pdu = data[0]
        if pdu == PDU_S_Type.PDU_S_InvokeRes:
            return PDU_S_InvokeResData.from_bytes(data)
        elif pdu == PDU_S_Type.PDU_S_ConnectRes:
            return PDU_S_ConnectResData.from_bytes(data)
        elif pdu == PDU_S_Type.PDU_S_DisconnectRes:
            return PDU_S_DisconnectResData.from_bytes(data)
        # Add more PDU types as needed
        return None


class PDU_S_InvokeResData(PDU_S_WriteType):
    """Invoke response data"""

    def __init__(self):
        """Initialize invoke response"""
        super().__init__(PDU_S_Type.PDU_S_InvokeRes)
        self.result = BaseConstants.RZ_OK
        self.obj: Optional[List[Any]] = None

    @classmethod
    def from_bytes(cls, data: bytes) -> "PDU_S_InvokeResData":
        """Create from bytes"""
        instance = cls()
        if len(data) >= 5:
            from retiqo.streams.deserializing_stream import DeserializingStream

            stream = DeserializingStream(data[1:])  # Skip PDU
            instance.seq_number = stream.read_short()
            instance.result = stream.read_short()
            if stream.remaining() > 0:
                instance.obj = stream.read_object()
        return instance

    def get_result(self) -> int:
        """Get result code"""
        return self.result

    def get_seq_number(self) -> int:
        """Get sequence number"""
        return self.seq_number

    def get_object(self) -> Optional[List[Any]]:
        """Get object"""
        return self.obj


class PDU_S_ConnectResData(PDU_S_WriteType):
    """Connect response data"""

    def __init__(self):
        """Initialize connect response"""
        super().__init__(PDU_S_Type.PDU_S_ConnectRes)
        self.result = BaseConstants.RZ_FAILED_INVALIDLOGIN

    @classmethod
    def from_bytes(cls, data: bytes) -> "PDU_S_ConnectResData":
        """Create from bytes"""
        instance = cls()
        if len(data) >= 5:
            from retiqo.streams.deserializing_stream import DeserializingStream

            stream = DeserializingStream(data[1:])  # Skip PDU
            instance.seq_number = stream.read_short()
            instance.result = stream.read_short()
        return instance


class PDU_S_DisconnectResData(PDU_S_WriteType):
    """Disconnect response data"""

    def __init__(self):
        """Initialize disconnect response"""
        super().__init__(PDU_S_Type.PDU_S_DisconnectRes)
        self.result = BaseConstants.RZ_OK

    @classmethod
    def from_bytes(cls, data: bytes) -> "PDU_S_DisconnectResData":
        """Create from bytes"""
        instance = cls()
        if len(data) >= 5:
            from retiqo.streams.deserializing_stream import DeserializingStream

            stream = DeserializingStream(data[1:])  # Skip PDU
            instance.seq_number = stream.read_short()
            instance.result = stream.read_short()
        return instance

