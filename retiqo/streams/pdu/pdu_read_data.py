# Copyright 2026 Loreum Digital Inc
# SPDX-License-Identifier: Apache-2.0
"""
PDU Read Data - for reading response PDUs
"""
from typing import Optional, Any
from retiqo.streams.base import Base, BaseConstants
from retiqo.streams.pdu.pdu_type import PDU_S_Type
from retiqo.streams.deserializing_stream import DeserializingStream
import io


class PDUReadData:
    """Container for PDU read data classes"""
    pass


class PDU_S_ReadType:
    """Base class for read PDUs"""

    def __init__(self, pdu: int):
        """Initialize with PDU type"""
        self.pdu = pdu
        self.seq_number = 0


class PDU_S_InvokeReqData(PDU_S_ReadType):
    """Invoke request data"""

    def __init__(self):
        """Initialize invoke request"""
        super().__init__(PDU_S_Type.PDU_S_InvokeReq)
        self.method_id = 0
        self.tc_in = BaseConstants.TC_VOID
        self.tc_out = BaseConstants.TC_VOID
        self.obj: Optional[Any] = None

    def set_method_id(self, method_id: int) -> None:
        """Set method ID"""
        self.method_id = method_id

    def set_seq_number(self, seq_number: int) -> None:
        """Set sequence number"""
        self.seq_number = seq_number

    def set_tc_in(self, tc_in: int) -> None:
        """Set input type code"""
        self.tc_in = tc_in

    def set_tc_out(self, tc_out: int) -> None:
        """Set output type code"""
        self.tc_out = tc_out

    def set_object(self, obj: Any) -> None:
        """Set object"""
        self.obj = obj

    def pack(self) -> bytes:
        """Pack into bytes"""
        from retiqo.streams.marshaller import Marshaller

        if self.tc_in == BaseConstants.TC_VOID:
            return Marshaller.pack_void(self.seq_number, self.method_id, self.tc_in, self.tc_out)
        else:
            return Marshaller.pack_object(self.seq_number, self.method_id, self.tc_in, self.tc_out, self.obj)

