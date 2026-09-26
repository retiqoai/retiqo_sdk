# Copyright 2026 Loreum Digital Inc
# SPDX-License-Identifier: Apache-2.0
"""
ActorSurrogate interface - must be implemented by actors
"""
from abc import ABC, abstractmethod
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from retiqo.scd.base_state import BaseState

from retiqo.rti.consensus_state import ConsensusState
from retiqo.rti.reflected_attributes import ReflectedAttributes
from retiqo.rti.received_interaction import ReceivedInteraction
from retiqo.rti.attribute_handle_set import AttributeHandleSet


class ActorSurrogate(ABC):
    """Interface that actors must implement to receive RTI callbacks"""

    @abstractmethod
    def set_base_state(self, base_state: "BaseState") -> None:
        """Set the base state for this actor"""
        pass

    @abstractmethod
    def get_base_state(self) -> Optional["BaseState"]:
        """Get the base state for this actor"""
        pass

    # State Channel Management Services

    @abstractmethod
    async def consensus_point_registration_failed(self, consensus_point_label: str) -> None:
        """Called when consensus point registration fails"""
        pass

    @abstractmethod
    async def consensus_point_registration_succeeded(self, consensus_point_label: str) -> None:
        """Called when consensus point registration succeeds"""
        pass

    @abstractmethod
    async def announce_consensus_point(
        self, consensus_point_label: str, user_supplied_tag: bytes
    ) -> None:
        """Called when a consensus point is announced"""
        pass

    @abstractmethod
    async def state_channel_in_consensus(
        self, consensus_point_label: str, consensus_state: ConsensusState
    ) -> None:
        """Called when state channel reaches consensus"""
        pass

    @abstractmethod
    async def initiate_actor_save(self, label: str) -> None:
        """Called to initiate actor save"""
        pass

    @abstractmethod
    async def state_channel_saved(self) -> None:
        """Called when state channel is saved"""
        pass

    @abstractmethod
    async def state_channel_not_saved(self) -> None:
        """Called when state channel save fails"""
        pass

    @abstractmethod
    async def request_state_channel_restore_succeeded(self, label: str) -> None:
        """Called when restore request succeeds"""
        pass

    @abstractmethod
    async def request_state_channel_restore_failed(self, label: str, reason: str) -> None:
        """Called when restore request fails"""
        pass

    @abstractmethod
    async def state_channel_restore_begun(self) -> None:
        """Called when restore begins"""
        pass

    @abstractmethod
    async def initiate_actor_restore(self, label: str, actor_handle: int) -> None:
        """Called to initiate actor restore"""
        pass

    @abstractmethod
    async def state_channel_restored(self) -> None:
        """Called when state channel is restored"""
        pass

    @abstractmethod
    async def state_channel_not_restored(self) -> None:
        """Called when state channel restore fails"""
        pass

    # Declaration Management Services

    @abstractmethod
    async def start_registration_for_object_class(self, the_class: int) -> None:
        """Called when registration for object class starts"""
        pass

    @abstractmethod
    async def stop_registration_for_object_class(self, the_class: int) -> None:
        """Called when registration for object class stops"""
        pass

    @abstractmethod
    async def turn_interactions_on(self, the_handle: int) -> None:
        """Called to turn interactions on"""
        pass

    @abstractmethod
    async def turn_interactions_off(self, the_handle: int) -> None:
        """Called to turn interactions off"""
        pass

    # Object Management Services

    @abstractmethod
    async def discover_object_instance(
        self, the_object: int, the_object_class: int, object_name: str
    ) -> None:
        """Called when an object instance is discovered"""
        pass

    @abstractmethod
    async def reflect_attribute_values(
        self,
        the_object: int,
        the_attributes: ReflectedAttributes,
        user_supplied_tag: bytes,
    ) -> None:
        """Called when attribute values are reflected"""
        pass

    @abstractmethod
    async def receive_interaction(
        self,
        interaction_class: int,
        the_interaction: ReceivedInteraction,
        user_supplied_tag: bytes,
    ) -> None:
        """Called when an interaction is received"""
        pass

    @abstractmethod
    async def remove_object_instance(self, the_object: int, user_supplied_tag: bytes) -> None:
        """Called when an object instance is removed"""
        pass

    @abstractmethod
    async def attributes_in_scope(
        self, the_object: int, the_attributes: AttributeHandleSet
    ) -> None:
        """Called when attributes come into scope"""
        pass

    @abstractmethod
    async def attributes_out_of_scope(
        self, the_object: int, the_attributes: AttributeHandleSet
    ) -> None:
        """Called when attributes go out of scope"""
        pass

    @abstractmethod
    async def provide_attribute_value_update(
        self, the_object: int, the_attributes: AttributeHandleSet
    ) -> None:
        """Called to provide attribute value update"""
        pass

    @abstractmethod
    async def turn_updates_on_for_object_instance(
        self, the_object: int, the_attributes: AttributeHandleSet
    ) -> None:
        """Called to turn updates on for object instance"""
        pass

    @abstractmethod
    async def turn_updates_off_for_object_instance(
        self, the_object: int, the_attributes: AttributeHandleSet
    ) -> None:
        """Called to turn updates off for object instance"""
        pass

    # Ownership Management Services

    @abstractmethod
    async def request_attribute_ownership_assumption(
        self,
        the_object: int,
        offered_attributes: AttributeHandleSet,
        user_supplied_tag: bytes,
    ) -> None:
        """Called to request attribute ownership assumption"""
        pass

    @abstractmethod
    async def attribute_ownership_divestiture_notification(
        self, the_object: int, released_attributes: AttributeHandleSet
    ) -> None:
        """Called when attribute ownership divestiture is notified"""
        pass

    @abstractmethod
    async def attribute_ownership_acquisition_notification(
        self, the_object: int, secured_attributes: AttributeHandleSet
    ) -> None:
        """Called when attribute ownership acquisition is notified"""
        pass

    @abstractmethod
    async def attribute_ownership_unavailable(
        self, the_object: int, the_attributes: AttributeHandleSet
    ) -> None:
        """Called when attribute ownership is unavailable"""
        pass

    @abstractmethod
    async def request_attribute_ownership_release(
        self,
        the_object: int,
        candidate_attributes: AttributeHandleSet,
        user_supplied_tag: bytes,
    ) -> None:
        """Called to request attribute ownership release"""
        pass

    @abstractmethod
    async def confirm_attribute_ownership_acquisition_cancellation(
        self, the_object: int, the_attributes: AttributeHandleSet
    ) -> None:
        """Called to confirm attribute ownership acquisition cancellation"""
        pass

    @abstractmethod
    async def inform_attribute_ownership(
        self, the_object: int, the_attribute: int, the_owner: int
    ) -> None:
        """Called to inform about attribute ownership"""
        pass

    @abstractmethod
    async def attribute_is_not_owned(self, the_object: int, the_attribute: int) -> None:
        """Called when attribute is not owned"""
        pass

    @abstractmethod
    async def attribute_owned_by_rti(self, the_object: int, the_attribute: int) -> None:
        """Called when attribute is owned by RTI"""
        pass

