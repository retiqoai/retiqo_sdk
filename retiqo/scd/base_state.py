# Copyright 2026 Loreum Digital Inc
# SPDX-License-Identifier: Apache-2.0
"""
BaseState - manages state channel state
"""
from typing import Dict, Optional, Callable, List, Any, TYPE_CHECKING
from retiqo.rti.rti_surrogate import RTISurrogate
from retiqo.rti.consensus_state import ConsensusState
from retiqo.rti.actor_handle_set import ActorHandleSet, ActorHandleSetFactory
from retiqo.crypto.ec_key import ECKey
from retiqo.crypto.hash_util import HashUtil
if TYPE_CHECKING:
    from retiqo.scd.base_entity import BaseEntity
    from retiqo.scd.base_interaction import BaseInteraction
from retiqo.scd.exceptions import EntityException
from retiqo.exceptions import (
    ActorNotExecutionMember,
    SaveInProgress,
    RestoreInProgress,
    RTIInternalError,
    ObjectNotKnown,
    AttributeNotDefined,
    ConsensusLabelNotAnnounced,
)
import asyncio


class BaseState:
    """Base state for state channel"""

    # Event handler type definitions
    StartRegistrationForObjectClassEvent = Callable[[int], None]
    StopRegistrationForObjectClassEvent = Callable[[int], None]
    RemoveObjectInstanceEvent = Callable[[Any], None]  # BaseEntity
    ConsensusPointRegistrationFailedEvent = Callable[[str], None]
    ConsensusPointRegistrationSucceededEvent = Callable[[str], None]
    AnnounceConsensusPointEvent = Callable[[str, bytes], None]
    StateChannelInConsensusEvent = Callable[[str, ConsensusState], None]
    ReceivedInteractionEvent = Callable[[Any, bytes], None]  # BaseInteraction
    DiscoverObjectInstanceEvent = Callable[[Any], None]  # BaseEntity

    def __init__(self, rti: RTISurrogate, private_key: bytes):
        """Initialize base state"""
        self.rti = rti
        self.entities: Dict[int, Any] = {}  # Dict[int, BaseEntity]
        self.private_key = private_key

        # Event handlers
        self.start_registration_for_object_class_event_handler: Optional[BaseState.StartRegistrationForObjectClassEvent] = None
        self.stop_registration_for_object_class_event_handler: Optional[BaseState.StopRegistrationForObjectClassEvent] = None
        self.remove_object_instance_event_handler: Optional[BaseState.RemoveObjectInstanceEvent] = None
        self.consensus_point_registration_failed_event_handler: Optional[BaseState.ConsensusPointRegistrationFailedEvent] = None
        self.consensus_point_registration_succeeded_event_handler: Optional[BaseState.ConsensusPointRegistrationSucceededEvent] = None
        self.consensus_point_announced_event_handler: Optional[BaseState.AnnounceConsensusPointEvent] = None
        self.state_channel_in_consensus_event_handler: Optional[BaseState.StateChannelInConsensusEvent] = None
        self.discover_object_instance_event_handler: Optional[BaseState.DiscoverObjectInstanceEvent] = None
        self.received_interaction_event_handler: Optional[BaseState.ReceivedInteractionEvent] = None

    def get_rti(self) -> RTISurrogate:
        """Get RTI surrogate"""
        return self.rti

    def get_private_key(self) -> bytes:
        """Get private key"""
        return self.private_key

    def get_entities(self) -> Dict[int, Any]:  # Dict[int, BaseEntity]
        """Get entities map"""
        return self.entities

    def create_object_instance(self, object_class: int) -> Optional[Any]:  # Optional[BaseEntity]
        """Create object instance - override in derived class"""
        return None

    async def register_consensus_point(self, label: str, tag: bytes) -> None:
        """Register consensus point"""
        try:
            await self.rti.register_state_channel_consensus_point(label, tag)
        except (ActorNotExecutionMember, SaveInProgress, RestoreInProgress, RTIInternalError, ObjectNotKnown, AttributeNotDefined) as e:
            raise EntityException(str(e), e)

    async def register_consensus_point_with_set(
        self, label: str, tag: bytes, actor_handle_array: List[int]
    ) -> None:
        """Register consensus point with actor set"""
        try:
            actor_set = ActorHandleSetFactory.create(actor_handle_array)
            await self.rti.register_state_channel_consensus_point_with_set(label, tag, actor_set)
        except (ActorNotExecutionMember, SaveInProgress, RestoreInProgress, RTIInternalError, ObjectNotKnown, AttributeNotDefined) as e:
            raise EntityException(str(e), e)

    async def consensus_point_achieved(self, label: str, consensus_value: bytes) -> None:
        """Achieve consensus point"""
        try:
            # Generate consensus hash
            consensus_hash = HashUtil.sha3(consensus_value)
            
            # Sign consensus hash (not the value)
            signature = self._sign(consensus_hash, self.private_key)
            
            await self.rti.consensus_point_achieved(label, consensus_hash, signature)
        except (ConsensusLabelNotAnnounced, ActorNotExecutionMember, SaveInProgress, RestoreInProgress, RTIInternalError) as e:
            raise EntityException(str(e), e)

    def _sign(self, hash_bytes: bytes, priv_key_bytes: bytes) -> bytes:
        """Sign hash with private key"""
        key = ECKey.from_private(priv_key_bytes)
        signature = key.sign(hash_bytes)
        return signature.to_byte_array()

    def get_state_element_id(self, object_name: str, attribute_handle: int) -> bytes:
        """Create element ID for Merkle tree"""
        prefix = object_name.encode("utf-8")
        attribute = attribute_handle.to_bytes(4, "big")
        element_id = prefix + attribute
        return element_id

    # Event handler setters/getters
    def set_start_registration_for_object_class_event_handler(self, handler: StartRegistrationForObjectClassEvent) -> None:
        self.start_registration_for_object_class_event_handler = handler

    def set_stop_registration_for_object_class_event_handler(self, handler: StopRegistrationForObjectClassEvent) -> None:
        self.stop_registration_for_object_class_event_handler = handler

    def set_remove_object_instance_event_handler(self, handler: RemoveObjectInstanceEvent) -> None:
        self.remove_object_instance_event_handler = handler

    def set_consensus_point_registration_failed_event_handler(self, handler: ConsensusPointRegistrationFailedEvent) -> None:
        self.consensus_point_registration_failed_event_handler = handler

    def set_consensus_point_registration_succeeded_event_handler(self, handler: ConsensusPointRegistrationSucceededEvent) -> None:
        self.consensus_point_registration_succeeded_event_handler = handler

    def set_consensus_point_announced_event_handler(self, handler: AnnounceConsensusPointEvent) -> None:
        self.consensus_point_announced_event_handler = handler

    def set_state_channel_in_consensus_event_handler(self, handler: StateChannelInConsensusEvent) -> None:
        self.state_channel_in_consensus_event_handler = handler

    def set_discover_object_instance_event_handler(self, handler: DiscoverObjectInstanceEvent) -> None:
        self.discover_object_instance_event_handler = handler

