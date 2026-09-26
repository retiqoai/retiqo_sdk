# Copyright 2026 Loreum Digital Inc
# SPDX-License-Identifier: Apache-2.0
"""
TransportProvider - abstract transport provider interface
"""
from abc import ABC, abstractmethod
from typing import Optional


class TransportProvider(ABC):
    """Abstract transport provider"""

    @abstractmethod
    async def connect(self) -> None:
        """Connect to transport"""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from transport"""
        pass

    @abstractmethod
    async def send(self, data: bytes) -> None:
        """Send data"""
        pass

    @abstractmethod
    async def recv(self) -> bytes:
        """Receive data"""
        pass

    @abstractmethod
    def get_keep_alive_emitter(self) -> Optional["KeepAlive"]:
        """Get keep-alive emitter"""
        pass

    class KeepAlive(ABC):
        """Keep-alive interface"""

        @abstractmethod
        async def emit(self) -> None:
            """Emit keep-alive"""
            pass

