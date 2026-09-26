# Copyright 2026 Loreum Digital Inc
# SPDX-License-Identifier: Apache-2.0
"""
RTI - Factory class for creating RTI instances
"""
from typing import Optional
from retiqo.rti.rti_surrogate import RTISurrogate
from retiqo.rti.rti_surrogate_impl import RTISurrogateImpl
from retiqo.rti.rti_surrogate_stub import RTISurrogateStub
from retiqo.transport.transport_provider import TransportProvider
from retiqo.transport.base_session import BaseSession


class RTI:
    """RTI factory class"""

    @staticmethod
    async def create_rti_surrogate_async(transport_provider: TransportProvider) -> Optional[RTISurrogate]:
        """Create RTI surrogate instance (async version)"""
        try:
            # Create session
            session = BaseSession(transport_provider)
            
            # Open session
            await session.open()
            
            # Verify session is open
            if not session.is_open():
                raise IOError("Failed to open session")

            # Create stub
            stub = RTISurrogateStub(session)

            # Create implementation
            surrogate = RTISurrogateImpl(stub)
            if surrogate:
                surrogate.start_callback_thread()

            return surrogate
        except Exception as e:
            print(f"Error creating RTI surrogate: {e}")
            import traceback
            traceback.print_exc()
            return None

    @staticmethod
    def create_rti_surrogate(transport_provider: TransportProvider) -> Optional[RTISurrogate]:
        """Create RTI surrogate instance (sync wrapper)"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is running, we can't use run_until_complete
                # Create a future and return None for now (caller should use async version)
                # This is a limitation - in async context, use create_rti_surrogate_async
                raise RuntimeError("Event loop is running. Use create_rti_surrogate_async() instead")
            else:
                return loop.run_until_complete(RTI.create_rti_surrogate_async(transport_provider))
        except Exception as e:
            print(f"Error creating RTI surrogate: {e}")
            import traceback
            traceback.print_exc()
            return None

    @staticmethod
    def destroy_rti_surrogate(rti_surrogate: RTISurrogate) -> None:
        """Destroy RTI surrogate instance"""
        if isinstance(rti_surrogate, RTISurrogateImpl):
            rti_surrogate.shutdown_callback_thread()
            # Close session
            stub = rti_surrogate.get_stub()
            if stub:
                session = stub.get_session()
                if session:
                    import asyncio
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        async def _close():
                            await session.close()
                        asyncio.create_task(_close())
                    else:
                        loop.run_until_complete(session.close())

