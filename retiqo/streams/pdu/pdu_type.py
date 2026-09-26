# Copyright 2026 Loreum Digital Inc
# SPDX-License-Identifier: Apache-2.0
"""PDU Type constants"""


class PDU_S_Type:
    """PDU Type constants"""

    PDU_S_ConnectReq = 0x01
    PDU_S_ConnectRes = 0x02
    PDU_S_DisconnectReq = 0x03
    PDU_S_DisconnectRes = 0x04

    PDU_S_CreateInstanceReq = 0x05
    PDU_S_CreateInstanceRes = 0x06
    PDU_S_DestroyInstanceReq = 0x07
    PDU_S_DestroyInstanceRes = 0x08

    PDU_S_InvokeReq = 0x20
    PDU_S_InvokeRes = 0x21

    PDU_S_KeepAlive = 0x80
    PDU_S_CallBack = 0x81

