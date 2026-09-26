# Copyright 2026 Loreum Digital Inc
# SPDX-License-Identifier: Apache-2.0
"""
RTISurrogateImpl - implementation that wraps stub and handles exceptions
"""
from typing import List, Optional, Any, TYPE_CHECKING
from retiqo.rti.rti_surrogate import RTISurrogate
from retiqo.rti.actor_surrogate import ActorSurrogate
from retiqo.rti.rti_surrogate_stub import RTISurrogateStub
from retiqo.rti.rti_exceptions import RTIExceptions
from retiqo.rti.attribute_handle_set import AttributeHandleSet
from retiqo.rti.actor_handle_set import ActorHandleSet
from retiqo.rti.region import Region
from retiqo.rti.supplied_attributes import SuppliedAttributes
from retiqo.rti.supplied_parameters import SuppliedParameters
from retiqo.streams.marshaller import Marshaller, MarshallerException
from retiqo.exceptions import *
import asyncio

if TYPE_CHECKING:
    from retiqo.streams.deserializing_stream import DeserializingStream


class RTISurrogateImpl(RTISurrogate, RTIExceptions):
    """RTI Surrogate Implementation"""

    def __init__(self, stub: RTISurrogateStub):
        """Initialize with stub"""
        self._stub = stub
        self._actor_reference: Optional[ActorSurrogate] = None
        self._callback_task: Optional[asyncio.Task] = None
        self._shutdown_flag = False

        # Exception message constants
        self._exception_marshaller_str = "MarshallerException occurred! "
        self._exception_io_str = "IOException occurred!"

    def get_stub(self) -> RTISurrogateStub:
        """Get stub"""
        return self._stub

    def get_actor_surrogate(self) -> Optional[ActorSurrogate]:
        """Get actor surrogate"""
        return self._actor_reference

    def start_callback_thread(self) -> None:
        """Start callback thread"""
        if self._callback_task is None:
            self._shutdown_flag = False
            self._callback_task = asyncio.create_task(self._callback_loop())

    def shutdown_callback_thread(self) -> None:
        """Shutdown callback thread"""
        self._shutdown_flag = True
        if self._callback_task:
            self._callback_task.cancel()
            try:
                asyncio.get_event_loop().run_until_complete(self._callback_task)
            except asyncio.CancelledError:
                pass
            self._callback_task = None

    def _handle_exception(self, v: Optional[List[Any]]) -> None:
        """Handle exception from response vector"""
        if v is None or len(v) == 0:
            return

        exception_code = v[0] if isinstance(v[0], int) else int(v[0])
        reason = v[1] if len(v) > 1 and v[1] is not None else ""

        if exception_code == RTIExceptions.Exception_Null:
            return

        # Map exception codes to exception classes
        exception_map = {
            RTIExceptions.Exception_StateChannelExecutionAlreadyExists: StateChannelExecutionAlreadyExists,
            RTIExceptions.Exception_CouldNotOpenSCD: CouldNotOpenSCD,
            RTIExceptions.Exception_ErrorReadingSCD: ErrorReadingSCD,
            RTIExceptions.Exception_RTIinternalError: RTIInternalError,
            RTIExceptions.Exception_ActorsCurrentlyJoined: ActorsCurrentlyJoined,
            RTIExceptions.Exception_StateChannelExecutionDoesNotExist: StateChannelExecutionDoesNotExist,
            RTIExceptions.Exception_ActorAlreadyExecutionMember: ActorAlreadyExecutionMember,
            RTIExceptions.Exception_SaveInProgress: SaveInProgress,
            RTIExceptions.Exception_RestoreInProgress: RestoreInProgress,
            RTIExceptions.Exception_ActorOwnsAttributes: ActorOwnsAttributes,
            RTIExceptions.Exception_ActorNotExecutionMember: ActorNotExecutionMember,
            RTIExceptions.Exception_InvalidResignAction: InvalidResignAction,
            RTIExceptions.Exception_ConsensusLabelNotAnnounced: ConsensusLabelNotAnnounced,
            RTIExceptions.Exception_ConsensusLabelOutstanding: ConsensusLabelOutstanding,
            RTIExceptions.Exception_ConsensusPointLabelWasNotAnnounced: ConsensusPointLabelWasNotAnnounced,
            RTIExceptions.Exception_SaveNotInitiated: SaveNotInitiated,
            RTIExceptions.Exception_RestoreNotRequested: RestoreNotRequested,
            RTIExceptions.Exception_SpecifiedSaveLabelDoesNotExist: SpecifiedSaveLabelDoesNotExist,
            RTIExceptions.Exception_CouldNotRestore: CouldNotRestore,
            RTIExceptions.Exception_UnableToPerformSave: UnableToPerformSave,
            RTIExceptions.Exception_ObjectClassNotDefined: ObjectClassNotDefined,
            RTIExceptions.Exception_AttributeNotDefined: AttributeNotDefined,
            RTIExceptions.Exception_OwnershipAcquisitionPending: OwnershipAcquisitionPending,
            RTIExceptions.Exception_InteractionClassNotDefined: InteractionClassNotDefined,
            RTIExceptions.Exception_InteractionClassNotPublished: InteractionClassNotPublished,
            RTIExceptions.Exception_ObjectClassNotPublished: ObjectClassNotPublished,
            RTIExceptions.Exception_ObjectClassNotSubscribed: ObjectClassNotSubscribed,
            RTIExceptions.Exception_InteractionClassNotSubscribed: InteractionClassNotSubscribed,
            RTIExceptions.Exception_ObjectNotKnown: ObjectNotKnown,
            RTIExceptions.Exception_AttributeNotKnown: AttributeNotKnown,
            RTIExceptions.Exception_AttributeNotOwned: AttributeNotOwned,
            RTIExceptions.Exception_InteractionClassNotKnown: InteractionClassNotKnown,
            RTIExceptions.Exception_InteractionParameterNotKnown: InteractionParameterNotKnown,
            RTIExceptions.Exception_RegionNotKnown: RegionNotKnown,
            RTIExceptions.Exception_RegionInUse: RegionInUse,
            RTIExceptions.Exception_InvalidRegionContext: InvalidRegionContext,
            RTIExceptions.Exception_InvalidExtents: InvalidExtents,
            RTIExceptions.Exception_DimensionNotDefined: DimensionNotDefined,
            RTIExceptions.Exception_SpaceNotDefined: SpaceNotDefined,
            RTIExceptions.Exception_AttributeAlreadyOwned: AttributeAlreadyOwned,
            RTIExceptions.Exception_AttributeAlreadyBeingAcquired: AttributeAlreadyBeingAcquired,
            RTIExceptions.Exception_AttributeAlreadyBeingDivested: AttributeAlreadyBeingDivested,
            RTIExceptions.Exception_AttributeAcquisitionWasNotRequested: AttributeAcquisitionWasNotRequested,
            RTIExceptions.Exception_AttributeAcquisitionWasNotCanceled: AttributeAcquisitionWasNotCanceled,
            RTIExceptions.Exception_AttributeDivestitureWasNotRequested: AttributeDivestitureWasNotRequested,
            RTIExceptions.Exception_ActorWasNotAskedToReleaseAttribute: ActorWasNotAskedToReleaseAttribute,
            RTIExceptions.Exception_ObjectAlreadyRegistered: ObjectAlreadyRegistered,
            RTIExceptions.Exception_ObjectClassNotKnown: ObjectClassNotKnown,
            RTIExceptions.Exception_AttributeNotPublished: AttributeNotPublished,
            RTIExceptions.Exception_NameNotFound: NameNotFound,
            RTIExceptions.Exception_EventNotKnown: EventNotKnown,
            RTIExceptions.Exception_CouldNotDiscover: CouldNotDiscover,
            RTIExceptions.Exception_CouldNotDecode: CouldNotDecode,
            RTIExceptions.Exception_DeleteRightNotHeld: DeleteRightNotHeld,
            RTIExceptions.Exception_TooManyActors: TooManyActors,
            RTIExceptions.Exception_UnimplementedService: UnimplementedService,
            RTIExceptions.Exception_AsynchronousDeliveryAlreadyEnabled: AsynchronousDeliveryAlreadyEnabled,
            RTIExceptions.Exception_AsynchronousDeliveryAlreadyDisabled: AsynchronousDeliveryAlreadyDisabled,
        }

        exception_class = exception_map.get(exception_code)
        if exception_class:
            raise exception_class(str(reason))
        else:
            raise RTIInternalError(f"Unknown exception code: {exception_code}, reason: {reason}")

    # State Channel Management Services

    async def create_state_channel_execution(self, execution_name: str, scd: str) -> None:
        """Create state channel execution"""
        try:
            v = await self._stub.create_state_channel_execution(execution_name, scd)
            self._handle_exception(v)
        except (IOError, OSError) as e:
            raise RTIInternalError(self._exception_io_str) from e
        except MarshallerException as e:
            raise RTIInternalError(self._exception_marshaller_str + str(e)) from e

    async def destroy_state_channel_execution(self, execution_name: str) -> None:
        """Destroy state channel execution"""
        try:
            v = await self._stub.destroy_state_channel_execution(execution_name)
            self._handle_exception(v)
        except (IOError, OSError) as e:
            raise RTIInternalError(self._exception_io_str) from e
        except MarshallerException as e:
            raise RTIInternalError(self._exception_marshaller_str + str(e)) from e

    async def get_state_channel_executions(self) -> List[str]:
        """Get state channel executions"""
        try:
            v = await self._stub.get_state_channel_executions()
            if v is None:
                return []

            exception_code = v[0] if isinstance(v[0], int) else int(v[0])
            if exception_code == RTIExceptions.Exception_RTIinternalError:
                reason = v[1] if len(v) > 1 and v[1] is not None else ""
                raise RTIInternalError(str(reason))
            elif exception_code == RTIExceptions.Exception_Null:
                executions = v[2] if len(v) > 2 else []
                return executions if isinstance(executions, list) else []
            else:
                self._handle_exception(v)
                return []
        except (IOError, OSError) as e:
            # Server may have BufferOverflowException when response is too large (>4KB)
            # This is a server-side limitation in IOCtxt.MAX_PERSOCKETIOCONTEXT_BUFF_SIZE
            if "BufferOverflow" in str(e) or "buffer" in str(e).lower():
                raise RTIInternalError(
                    "Server buffer overflow: response too large. "
                    "This may occur when there are many state channel executions (>100). "
                    "Server-side buffer limit is 4KB. Consider cleaning up old executions."
                ) from e
            raise RTIInternalError(self._exception_io_str) from e
        except MarshallerException as e:
            # Check if the error is related to buffer overflow
            if "BufferOverflow" in str(e) or "buffer" in str(e).lower():
                raise RTIInternalError(
                    "Server buffer overflow: response too large. "
                    "This may occur when there are many state channel executions (>100). "
                    "Server-side buffer limit is 4KB. Consider cleaning up old executions."
                ) from e
            raise RTIInternalError(self._exception_marshaller_str + str(e)) from e

    async def join_state_channel_execution(
        self,
        actor_type: str,
        state_channel_execution_name: str,
        public_key: bytes,
        actor_reference: ActorSurrogate,
    ) -> bytes:
        """Join state channel execution"""
        self._actor_reference = actor_reference

        try:
            v = await self._stub.join_state_channel_execution(actor_type, state_channel_execution_name, public_key)
            if v is None:
                raise RTIInternalError("No response from join")

            exception_code = v[0] if isinstance(v[0], int) else int(v[0])
            if exception_code == RTIExceptions.Exception_Null:
                result = v[2] if len(v) > 2 else None
                if result is None:
                    raise RTIInternalError("No result in join response")
                return result if isinstance(result, bytes) else bytes(result)
            else:
                self._handle_exception(v)
                raise RTIInternalError("Unexpected response format")
        except (IOError, OSError) as e:
            raise RTIInternalError(self._exception_io_str) from e
        except MarshallerException as e:
            raise RTIInternalError(self._exception_marshaller_str + str(e)) from e

    async def resign_state_channel_execution(self, resign_action: int) -> None:
        """Resign from state channel execution"""
        try:
            v = await self._stub.resign_state_channel_execution(resign_action)
            self._handle_exception(v)
            self._actor_reference = None
        except (IOError, OSError) as e:
            raise RTIInternalError(self._exception_io_str) from e
        except MarshallerException as e:
            raise RTIInternalError(self._exception_marshaller_str + str(e)) from e

    async def register_state_channel_consensus_point(
        self, consensus_point_label: str, user_supplied_tag: bytes
    ) -> None:
        """Register consensus point"""
        try:
            v = await self._stub.register_state_channel_consensus_point(consensus_point_label, user_supplied_tag)
            self._handle_exception(v)
        except (IOError, OSError) as e:
            raise RTIInternalError(self._exception_io_str) from e
        except MarshallerException as e:
            raise RTIInternalError(self._exception_marshaller_str + str(e)) from e

    async def register_state_channel_consensus_point_with_set(
        self,
        consensus_point_label: str,
        user_supplied_tag: bytes,
        consensus_set: ActorHandleSet,
    ) -> None:
        """Register consensus point with actor set"""
        try:
            consensus_list = list(consensus_set.to_list()) if consensus_set else []
            v = await self._stub.register_state_channel_consensus_point(
                consensus_point_label, user_supplied_tag, consensus_list
            )
            self._handle_exception(v)
        except (IOError, OSError) as e:
            raise RTIInternalError(self._exception_io_str) from e
        except MarshallerException as e:
            raise RTIInternalError(self._exception_marshaller_str + str(e)) from e

    async def consensus_point_achieved(
        self, consensus_point_label: str, consensus_hash: bytes, signature: bytes
    ) -> None:
        """Achieve consensus point"""
        try:
            v = await self._stub.consensus_point_achieved(consensus_point_label, consensus_hash, signature)
            self._handle_exception(v)
        except (IOError, OSError) as e:
            raise RTIInternalError(self._exception_io_str) from e
        except MarshallerException as e:
            raise RTIInternalError(self._exception_marshaller_str + str(e)) from e

    # Save/Restore Services

    async def request_state_channel_save(self, label: str) -> None:
        """Request state channel save"""
        try:
            v = await self._stub.request_state_channel_save(label)
            self._handle_exception(v)
        except (IOError, OSError) as e:
            raise RTIInternalError(self._exception_io_str) from e
        except MarshallerException as e:
            raise RTIInternalError(self._exception_marshaller_str + str(e)) from e

    async def request_state_channel_save_with_set(self, label: str, actor_set: ActorHandleSet) -> None:
        """Request state channel save for actor set"""
        try:
            actor_list = list(actor_set.to_list()) if actor_set else []
            v = await self._stub.request_state_channel_save(label, actor_list)
            self._handle_exception(v)
        except (IOError, OSError) as e:
            raise RTIInternalError(self._exception_io_str) from e
        except MarshallerException as e:
            raise RTIInternalError(self._exception_marshaller_str + str(e)) from e

    async def actor_save_begun(self) -> None:
        """Actor save begun"""
        try:
            v = await self._stub.actor_save_begun()
            self._handle_exception(v)
        except (IOError, OSError) as e:
            raise RTIInternalError(self._exception_io_str) from e
        except MarshallerException as e:
            raise RTIInternalError(self._exception_marshaller_str + str(e)) from e

    async def actor_save_complete(self) -> None:
        """Actor save complete"""
        try:
            v = await self._stub.actor_save_complete()
            self._handle_exception(v)
        except (IOError, OSError) as e:
            raise RTIInternalError(self._exception_io_str) from e
        except MarshallerException as e:
            raise RTIInternalError(self._exception_marshaller_str + str(e)) from e

    async def actor_save_not_complete(self) -> None:
        """Actor save not complete"""
        try:
            v = await self._stub.actor_save_not_complete()
            self._handle_exception(v)
        except (IOError, OSError) as e:
            raise RTIInternalError(self._exception_io_str) from e
        except MarshallerException as e:
            raise RTIInternalError(self._exception_marshaller_str + str(e)) from e

    async def request_state_channel_restore(self, label: str) -> None:
        """Request state channel restore"""
        try:
            v = await self._stub.request_state_channel_restore(label)
            self._handle_exception(v)
        except (IOError, OSError) as e:
            raise RTIInternalError(self._exception_io_str) from e
        except MarshallerException as e:
            raise RTIInternalError(self._exception_marshaller_str + str(e)) from e

    async def actor_restore_complete(self) -> None:
        """Actor restore complete"""
        try:
            v = await self._stub.actor_restore_complete()
            self._handle_exception(v)
        except (IOError, OSError) as e:
            raise RTIInternalError(self._exception_io_str) from e
        except MarshallerException as e:
            raise RTIInternalError(self._exception_marshaller_str + str(e)) from e

    async def actor_restore_not_complete(self) -> None:
        """Actor restore not complete"""
        try:
            v = await self._stub.actor_restore_not_complete()
            self._handle_exception(v)
        except (IOError, OSError) as e:
            raise RTIInternalError(self._exception_io_str) from e
        except MarshallerException as e:
            raise RTIInternalError(self._exception_marshaller_str + str(e)) from e

    # Declaration Management Services

    async def publish_object_class(self, the_class: int, attribute_list: AttributeHandleSet) -> None:
        """Publish object class"""
        try:
            attr_list = list(attribute_list.to_list()) if attribute_list else []
            v = await self._stub.publish_object_class(the_class, attr_list)
            self._handle_exception(v)
        except (IOError, OSError) as e:
            raise RTIInternalError(self._exception_io_str) from e
        except MarshallerException as e:
            raise RTIInternalError(self._exception_marshaller_str + str(e)) from e

    async def unpublish_object_class(self, the_class: int) -> None:
        """Unpublish object class"""
        try:
            v = await self._stub.unpublish_object_class(the_class)
            # Verify unpublish succeeded (no debug output needed for normal operation)
            self._handle_exception(v)
        except (IOError, OSError) as e:
            raise RTIInternalError(self._exception_io_str) from e
        except MarshallerException as e:
            raise RTIInternalError(self._exception_marshaller_str + str(e)) from e

    async def publish_interaction_class(self, the_interaction: int) -> None:
        """Publish interaction class"""
        try:
            v = await self._stub.publish_interaction_class(the_interaction)
            self._handle_exception(v)
        except (IOError, OSError) as e:
            raise RTIInternalError(self._exception_io_str) from e
        except MarshallerException as e:
            raise RTIInternalError(self._exception_marshaller_str + str(e)) from e

    async def unpublish_interaction_class(self, the_interaction: int) -> None:
        """Unpublish interaction class"""
        try:
            v = await self._stub.unpublish_interaction_class(the_interaction)
            self._handle_exception(v)
        except (IOError, OSError) as e:
            raise RTIInternalError(self._exception_io_str) from e
        except MarshallerException as e:
            raise RTIInternalError(self._exception_marshaller_str + str(e)) from e

    async def subscribe_object_class_attributes(
        self, the_class: int, attribute_list: AttributeHandleSet
    ) -> None:
        """Subscribe to object class attributes"""
        try:
            attr_list = list(attribute_list.to_list()) if attribute_list else []
            v = await self._stub.subscribe_object_class_attributes(the_class, attr_list)
            self._handle_exception(v)
        except (IOError, OSError) as e:
            raise RTIInternalError(self._exception_io_str) from e
        except MarshallerException as e:
            raise RTIInternalError(self._exception_marshaller_str + str(e)) from e

    async def subscribe_object_class_attributes_passively(
        self, the_class: int, attribute_list: AttributeHandleSet
    ) -> None:
        """Subscribe to object class attributes passively"""
        try:
            attr_list = list(attribute_list.to_list()) if attribute_list else []
            v = await self._stub.subscribe_object_class_attributes(the_class, attr_list, passively=True)
            self._handle_exception(v)
        except (IOError, OSError) as e:
            raise RTIInternalError(self._exception_io_str) from e
        except MarshallerException as e:
            raise RTIInternalError(self._exception_marshaller_str + str(e)) from e

    async def unsubscribe_object_class(self, the_class: int) -> None:
        """Unsubscribe from object class"""
        try:
            v = await self._stub.unsubscribe_object_class(the_class)
            self._handle_exception(v)
        except (IOError, OSError) as e:
            raise RTIInternalError(self._exception_io_str) from e
        except MarshallerException as e:
            raise RTIInternalError(self._exception_marshaller_str + str(e)) from e

    async def subscribe_interaction_class(self, the_class: int) -> None:
        """Subscribe to interaction class"""
        try:
            v = await self._stub.subscribe_interaction_class(the_class)
            self._handle_exception(v)
        except (IOError, OSError) as e:
            raise RTIInternalError(self._exception_io_str) from e
        except MarshallerException as e:
            raise RTIInternalError(self._exception_marshaller_str + str(e)) from e

    async def subscribe_interaction_class_passively(self, the_class: int) -> None:
        """Subscribe to interaction class passively"""
        try:
            v = await self._stub.subscribe_interaction_class(the_class, passively=True)
            self._handle_exception(v)
        except (IOError, OSError) as e:
            raise RTIInternalError(self._exception_io_str) from e
        except MarshallerException as e:
            raise RTIInternalError(self._exception_marshaller_str + str(e)) from e

    async def unsubscribe_interaction_class(self, the_class: int) -> None:
        """Unsubscribe from interaction class"""
        try:
            v = await self._stub.unsubscribe_interaction_class(the_class)
            self._handle_exception(v)
        except (IOError, OSError) as e:
            raise RTIInternalError(self._exception_io_str) from e
        except MarshallerException as e:
            raise RTIInternalError(self._exception_marshaller_str + str(e)) from e

    # Object Management Services - Placeholder implementations
    # (Full implementation would follow the same pattern as above)

    async def register_object_instance(self, the_class: int, the_object_name: Optional[str] = None) -> int:
        """Register object instance"""
        try:
            v = await self._stub.register_object_instance(the_class, the_object_name)
            if v is None:
                raise RTIInternalError("Invalid response from register_object_instance: response is None")
            
            if len(v) == 0:
                raise RTIInternalError("Invalid response from register_object_instance: empty response")
            
            # Response format: [exception_code, exception_description, instance_handle]
            # Even when there's an exception, the vector has 3 elements (instance_handle is -1)
            # Handle different types that might be in v[0] (int, str, etc.)
            raw_exception_code = v[0]
            if isinstance(raw_exception_code, str):
                # Try to parse as int
                try:
                    exception_code = int(raw_exception_code)
                except (ValueError, TypeError):
                    raise RTIInternalError(f"Invalid exception code type in response: {type(raw_exception_code)}, value: {raw_exception_code}")
            elif isinstance(raw_exception_code, int):
                exception_code = raw_exception_code
            else:
                # Try to convert to int (handles int-like objects, etc.)
                try:
                    exception_code = int(raw_exception_code)
                except (ValueError, TypeError):
                    raise RTIInternalError(f"Invalid exception code type in response: {type(raw_exception_code)}, value: {raw_exception_code}")
            
            if exception_code == RTIExceptions.Exception_Null:
                # Success - return instance handle
                if len(v) > 2:
                    handle = int(v[2]) if isinstance(v[2], (int, str)) else 0
                    # Debug: Log if handle is unexpectedly valid after unpublishing
                    # (This might indicate a server-side caching issue)
                    return handle
                else:
                    raise RTIInternalError("Invalid response from register_object_instance: missing instance handle")
            else:
                # Exception occurred - handle it (will raise exception)
                # Make sure we raise the exception - don't return
                self._handle_exception(v)
                # This should never be reached, but if _handle_exception doesn't raise, we have a problem
                raise RTIInternalError(f"register_object_instance: exception code {exception_code} not handled properly")
        except (IOError, OSError) as e:
            raise RTIInternalError(self._exception_io_str) from e
        except MarshallerException as e:
            raise RTIInternalError(self._exception_marshaller_str + str(e)) from e

    async def register_object_instance_with_region(
        self,
        the_class: int,
        the_object_name: Optional[str],
        the_attributes: AttributeHandleSet,
        the_regions: List[Region],
    ) -> int:
        """Register object instance with region"""
        try:
            attr_list = list(the_attributes.to_list()) if the_attributes else []
            region_handles = [r.get_handle() if hasattr(r, 'get_handle') else -1 for r in the_regions] if the_regions else []
            v = await self._stub.register_object_instance_with_region(the_class, the_object_name, attr_list, region_handles)
            if v and len(v) > 2 and v[0] == RTIExceptions.Exception_Null:
                return int(v[2]) if isinstance(v[2], (int, str)) else 0
            self._handle_exception(v)
            return 0
        except (IOError, OSError) as e:
            raise RTIInternalError(self._exception_io_str) from e
        except MarshallerException as e:
            raise RTIInternalError(self._exception_marshaller_str + str(e)) from e

    async def update_attribute_values(
        self,
        the_object: int,
        the_attributes: SuppliedAttributes,
        user_supplied_tag: bytes,
    ) -> None:
        """Update attribute values"""
        try:
            attr_vector = the_attributes.get_vector() if hasattr(the_attributes, 'get_vector') else []
            v = await self._stub.update_attribute_values(the_object, attr_vector, user_supplied_tag)
            self._handle_exception(v)
        except (IOError, OSError) as e:
            raise RTIInternalError(self._exception_io_str) from e
        except MarshallerException as e:
            raise RTIInternalError(self._exception_marshaller_str + str(e)) from e

    async def update_attribute_values_with_region(
        self,
        the_object: int,
        the_attributes: SuppliedAttributes,
        user_supplied_tag: bytes,
        the_region: Region,
    ) -> None:
        """Update attribute values with region"""
        try:
            attr_vector = the_attributes.get_vector() if hasattr(the_attributes, 'get_vector') else []
            region_handle = the_region.get_handle() if hasattr(the_region, 'get_handle') else -1
            v = await self._stub.update_attribute_values(the_object, attr_vector, user_supplied_tag, region_handle)
            self._handle_exception(v)
        except (IOError, OSError) as e:
            raise RTIInternalError(self._exception_io_str) from e
        except MarshallerException as e:
            raise RTIInternalError(self._exception_marshaller_str + str(e)) from e

    async def send_interaction(
        self,
        the_interaction: int,
        the_parameters: SuppliedParameters,
        user_supplied_tag: bytes,
    ) -> None:
        """Send interaction"""
        try:
            param_vector = the_parameters.get_vector() if hasattr(the_parameters, 'get_vector') else []
            v = await self._stub.send_interaction(the_interaction, param_vector, user_supplied_tag)
            self._handle_exception(v)
        except (IOError, OSError) as e:
            raise RTIInternalError(self._exception_io_str) from e
        except MarshallerException as e:
            raise RTIInternalError(self._exception_marshaller_str + str(e)) from e

    async def send_interaction_with_region(
        self,
        the_interaction: int,
        the_parameters: SuppliedParameters,
        user_supplied_tag: bytes,
        the_region: Region,
    ) -> None:
        """Send interaction with region"""
        try:
            param_vector = the_parameters.get_vector() if hasattr(the_parameters, 'get_vector') else []
            region_handle = the_region.get_handle() if hasattr(the_region, 'get_handle') else -1
            v = await self._stub.send_interaction_with_region(the_interaction, param_vector, user_supplied_tag, region_handle)
            self._handle_exception(v)
        except (IOError, OSError) as e:
            raise RTIInternalError(self._exception_io_str) from e
        except MarshallerException as e:
            raise RTIInternalError(self._exception_marshaller_str + str(e)) from e

    async def delete_object_instance(self, the_object: int, user_supplied_tag: bytes) -> None:
        """Delete object instance"""
        try:
            v = await self._stub.delete_object_instance(the_object, user_supplied_tag)
            self._handle_exception(v)
        except (IOError, OSError) as e:
            raise RTIInternalError(self._exception_io_str) from e
        except MarshallerException as e:
            raise RTIInternalError(self._exception_marshaller_str + str(e)) from e

    # Region Management
    async def create_region(self, space_handle: int, number_of_extents: int) -> Region:
        """Create region"""
        try:
            v = await self._stub.create_region(space_handle, number_of_extents)
            self._handle_exception(v)
            if v and len(v) > 2:
                # v[0] = exception code, v[1] = exception description, v[2] = region vector
                region_vector = v[2]
                if region_vector and isinstance(region_vector, list) and len(region_vector) >= 3:
                    # Parse region vector: [routingSpaceHandle, numberOfDimensions, handle, ...extents]
                    routing_space_handle = int(region_vector[0])
                    number_of_dimensions = int(region_vector[1])
                    region_handle = int(region_vector[2])
                    # Create Region object
                    region = Region(routing_space_handle, number_of_extents, number_of_dimensions)
                    region.set_handle(region_handle)
                    # TODO: Parse extents if needed (they're byte arrays starting at index 3)
                    return region
            raise RTIInternalError("Invalid response from create_region")
        except (IOError, OSError) as e:
            raise RTIInternalError(self._exception_io_str) from e
        except MarshallerException as e:
            raise RTIInternalError(self._exception_marshaller_str + str(e)) from e

    async def delete_region(self, the_region: Region) -> None:
        """Delete region"""
        try:
            # The server takes the region handle, not a Region object
            region_handle = the_region.get_handle()
            v = await self._stub.delete_region(region_handle)
            self._handle_exception(v)
        except (IOError, OSError) as e:
            raise RTIInternalError(self._exception_io_str) from e
        except MarshallerException as e:
            raise RTIInternalError(self._exception_marshaller_str + str(e)) from e

    async def notify_of_region_modification(self, the_region: Region) -> None:
        """Notify of region modification"""
        try:
            # Serialize region to Vector format: [routingSpaceHandle, numberOfDimensions, handle, ...extents]
            # Send the region in its vector form
            # The server expects vector, not int array - use _VectorParam wrapper to force TC_VECTOR
            from retiqo.rti.rti_surrogate_stub import _VectorParam
            region_vector = the_region.get_vector()
            region_vector_wrapped = _VectorParam(region_vector)
            v = await self._stub.notify_of_region_modification(region_vector_wrapped)
            self._handle_exception(v)
        except (IOError, OSError) as e:
            raise RTIInternalError(self._exception_io_str) from e
        except MarshallerException as e:
            raise RTIInternalError(self._exception_marshaller_str + str(e)) from e

    async def get_region_token(self, the_region: Region) -> int:
        """Get region token"""
        try:
            # The server takes the region vector, not a Region object
            from retiqo.rti.rti_surrogate_stub import _VectorParam
            region_vector = the_region.get_vector()
            region_vector_wrapped = _VectorParam(region_vector)
            v = await self._stub.get_region_token(region_vector_wrapped)
            self._handle_exception(v)
            if v and len(v) > 2:
                # v[0] = exception code, v[1] = exception description, v[2] = region token
                return int(v[2]) if isinstance(v[2], (int, str)) else int(v[2])
            raise RTIInternalError("Invalid response from get_region_token")
        except (IOError, OSError) as e:
            raise RTIInternalError(self._exception_io_str) from e
        except MarshallerException as e:
            raise RTIInternalError(self._exception_marshaller_str + str(e)) from e

    async def get_region(self, region_token: int) -> Region:
        """Get region from token"""
        try:
            v = await self._stub.get_region(region_token)
            self._handle_exception(v)
            if v and len(v) > 2:
                # v[0] = exception code, v[1] = exception description, v[2] = region vector
                region_vector = v[2]
                if region_vector and isinstance(region_vector, list) and len(region_vector) >= 3:
                    # Parse region vector: [routingSpaceHandle, numberOfDimensions, handle, ...extents as bytes]
                    routing_space_handle = int(region_vector[0])
                    number_of_dimensions = int(region_vector[1])
                    region_handle = int(region_vector[2])
                    # Calculate number of extents from vector size
                    num_of_extents = len(region_vector) - 3
                    # Create Region object
                    region = Region(routing_space_handle, num_of_extents, number_of_dimensions)
                    region.set_handle(region_handle)
                    # Parse extents from byte arrays (starting at index 3)
                    from retiqo.rti.region import Extent
                    for j in range(num_of_extents):
                        extent_byte_array = region_vector[j + 3]
                        if isinstance(extent_byte_array, bytes):
                            # Deserialize extent from byte array
                            extent = Extent(byte_array=extent_byte_array)
                            region._extents[j] = extent
                    return region
            raise RTIInternalError("Invalid response from get_region")
        except (IOError, OSError) as e:
            raise RTIInternalError(self._exception_io_str) from e
        except MarshallerException as e:
            raise RTIInternalError(self._exception_marshaller_str + str(e)) from e

    async def associate_region_for_updates(
        self,
        the_region: Region,
        the_object: int,
        the_attributes: AttributeHandleSet,
    ) -> None:
        """Associate region for updates"""
        try:
            attr_list = list(the_attributes.to_list()) if the_attributes else []
            region_handle = the_region.get_handle() if hasattr(the_region, 'get_handle') else -1
            v = await self._stub.associate_region_for_updates(region_handle, the_object, attr_list)
            self._handle_exception(v)
        except (IOError, OSError) as e:
            raise RTIInternalError(self._exception_io_str) from e
        except MarshallerException as e:
            raise RTIInternalError(self._exception_marshaller_str + str(e)) from e

    async def unassociate_region_for_updates(
        self,
        the_region: Region,
        the_object: int,
        the_attributes: Optional[AttributeHandleSet] = None,
    ) -> None:
        """Unassociate region for updates"""
        try:
            # Server expects (region, object handle), with no attributes parameter
            region_handle = the_region.get_handle() if hasattr(the_region, 'get_handle') else -1
            v = await self._stub.unassociate_region_for_updates(region_handle, the_object)
            self._handle_exception(v)
        except (IOError, OSError) as e:
            raise RTIInternalError(self._exception_io_str) from e
        except MarshallerException as e:
            raise RTIInternalError(self._exception_marshaller_str + str(e)) from e

    async def subscribe_object_class_attributes_with_region(
        self,
        the_class: int,
        attribute_list: AttributeHandleSet,
        the_region: Region,
    ) -> None:
        """Subscribe to object class attributes with region"""
        try:
            attr_list = list(attribute_list.to_list()) if attribute_list else []
            region_handle = the_region.get_handle() if hasattr(the_region, 'get_handle') else -1
            v = await self._stub.subscribe_object_class_attributes_with_region(the_class, attr_list, region_handle)
            self._handle_exception(v)
        except (IOError, OSError) as e:
            raise RTIInternalError(self._exception_io_str) from e
        except MarshallerException as e:
            raise RTIInternalError(self._exception_marshaller_str + str(e)) from e

    async def subscribe_interaction_class_with_region(self, the_class: int, the_region: Region) -> None:
        """Subscribe to interaction class with region"""
        try:
            region_handle = the_region.get_handle() if hasattr(the_region, 'get_handle') else -1
            v = await self._stub.subscribe_interaction_class_with_region(the_class, region_handle)
            self._handle_exception(v)
        except (IOError, OSError) as e:
            raise RTIInternalError(self._exception_io_str) from e
        except MarshallerException as e:
            raise RTIInternalError(self._exception_marshaller_str + str(e)) from e

    async def request_object_attribute_value_update(
        self, the_object: int, the_attributes: AttributeHandleSet
    ) -> None:
        """Request object attribute value update"""
        try:
            attr_list = list(the_attributes.to_list()) if the_attributes else []
            v = await self._stub.request_object_attribute_value_update(the_object, attr_list)
            self._handle_exception(v)
        except (IOError, OSError) as e:
            raise RTIInternalError(self._exception_io_str) from e
        except MarshallerException as e:
            raise RTIInternalError(self._exception_marshaller_str + str(e)) from e

    async def request_class_attribute_value_update(
        self, the_class: int, the_attributes: AttributeHandleSet
    ) -> None:
        """Request class attribute value update"""
        try:
            attr_list = list(the_attributes.to_list()) if the_attributes else []
            v = await self._stub.request_class_attribute_value_update(the_class, attr_list)
            self._handle_exception(v)
        except (IOError, OSError) as e:
            raise RTIInternalError(self._exception_io_str) from e
        except MarshallerException as e:
            raise RTIInternalError(self._exception_marshaller_str + str(e)) from e

    async def request_class_attribute_value_update_with_region(
        self,
        the_class: int,
        the_attributes: AttributeHandleSet,
        the_region: Region,
    ) -> None:
        """Request class attribute value update with region"""
        try:
            attr_list = the_attributes.to_list() if hasattr(the_attributes, 'to_list') else list(the_attributes)
            region_handle = the_region.get_handle() if hasattr(the_region, 'get_handle') else -1
            v = await self._stub.request_class_attribute_value_update_with_region(the_class, attr_list, region_handle)
            self._handle_exception(v)
        except (IOError, OSError) as e:
            raise RTIInternalError(self._exception_io_str) from e
        except MarshallerException as e:
            raise RTIInternalError(self._exception_marshaller_str + str(e)) from e

    # Ownership Management
    async def attribute_ownership_acquisition_request(
        self, the_object: int, desired_attributes: AttributeHandleSet, user_supplied_tag: bytes
    ) -> None:
        """Request attribute ownership acquisition (alias for attribute_ownership_acquisition)"""
        await self.attribute_ownership_acquisition(the_object, desired_attributes, user_supplied_tag)

    async def attribute_ownership_acquisition(
        self, the_object: int, desired_attributes: AttributeHandleSet, user_supplied_tag: bytes
    ) -> None:
        """Acquire attribute ownership"""
        try:
            attr_list = list(desired_attributes.to_list()) if desired_attributes else []
            v = await self._stub.attribute_ownership_acquisition(the_object, attr_list, user_supplied_tag)
            self._handle_exception(v)
        except (IOError, OSError) as e:
            raise RTIInternalError(self._exception_io_str) from e
        except MarshallerException as e:
            raise RTIInternalError(self._exception_marshaller_str + str(e)) from e

    async def attribute_ownership_acquisition_if_available(
        self, the_object: int, desired_attributes: AttributeHandleSet
    ) -> None:
        """Acquire attribute ownership if available"""
        try:
            attr_list = list(desired_attributes.to_list()) if desired_attributes else []
            v = await self._stub.attribute_ownership_acquisition_if_available(the_object, attr_list)
            self._handle_exception(v)
        except (IOError, OSError) as e:
            raise RTIInternalError(self._exception_io_str) from e
        except MarshallerException as e:
            raise RTIInternalError(self._exception_marshaller_str + str(e)) from e

    async def cancel_attribute_ownership_acquisition(
        self, the_object: int, the_attributes: AttributeHandleSet
    ) -> None:
        """Cancel attribute ownership acquisition"""
        try:
            attr_list = list(the_attributes.to_list()) if the_attributes else []
            v = await self._stub.cancel_attribute_ownership_acquisition(the_object, attr_list)
            self._handle_exception(v)
        except (IOError, OSError) as e:
            raise RTIInternalError(self._exception_io_str) from e
        except MarshallerException as e:
            raise RTIInternalError(self._exception_marshaller_str + str(e)) from e

    async def query_attribute_ownership(self, the_object: int, the_attribute: int) -> None:
        """Query attribute ownership"""
        try:
            v = await self._stub.query_attribute_ownership(the_object, the_attribute)
            self._handle_exception(v)
        except (IOError, OSError) as e:
            raise RTIInternalError(self._exception_io_str) from e
        except MarshallerException as e:
            raise RTIInternalError(self._exception_marshaller_str + str(e)) from e

    async def is_attribute_owned_by_actor(self, the_object: int, the_attribute: int) -> bool:
        """Check if attribute is owned by actor"""
        try:
            v = await self._stub.is_attribute_owned_by_actor(the_object, the_attribute)
            self._handle_exception(v)
            if v and len(v) > 2:
                # v[0] = exception code, v[1] = exception description, v[2] = boolean result
                # Handle case where boolean might be None/null
                result = v[2]
                if result is None:
                    return False
                # Convert to bool - handle both boolean and integer (0/1) representations
                if isinstance(result, bool):
                    return result
                elif isinstance(result, int):
                    return bool(result)
                else:
                    # Try to convert to bool
                    return bool(result)
            return False
        except (IOError, OSError) as e:
            raise RTIInternalError(self._exception_io_str) from e
        except MarshallerException as e:
            raise RTIInternalError(self._exception_marshaller_str + str(e)) from e
        except ValueError as e:
            # Handle "Expected TC_BOOLEAN, got 0" error - boolean might be null
            if "Expected TC_BOOLEAN" in str(e):
                # The boolean value in the response is null - return False
                return False
            raise RTIInternalError(f"Error parsing boolean result: {e}") from e

    async def unconditional_attribute_ownership_divestiture(
        self, the_object: int, the_attributes: AttributeHandleSet
    ) -> None:
        """Unconditionally divest attribute ownership"""
        try:
            # Convert AttributeHandleSet to list of ints
            attr_list = the_attributes.to_list() if hasattr(the_attributes, 'to_list') else list(the_attributes)
            v = await self._stub.unconditional_attribute_ownership_divestiture(the_object, attr_list)
            self._handle_exception(v)
        except (IOError, OSError) as e:
            raise RTIInternalError(self._exception_io_str) from e
        except MarshallerException as e:
            raise RTIInternalError(self._exception_marshaller_str + str(e)) from e

    async def negotiated_attribute_ownership_divestiture(
        self,
        the_object: int,
        the_attributes: AttributeHandleSet,
        user_supplied_tag: bytes,
    ) -> None:
        """Negotiate attribute ownership divestiture"""
        try:
            attr_list = the_attributes.to_list() if hasattr(the_attributes, 'to_list') else list(the_attributes)
            v = await self._stub.negotiated_attribute_ownership_divestiture(the_object, attr_list, user_supplied_tag)
            self._handle_exception(v)
        except (IOError, OSError) as e:
            raise RTIInternalError(self._exception_io_str) from e
        except MarshallerException as e:
            raise RTIInternalError(self._exception_marshaller_str + str(e)) from e

    async def cancel_negotiated_attribute_ownership_divestiture(
        self, the_object: int, the_attributes: AttributeHandleSet
    ) -> None:
        """Cancel negotiated attribute ownership divestiture"""
        try:
            attr_list = the_attributes.to_list() if hasattr(the_attributes, 'to_list') else list(the_attributes)
            v = await self._stub.cancel_negotiated_attribute_ownership_divestiture(the_object, attr_list)
            self._handle_exception(v)
        except (IOError, OSError) as e:
            raise RTIInternalError(self._exception_io_str) from e
        except MarshallerException as e:
            raise RTIInternalError(self._exception_marshaller_str + str(e)) from e

    # RTI Support Services
    async def get_object_class_handle(self, the_object_class_name: str) -> int:
        """Get object class handle from name"""
        try:
            v = await self._stub.get_object_class_handle(the_object_class_name)
            self._handle_exception(v)
            if v and len(v) > 2:
                # v[0] = exception code, v[1] = exception description, v[2] = object class handle
                return int(v[2]) if isinstance(v[2], (int, str)) else int(v[2])
            raise RTIInternalError("Invalid response from get_object_class_handle")
        except Exception as e:
            if isinstance(e, RTIException):
                raise
            raise RTIInternalError(f"Error in get_object_class_handle: {e}")

    async def get_object_class_name(self, the_object_class: int) -> str:
        """Get object class name from handle"""
        try:
            v = await self._stub.get_object_class_name(the_object_class)
            self._handle_exception(v)
            if v and len(v) > 2:
                # v[0] = exception code, v[1] = exception description, v[2] = object class name
                return str(v[2]) if v[2] is not None else ""
            raise RTIInternalError("Invalid response from get_object_class_name")
        except Exception as e:
            if isinstance(e, RTIException):
                raise
            raise RTIInternalError(f"Error in get_object_class_name: {e}")

    async def get_attribute_handle(self, the_attribute_name: str, which_class: int) -> int:
        """Get attribute handle from name"""
        try:
            v = await self._stub.get_attribute_handle(the_attribute_name, which_class)
            self._handle_exception(v)
            if v and len(v) > 2:
                # v[0] = exception code, v[1] = exception description, v[2] = attribute handle
                return int(v[2]) if isinstance(v[2], (int, str)) else int(v[2])
            raise RTIInternalError("Invalid response from get_attribute_handle")
        except Exception as e:
            if isinstance(e, RTIException):
                raise
            raise RTIInternalError(f"Error in get_attribute_handle: {e}")

    async def get_attribute_name(self, the_attribute: int, which_class: int) -> str:
        """Get attribute name from handle"""
        try:
            v = await self._stub.get_attribute_name(the_attribute, which_class)
            self._handle_exception(v)
            if v and len(v) > 2:
                # v[0] = exception code, v[1] = exception description, v[2] = attribute name
                return str(v[2]) if v[2] is not None else ""
            raise RTIInternalError("Invalid response from get_attribute_name")
        except Exception as e:
            if isinstance(e, RTIException):
                raise
            raise RTIInternalError(f"Error in get_attribute_name: {e}")

    async def get_interaction_class_handle(self, the_interaction_class_name: str) -> int:
        """Get interaction class handle from name"""
        try:
            v = await self._stub.get_interaction_class_handle(the_interaction_class_name)
            self._handle_exception(v)
            if v and len(v) > 2:
                # v[0] = exception code, v[1] = exception description, v[2] = interaction class handle
                return int(v[2]) if isinstance(v[2], (int, str)) else int(v[2])
            raise RTIInternalError("Invalid response from get_interaction_class_handle")
        except Exception as e:
            if isinstance(e, RTIException):
                raise
            raise RTIInternalError(f"Error in get_interaction_class_handle: {e}")

    async def get_interaction_class_name(self, the_interaction_class: int) -> str:
        """Get interaction class name from handle"""
        try:
            v = await self._stub.get_interaction_class_name(the_interaction_class)
            self._handle_exception(v)
            if v and len(v) > 2:
                # v[0] = exception code, v[1] = exception description, v[2] = interaction class name
                return str(v[2]) if v[2] is not None else ""
            raise RTIInternalError("Invalid response from get_interaction_class_name")
        except Exception as e:
            if isinstance(e, RTIException):
                raise
            raise RTIInternalError(f"Error in get_interaction_class_name: {e}")

    async def get_parameter_handle(self, the_parameter_name: str, which_class: int) -> int:
        """Get parameter handle from name"""
        try:
            v = await self._stub.get_parameter_handle(the_parameter_name, which_class)
            self._handle_exception(v)
            if v and len(v) > 2:
                # v[0] = exception code, v[1] = exception description, v[2] = parameter handle
                return int(v[2]) if isinstance(v[2], (int, str)) else int(v[2])
            raise RTIInternalError("Invalid response from get_parameter_handle")
        except Exception as e:
            if isinstance(e, RTIException):
                raise
            raise RTIInternalError(f"Error in get_parameter_handle: {e}")

    async def get_parameter_name(self, the_parameter: int, which_class: int) -> str:
        """Get parameter name from handle"""
        try:
            v = await self._stub.get_parameter_name(the_parameter, which_class)
            self._handle_exception(v)
            if v and len(v) > 2:
                # v[0] = exception code, v[1] = exception description, v[2] = parameter name
                return str(v[2]) if v[2] is not None else ""
            raise RTIInternalError("Invalid response from get_parameter_name")
        except Exception as e:
            if isinstance(e, RTIException):
                raise
            raise RTIInternalError(f"Error in get_parameter_name: {e}")

    async def get_routing_space_handle(self, the_routing_space_name: str) -> int:
        """Get routing space handle from name"""
        try:
            v = await self._stub.get_routing_space_handle(the_routing_space_name)
            self._handle_exception(v)
            if v and len(v) > 2:
                # v[0] = exception code, v[1] = exception description, v[2] = routing space handle
                return int(v[2]) if isinstance(v[2], (int, str)) else int(v[2])
            raise RTIInternalError("Invalid response from get_routing_space_handle")
        except Exception as e:
            if isinstance(e, RTIException):
                raise
            raise RTIInternalError(f"Error in get_routing_space_handle: {e}")

    async def get_routing_space_name(self, the_routing_space: int) -> str:
        """Get routing space name from handle"""
        try:
            v = await self._stub.get_routing_space_name(the_routing_space)
            self._handle_exception(v)
            if v and len(v) > 2:
                # v[0] = exception code, v[1] = exception description, v[2] = routing space name
                return str(v[2]) if v[2] is not None else ""
            raise RTIInternalError("Invalid response from get_routing_space_name")
        except Exception as e:
            if isinstance(e, RTIException):
                raise
            raise RTIInternalError(f"Error in get_routing_space_name: {e}")

    async def get_dimension_handle(self, the_dimension_name: str, which_space: int) -> int:
        """Get dimension handle from name"""
        try:
            v = await self._stub.get_dimension_handle(the_dimension_name, which_space)
            self._handle_exception(v)
            if v and len(v) > 2:
                # v[0] = exception code, v[1] = exception description, v[2] = dimension handle
                return int(v[2]) if isinstance(v[2], (int, str)) else int(v[2])
            raise RTIInternalError("Invalid response from get_dimension_handle")
        except Exception as e:
            if isinstance(e, RTIException):
                raise
            raise RTIInternalError(f"Error in get_dimension_handle: {e}")

    async def get_dimension_name(self, the_dimension: int, which_space: int) -> str:
        """Get dimension name from handle"""
        try:
            v = await self._stub.get_dimension_name(the_dimension, which_space)
            self._handle_exception(v)
            if v and len(v) > 2:
                # v[0] = exception code, v[1] = exception description, v[2] = dimension name
                return str(v[2]) if v[2] is not None else ""
            raise RTIInternalError("Invalid response from get_dimension_name")
        except Exception as e:
            if isinstance(e, RTIException):
                raise
            raise RTIInternalError(f"Error in get_dimension_name: {e}")

    async def get_object_instance_handle(self, the_object_name: str) -> int:
        """Get object instance handle from name"""
        # Placeholder - full implementation needed
        raise NotImplementedError("get_object_instance_handle not yet fully implemented")

    async def get_object_instance_name(self, the_object: int) -> str:
        """Get object instance name from handle"""
        try:
            v = await self._stub.get_object_instance_name(the_object)
            self._handle_exception(v)
            if v and len(v) > 2:
                # v[0] = exception code, v[1] = exception description, v[2] = object instance name
                return str(v[2]) if v[2] is not None else ""
            raise RTIInternalError("Invalid response from get_object_instance_name")
        except (IOError, OSError) as e:
            raise RTIInternalError(self._exception_io_str) from e
        except MarshallerException as e:
            raise RTIInternalError(self._exception_marshaller_str + str(e)) from e

    async def get_attribute_routing_space_handle(self, the_handle: int, which_class: int) -> int:
        """Get attribute routing space handle"""
        try:
            v = await self._stub.get_attribute_routing_space_handle(the_handle, which_class)
            self._handle_exception(v)
            if v and len(v) > 2:
                # v[0] = exception code, v[1] = exception description, v[2] = routing space handle
                return int(v[2]) if isinstance(v[2], (int, str)) else int(v[2])
            raise RTIInternalError("Invalid response from get_attribute_routing_space_handle")
        except Exception as e:
            if isinstance(e, RTIException):
                raise
            raise RTIInternalError(f"Error in get_attribute_routing_space_handle: {e}")

    async def get_interaction_routing_space_handle(self, the_class: int) -> int:
        """Get interaction routing space handle"""
        try:
            v = await self._stub.get_interaction_routing_space_handle(the_class)
            self._handle_exception(v)
            if v and len(v) > 2:
                # v[0] = exception code, v[1] = exception description, v[2] = routing space handle
                return int(v[2]) if isinstance(v[2], (int, str)) else int(v[2])
            raise RTIInternalError("Invalid response from get_interaction_routing_space_handle")
        except Exception as e:
            if isinstance(e, RTIException):
                raise
            raise RTIInternalError(f"Error in get_interaction_routing_space_handle: {e}")

    async def get_object_class_routing_space_handle(self, the_class: int) -> int:
        """Get object class routing space handle"""
        try:
            v = await self._stub.get_object_class_routing_space_handle(the_class)
            self._handle_exception(v)
            if v and len(v) > 2:
                # v[0] = exception code, v[1] = exception description, v[2] = routing space handle
                return int(v[2]) if isinstance(v[2], (int, str)) else int(v[2])
            raise RTIInternalError("Invalid response from get_object_class_routing_space_handle")
        except Exception as e:
            if isinstance(e, RTIException):
                raise
            raise RTIInternalError(f"Error in get_object_class_routing_space_handle: {e}")

    # Advisory Switches
    async def enable_class_relevance_advisory_switch(self) -> None:
        """Enable class relevance advisory switch"""
        try:
            v = await self._stub.enable_class_relevance_advisory_switch()
            self._handle_exception(v)
        except (IOError, OSError) as e:
            raise RTIInternalError(self._exception_io_str) from e
        except MarshallerException as e:
            raise RTIInternalError(self._exception_marshaller_str + str(e)) from e

    async def disable_class_relevance_advisory_switch(self) -> None:
        """Disable class relevance advisory switch"""
        try:
            v = await self._stub.disable_class_relevance_advisory_switch()
            self._handle_exception(v)
        except (IOError, OSError) as e:
            raise RTIInternalError(self._exception_io_str) from e
        except MarshallerException as e:
            raise RTIInternalError(self._exception_marshaller_str + str(e)) from e

    async def enable_attribute_relevance_advisory_switch(self) -> None:
        """Enable attribute relevance advisory switch"""
        try:
            v = await self._stub.enable_attribute_relevance_advisory_switch()
            self._handle_exception(v)
        except (IOError, OSError) as e:
            raise RTIInternalError(self._exception_io_str) from e
        except MarshallerException as e:
            raise RTIInternalError(self._exception_marshaller_str + str(e)) from e

    async def disable_attribute_relevance_advisory_switch(self) -> None:
        """Disable attribute relevance advisory switch"""
        try:
            v = await self._stub.disable_attribute_relevance_advisory_switch()
            self._handle_exception(v)
        except (IOError, OSError) as e:
            raise RTIInternalError(self._exception_io_str) from e
        except MarshallerException as e:
            raise RTIInternalError(self._exception_marshaller_str + str(e)) from e

    async def enable_attribute_scope_advisory_switch(self) -> None:
        """Enable attribute scope advisory switch"""
        try:
            v = await self._stub.enable_attribute_scope_advisory_switch()
            self._handle_exception(v)
        except (IOError, OSError) as e:
            raise RTIInternalError(self._exception_io_str) from e
        except MarshallerException as e:
            raise RTIInternalError(self._exception_marshaller_str + str(e)) from e

    async def disable_attribute_scope_advisory_switch(self) -> None:
        """Disable attribute scope advisory switch"""
        try:
            v = await self._stub.disable_attribute_scope_advisory_switch()
            self._handle_exception(v)
        except (IOError, OSError) as e:
            raise RTIInternalError(self._exception_io_str) from e
        except MarshallerException as e:
            raise RTIInternalError(self._exception_marshaller_str + str(e)) from e

    async def enable_interaction_relevance_advisory_switch(self) -> None:
        """Enable interaction relevance advisory switch"""
        try:
            v = await self._stub.enable_interaction_relevance_advisory_switch()
            self._handle_exception(v)
        except (IOError, OSError) as e:
            raise RTIInternalError(self._exception_io_str) from e
        except MarshallerException as e:
            raise RTIInternalError(self._exception_marshaller_str + str(e)) from e

    async def disable_interaction_relevance_advisory_switch(self) -> None:
        """Disable interaction relevance advisory switch"""
        try:
            v = await self._stub.disable_interaction_relevance_advisory_switch()
            self._handle_exception(v)
        except (IOError, OSError) as e:
            raise RTIInternalError(self._exception_io_str) from e
        except MarshallerException as e:
            raise RTIInternalError(self._exception_marshaller_str + str(e)) from e

    async def _callback_loop(self) -> None:
        """Callback loop for handling async callbacks"""
        from retiqo.transport.async_handler import AsyncHandler
        from retiqo.streams.deserializing_stream import DeserializingStream
        from retiqo.streams.pdu.pdu_type import PDU_S_Type
        from retiqo.rti.attribute_handle_set import AttributeHandleSetFactory
        from retiqo.rti.reflected_attributes import ReflectedAttributes
        from retiqo.rti.received_interaction import ReceivedInteraction
        from retiqo.rti.consensus_state import ConsensusState

        handler: Optional[AsyncHandler] = None
        session = self._stub.get_session()
        if session:
            handler = session.get_handler()

        loop_iteration = 0
        while not self._shutdown_flag:
            if handler:
                try:
                    bytes_in = await handler.recv_callback(timeout=1.0)
                    if bytes_in:
                        # Callback includes 8-byte length header: [8-byte length] + [PDU data]
                        if len(bytes_in) < 9:
                            continue
                        
                        # Extract length header
                        from retiqo.streams.base import Base
                        packet_length = Base.extract_long(bytes_in, 0)
                        if packet_length > len(bytes_in) - 8:
                            continue
                        
                        # Extract PDU data (skip 8-byte length header)
                        pdu_data = bytes_in[8:8+packet_length]
                        
                        # Parse callback message from PDU data
                        stream = DeserializingStream(pdu_data)
                        pdu = stream.read_byte()

                        if pdu == PDU_S_Type.PDU_S_KeepAlive:
                            # Keep-alive received
                            continue
                        elif pdu == PDU_S_Type.PDU_S_CallBack:
                            # Callback received
                            sequence_number = stream.read_short()
                            method_id = stream.read_byte()
                            
                            if self._actor_reference:
                                # Dispatch callback based on method_id
                                await self._dispatch_callback(method_id, stream)
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    if not self._shutdown_flag:
                        print(f"Exception in callback loop: {e}")
                        import traceback
                        traceback.print_exc()
            else:
                if loop_iteration == 0:
                    print(f"RTISurrogateImpl callback loop: No handler available")
                await asyncio.sleep(0.1)

    async def _dispatch_callback(self, method_id: int, stream: "DeserializingStream") -> None:
        """Dispatch callback to actor surrogate"""
        from retiqo.rti.callback_method_ids import RTICallbackMethodIds
        from retiqo.rti.attribute_handle_set import AttributeHandleSetFactory
        from retiqo.rti.reflected_attributes import ReflectedAttributes
        from retiqo.rti.received_interaction import ReceivedInteraction
        from retiqo.rti.consensus_state import ConsensusState

        if not self._actor_reference:
            return

        try:
            if method_id == RTICallbackMethodIds.CallbackMethodId_consensusPointRegistrationFailed:
                reason = stream.read_object()
                await self._actor_reference.consensus_point_registration_failed(str(reason))
            elif method_id == RTICallbackMethodIds.CallbackMethodId_consensusPointRegistrationSucceeded:
                reason = stream.read_object()
                await self._actor_reference.consensus_point_registration_succeeded(str(reason))
            elif method_id == RTICallbackMethodIds.CallbackMethodId_announceConsensusPoint:
                v = stream.read_object()
                if isinstance(v, list) and len(v) >= 2:
                    await self._actor_reference.announce_consensus_point(str(v[0]), bytes(v[1]) if isinstance(v[1], bytes) else v[1])
            elif method_id == RTICallbackMethodIds.CallbackMethodId_stateChannelInConsensus:
                v = stream.read_object()
                if isinstance(v, list) and len(v) >= 2:
                    # Parse ConsensusState from vector
                    consensus_state = ConsensusState.from_vector(v[1] if isinstance(v[1], list) else [])
                    await self._actor_reference.state_channel_in_consensus(str(v[0]), consensus_state)
            elif method_id == RTICallbackMethodIds.CallbackMethodId_initiateActorSave:
                label = stream.read_object()
                await self._actor_reference.initiate_actor_save(str(label))
            elif method_id == RTICallbackMethodIds.CallbackMethodId_stateChannelSaved:
                await self._actor_reference.state_channel_saved()
            elif method_id == RTICallbackMethodIds.CallbackMethodId_stateChannelNotSaved:
                await self._actor_reference.state_channel_not_saved()
            elif method_id == RTICallbackMethodIds.CallbackMethodId_requestStateChannelRestoreSucceeded:
                label = stream.read_object()
                await self._actor_reference.request_state_channel_restore_succeeded(str(label))
            elif method_id == RTICallbackMethodIds.CallbackMethodId_requestStateChannelRestoreFailed:
                v = stream.read_object()
                if isinstance(v, list) and len(v) >= 2:
                    await self._actor_reference.request_state_channel_restore_failed(str(v[0]), str(v[1]))
            elif method_id == RTICallbackMethodIds.CallbackMethodId_stateChannelRestoreBegun:
                await self._actor_reference.state_channel_restore_begun()
            elif method_id == RTICallbackMethodIds.CallbackMethodId_initiateActorRestore:
                v = stream.read_object()
                if isinstance(v, list) and len(v) >= 2:
                    await self._actor_reference.initiate_actor_restore(str(v[0]), int(v[1]))
            elif method_id == RTICallbackMethodIds.CallbackMethodId_stateChannelRestored:
                await self._actor_reference.state_channel_restored()
            elif method_id == RTICallbackMethodIds.CallbackMethodId_stateChannelNotRestored:
                await self._actor_reference.state_channel_not_restored()
            elif method_id == RTICallbackMethodIds.CallbackMethodId_startRegistrationForObjectClass:
                class_handle = stream.read_object()
                await self._actor_reference.start_registration_for_object_class(int(class_handle))
            elif method_id == RTICallbackMethodIds.CallbackMethodId_stopRegistrationForObjectClass:
                class_handle = stream.read_object()
                await self._actor_reference.stop_registration_for_object_class(int(class_handle))
            elif method_id == RTICallbackMethodIds.CallbackMethodId_turnInteractionsOn:
                class_handle = stream.read_object()
                await self._actor_reference.turn_interactions_on(int(class_handle))
            elif method_id == RTICallbackMethodIds.CallbackMethodId_turnInteractionsOff:
                class_handle = stream.read_object()
                await self._actor_reference.turn_interactions_off(int(class_handle))
            elif method_id == RTICallbackMethodIds.CallbackMethodId_discoverObjectInstance:
                v = stream.read_object()
                if isinstance(v, list) and len(v) >= 3:
                    await self._actor_reference.discover_object_instance(
                        int(v[0]), int(v[1]), str(v[2]) if v[2] else None
                    )
            elif method_id == RTICallbackMethodIds.CallbackMethodId_reflectAttributeValues_1:
                # reflectAttributeValues_1 - same format as _2, but may have different parameter structure
                try:
                    v = stream.read_object()
                    if not isinstance(v, list) or len(v) < 3:
                        print(f"Error in reflectAttributeValues_1: Invalid vector format. v type={type(v)}, v={v}")
                        return
                    
                    # v[0] = object handle (int)
                    # v[1] = attributes vector (vector) = [count, handle1, value1, region1, handle2, value2, region2, ...]
                    # v[2] = user supplied tag (bytes)
                    object_handle = int(v[0]) if v[0] is not None else 0
                    attrs_vector = v[1]
                    user_tag = bytes(v[2]) if isinstance(v[2], bytes) else (v[2] if v[2] else b"")
                    
                    if not isinstance(attrs_vector, list):
                        print(f"Error in reflectAttributeValues_1: attrs_vector is not a list. type={type(attrs_vector)}, value={attrs_vector}")
                        reflected_attrs = ReflectedAttributes.from_vector([])
                    else:
                        reflected_attrs = ReflectedAttributes.from_vector(attrs_vector)
                    
                    if self._actor_reference:
                        await self._actor_reference.reflect_attribute_values(object_handle, reflected_attrs, user_tag)
                except Exception as e:
                    print(f"Error in reflectAttributeValues_1 callback: {e}")
                    import traceback
                    traceback.print_exc()
                    raise
            elif method_id == RTICallbackMethodIds.CallbackMethodId_reflectAttributeValues_2:
                try:
                    v = stream.read_object()
                    if not isinstance(v, list) or len(v) < 3:
                        print(f"Error in reflectAttributeValues_2: Invalid vector format. v type={type(v)}, v={v}")
                        return
                    
                    # v[0] = object handle (int)
                    # v[1] = attributes vector (vector) = [count, handle1, value1, region1, handle2, value2, region2, ...]
                    # v[2] = user supplied tag (bytes)
                    object_handle = int(v[0]) if v[0] is not None else 0
                    attrs_vector = v[1]
                    user_tag = bytes(v[2]) if isinstance(v[2], bytes) else (v[2] if v[2] else b"")
                    
                    if not isinstance(attrs_vector, list):
                        print(f"Error in reflectAttributeValues_2: attrs_vector is not a list. type={type(attrs_vector)}, value={attrs_vector}")
                        reflected_attrs = ReflectedAttributes.from_vector([])
                    else:
                        reflected_attrs = ReflectedAttributes.from_vector(attrs_vector)
                    
                    if self._actor_reference:
                        await self._actor_reference.reflect_attribute_values(object_handle, reflected_attrs, user_tag)
                except Exception as e:
                    print(f"Error in reflectAttributeValues_2 callback: {e}")
                    import traceback
                    traceback.print_exc()
                    raise
            elif method_id == RTICallbackMethodIds.CallbackMethodId_receiveInteraction_1:
                try:
                    v = stream.read_object()
                    if not isinstance(v, list) or len(v) < 3:
                        print(f"Error in receiveInteraction_1: Invalid vector format. v type={type(v)}, v={v}, len={len(v) if isinstance(v, list) else 'N/A'}")
                        return
                    
                    interaction_class = int(v[0]) if v[0] is not None else 0
                    interaction_vector = v[1] if isinstance(v[1], list) else []
                    user_tag = bytes(v[2]) if isinstance(v[2], bytes) else (v[2] if v[2] else b"")
                    
                    # Debug: log the interaction vector format
                    if not interaction_vector:
                        print(f"Warning: receiveInteraction_1: interaction_vector is empty. v={v}")
                        return
                    
                    received_interaction = ReceivedInteraction.from_vector(interaction_vector)
                    if self._actor_reference:
                        await self._actor_reference.receive_interaction(interaction_class, received_interaction, user_tag)
                except Exception as e:
                    print(f"Error in receiveInteraction_1 callback: {e}")
                    import traceback
                    traceback.print_exc()
                    # Don't raise - log and continue to avoid breaking callback loop
                    return
            elif method_id == RTICallbackMethodIds.CallbackMethodId_receiveInteraction_2:
                # receiveInteraction_2 - timestamped version with order type and timestamp
                # v[0] = interaction class (int)
                # v[1] = interaction vector (vector)
                # v[2] = user supplied tag (bytes)
                # v[3] = order type (bytes)
                # v[4] = timestamp (int)
                try:
                    v = stream.read_object()
                    if not isinstance(v, list) or len(v) < 5:
                        print(f"Error in receiveInteraction_2: Invalid vector format. v type={type(v)}, v={v}, len={len(v) if isinstance(v, list) else 'N/A'}")
                        return
                    
                    interaction_class = int(v[0]) if v[0] is not None else 0
                    interaction_vector = v[1] if isinstance(v[1], list) else []
                    user_tag = bytes(v[2]) if isinstance(v[2], bytes) else (v[2] if v[2] else b"")
                    # order_type = bytes(v[3]) if isinstance(v[3], bytes) else (v[3] if v[3] else b"")
                    # timestamp = int(v[4]) if v[4] is not None else 0
                    
                    # Debug: log the interaction vector format
                    if not interaction_vector:
                        print(f"Warning: receiveInteraction_2: interaction_vector is empty. v={v}")
                        return
                    
                    received_interaction = ReceivedInteraction.from_vector(interaction_vector)
                    if self._actor_reference:
                        # For now, call the same method as _1 (timestamped version not yet fully supported in ActorSurrogate interface)
                        await self._actor_reference.receive_interaction(interaction_class, received_interaction, user_tag)
                except Exception as e:
                    print(f"Error in receiveInteraction_2 callback: {e}")
                    import traceback
                    traceback.print_exc()
                    # Don't raise - log and continue to avoid breaking callback loop
                    return
            elif method_id == RTICallbackMethodIds.CallbackMethodId_removeObjectInstance_1:
                # removeObjectInstance_1 - timestamped version with order type and timestamp
                # v[0] = object handle (int)
                # v[1] = user supplied tag (bytes)
                # v[2] = order type (bytes)
                # v[3] = timestamp (int)
                try:
                    v = stream.read_object()
                    if not isinstance(v, list) or len(v) < 4:
                        print(f"Error in removeObjectInstance_1: Invalid vector format. v type={type(v)}, v={v}, len={len(v) if isinstance(v, list) else 'N/A'}")
                        return
                    
                    object_handle = int(v[0]) if v[0] is not None else 0
                    user_tag = bytes(v[1]) if isinstance(v[1], bytes) else (v[1] if v[1] else b"")
                    # order_type = bytes(v[2]) if isinstance(v[2], bytes) else (v[2] if v[2] else b"")
                    # timestamp = int(v[3]) if v[3] is not None else 0
                    
                    if self._actor_reference:
                        # For now, call the same method as _2 (timestamped version not yet fully supported in ActorSurrogate interface)
                        await self._actor_reference.remove_object_instance(object_handle, user_tag)
                except Exception as e:
                    print(f"Error in removeObjectInstance_1 callback: {e}")
                    import traceback
                    traceback.print_exc()
                    raise
            elif method_id == RTICallbackMethodIds.CallbackMethodId_removeObjectInstance_2:
                try:
                    v = stream.read_object()
                    if not isinstance(v, list) or len(v) < 2:
                        print(f"Error in removeObjectInstance_2: Invalid vector format. v type={type(v)}, v={v}")
                        return
                    
                    object_handle = int(v[0]) if v[0] is not None else 0
                    user_tag = bytes(v[1]) if isinstance(v[1], bytes) else (v[1] if v[1] else b"")
                    
                    if self._actor_reference:
                        await self._actor_reference.remove_object_instance(object_handle, user_tag)
                except Exception as e:
                    print(f"Error in removeObjectInstance_2 callback: {e}")
                    import traceback
                    traceback.print_exc()
                    raise
            elif method_id == RTICallbackMethodIds.CallbackMethodId_attributesInScope:
                try:
                    v = stream.read_object()
                    if not isinstance(v, list) or len(v) < 2:
                        print(f"Error in attributesInScope: Invalid vector format. v type={type(v)}, v={v}")
                        return
                    
                    object_handle = int(v[0]) if v[0] is not None else 0
                    handles_list = v[1]
                    if isinstance(handles_list, list):
                        handles = [int(h) for h in handles_list if isinstance(h, (int, type(None))) and h is not None]
                    else:
                        handles = []
                    attr_set = AttributeHandleSetFactory.create(handles)
                    
                    if self._actor_reference:
                        await self._actor_reference.attributes_in_scope(object_handle, attr_set)
                except Exception as e:
                    print(f"Error in attributesInScope callback: {e}")
                    import traceback
                    traceback.print_exc()
                    raise
            elif method_id == RTICallbackMethodIds.CallbackMethodId_attributesOutOfScope:
                try:
                    v = stream.read_object()
                    if not isinstance(v, list) or len(v) < 2:
                        print(f"Error in attributesOutOfScope: Invalid vector format. v type={type(v)}, v={v}")
                        return
                    
                    object_handle = int(v[0]) if v[0] is not None else 0
                    handles_list = v[1]
                    if isinstance(handles_list, list):
                        handles = [int(h) for h in handles_list if isinstance(h, (int, type(None))) and h is not None]
                    else:
                        handles = []
                    attr_set = AttributeHandleSetFactory.create(handles)
                    
                    if self._actor_reference:
                        await self._actor_reference.attributes_out_of_scope(object_handle, attr_set)
                except Exception as e:
                    print(f"Error in attributesOutOfScope callback: {e}")
                    import traceback
                    traceback.print_exc()
                    raise
            elif method_id == RTICallbackMethodIds.CallbackMethodId_provideAttributeValueUpdate:
                try:
                    v = stream.read_object()
                    if isinstance(v, list) and len(v) >= 2:
                        # v[1] should be an int array array (list of ints)
                        handles_list = v[1]
                        if isinstance(handles_list, list):
                            # Ensure all elements are ints
                            handles = [int(h) for h in handles_list if isinstance(h, (int, type(None))) and h is not None]
                        else:
                            handles = []
                        attr_set = AttributeHandleSetFactory.create(handles)
                        await self._actor_reference.provide_attribute_value_update(int(v[0]), attr_set)
                except Exception as e:
                    print(f"Error in provideAttributeValueUpdate callback: {e}, v type={type(v) if 'v' in locals() else 'N/A'}, v={v if 'v' in locals() else 'N/A'}")
                    raise
            elif method_id == RTICallbackMethodIds.CallbackMethodId_turnUpdatesOnForObjectInstance:
                try:
                    v = stream.read_object()
                    if not isinstance(v, list) or len(v) < 2:
                        print(f"Error in turnUpdatesOnForObjectInstance: Invalid vector format. v type={type(v)}, v={v}")
                        return
                    
                    object_handle = int(v[0]) if v[0] is not None else 0
                    handles_list = v[1]
                    if isinstance(handles_list, list):
                        handles = [int(h) for h in handles_list if isinstance(h, (int, type(None))) and h is not None]
                    else:
                        handles = []
                    attr_set = AttributeHandleSetFactory.create(handles)
                    
                    if self._actor_reference:
                        await self._actor_reference.turn_updates_on_for_object_instance(object_handle, attr_set)
                except Exception as e:
                    print(f"Error in turnUpdatesOnForObjectInstance callback: {e}")
                    import traceback
                    traceback.print_exc()
                    raise
            elif method_id == RTICallbackMethodIds.CallbackMethodId_turnUpdatesOffForObjectInstance:
                try:
                    v = stream.read_object()
                    if not isinstance(v, list) or len(v) < 2:
                        print(f"Error in turnUpdatesOffForObjectInstance: Invalid vector format. v type={type(v)}, v={v}")
                        return
                    
                    object_handle = int(v[0]) if v[0] is not None else 0
                    handles_list = v[1]
                    if isinstance(handles_list, list):
                        handles = [int(h) for h in handles_list if isinstance(h, (int, type(None))) and h is not None]
                    else:
                        handles = []
                    attr_set = AttributeHandleSetFactory.create(handles)
                    
                    if self._actor_reference:
                        await self._actor_reference.turn_updates_off_for_object_instance(object_handle, attr_set)
                except Exception as e:
                    print(f"Error in turnUpdatesOffForObjectInstance callback: {e}")
                    import traceback
                    traceback.print_exc()
                    raise
            elif method_id == RTICallbackMethodIds.CallbackMethodId_requestAttributeOwnershipAssumption:
                try:
                    v = stream.read_object()
                    if not isinstance(v, list) or len(v) < 3:
                        return
                    handles_list = v[1]
                    if isinstance(handles_list, list):
                        handles = [int(h) for h in handles_list if isinstance(h, (int, type(None))) and h is not None]
                    else:
                        handles = []
                    attr_set = AttributeHandleSetFactory.create(handles)
                    user_tag = bytes(v[2]) if isinstance(v[2], bytes) else (v[2] if v[2] else b"")
                    if self._actor_reference:
                        await self._actor_reference.request_attribute_ownership_assumption(int(v[0]), attr_set, user_tag)
                except Exception as e:
                    print(f"Error in requestAttributeOwnershipAssumption callback: {e}")
                    import traceback
                    traceback.print_exc()
                    raise
            elif method_id == RTICallbackMethodIds.CallbackMethodId_attributeOwnershipDivestitureNotification:
                try:
                    v = stream.read_object()
                    if not isinstance(v, list) or len(v) < 2:
                        return
                    handles_list = v[1]
                    if isinstance(handles_list, list):
                        handles = [int(h) for h in handles_list if isinstance(h, (int, type(None))) and h is not None]
                    else:
                        handles = []
                    attr_set = AttributeHandleSetFactory.create(handles)
                    if self._actor_reference:
                        await self._actor_reference.attribute_ownership_divestiture_notification(int(v[0]), attr_set)
                except Exception as e:
                    print(f"Error in attributeOwnershipDivestitureNotification callback: {e}")
                    import traceback
                    traceback.print_exc()
                    raise
            elif method_id == RTICallbackMethodIds.CallbackMethodId_attributeOwnershipAcquisitionNotification:
                try:
                    v = stream.read_object()
                    if not isinstance(v, list) or len(v) < 2:
                        return
                    handles_list = v[1]
                    if isinstance(handles_list, list):
                        handles = [int(h) for h in handles_list if isinstance(h, (int, type(None))) and h is not None]
                    else:
                        handles = []
                    attr_set = AttributeHandleSetFactory.create(handles)
                    if self._actor_reference:
                        await self._actor_reference.attribute_ownership_acquisition_notification(int(v[0]), attr_set)
                except Exception as e:
                    print(f"Error in attributeOwnershipAcquisitionNotification callback: {e}")
                    import traceback
                    traceback.print_exc()
                    raise
            elif method_id == RTICallbackMethodIds.CallbackMethodId_attributeOwnershipUnavailable:
                try:
                    v = stream.read_object()
                    if not isinstance(v, list) or len(v) < 2:
                        return
                    handles_list = v[1]
                    if isinstance(handles_list, list):
                        handles = [int(h) for h in handles_list if isinstance(h, (int, type(None))) and h is not None]
                    else:
                        handles = []
                    attr_set = AttributeHandleSetFactory.create(handles)
                    if self._actor_reference:
                        await self._actor_reference.attribute_ownership_unavailable(int(v[0]), attr_set)
                except Exception as e:
                    print(f"Error in attributeOwnershipUnavailable callback: {e}")
                    import traceback
                    traceback.print_exc()
                    raise
            elif method_id == RTICallbackMethodIds.CallbackMethodId_requestAttributeOwnershipRelease:
                try:
                    v = stream.read_object()
                    if not isinstance(v, list) or len(v) < 3:
                        return
                    handles_list = v[1]
                    if isinstance(handles_list, list):
                        handles = [int(h) for h in handles_list if isinstance(h, (int, type(None))) and h is not None]
                    else:
                        handles = []
                    attr_set = AttributeHandleSetFactory.create(handles)
                    user_tag = bytes(v[2]) if isinstance(v[2], bytes) else (v[2] if v[2] else b"")
                    if self._actor_reference:
                        await self._actor_reference.request_attribute_ownership_release(int(v[0]), attr_set, user_tag)
                except Exception as e:
                    print(f"Error in requestAttributeOwnershipRelease callback: {e}")
                    import traceback
                    traceback.print_exc()
                    raise
            elif method_id == RTICallbackMethodIds.CallbackMethodId_confirmAttributeOwnershipAcquisitionCancellation:
                try:
                    v = stream.read_object()
                    if not isinstance(v, list) or len(v) < 2:
                        return
                    handles_list = v[1]
                    if isinstance(handles_list, list):
                        handles = [int(h) for h in handles_list if isinstance(h, (int, type(None))) and h is not None]
                    else:
                        handles = []
                    attr_set = AttributeHandleSetFactory.create(handles)
                    if self._actor_reference:
                        await self._actor_reference.confirm_attribute_ownership_acquisition_cancellation(int(v[0]), attr_set)
                except Exception as e:
                    print(f"Error in confirmAttributeOwnershipAcquisitionCancellation callback: {e}")
                    import traceback
                    traceback.print_exc()
                    raise
            elif method_id == RTICallbackMethodIds.CallbackMethodId_informAttributeOwnership:
                try:
                    v = stream.read_object()
                    if not isinstance(v, list) or len(v) < 3:
                        return
                    if self._actor_reference:
                        await self._actor_reference.inform_attribute_ownership(int(v[0]), int(v[1]), int(v[2]))
                except Exception as e:
                    print(f"Error in informAttributeOwnership callback: {e}")
                    import traceback
                    traceback.print_exc()
                    raise
            elif method_id == RTICallbackMethodIds.CallbackMethodId_attributeIsNotOwned:
                try:
                    v = stream.read_object()
                    if not isinstance(v, list) or len(v) < 2:
                        return
                    if self._actor_reference:
                        await self._actor_reference.attribute_is_not_owned(int(v[0]), int(v[1]))
                except Exception as e:
                    print(f"Error in attributeIsNotOwned callback: {e}")
                    import traceback
                    traceback.print_exc()
                    raise
            elif method_id == RTICallbackMethodIds.CallbackMethodId_attributeOwnedByRTI:
                try:
                    v = stream.read_object()
                    if not isinstance(v, list) or len(v) < 2:
                        return
                    if self._actor_reference:
                        await self._actor_reference.attribute_owned_by_rti(int(v[0]), int(v[1]))
                except Exception as e:
                    print(f"Error in attributeOwnedByRTI callback: {e}")
                    import traceback
                    traceback.print_exc()
                    raise
            else:
                # Unknown callback method ID - log it but don't crash
                print(f"WARNING: Unknown callback method ID: {method_id} (0x{method_id:02x}). This callback is not handled.")
                # Try to read the object anyway to consume it from the stream
                try:
                    obj = stream.read_object()
                    print(f"  Consumed object from unknown callback: type={type(obj)}, value={obj}")
                except Exception as e:
                    print(f"  Failed to consume object from unknown callback: {e}")
        except Exception as e:
            print(f"Error dispatching callback {method_id}: {e}")
            import traceback
            traceback.print_exc()

