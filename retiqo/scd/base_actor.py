# Copyright 2026 Loreum Digital Inc
# SPDX-License-Identifier: Apache-2.0
"""
BaseActor - implements ActorSurrogate and provides higher-level API
"""
from typing import Optional, Dict, List
from retiqo.scd.base_state import BaseState
from retiqo.scd.base_entity import BaseEntity
from retiqo.scd.base_interaction import BaseInteraction
from retiqo.scd.exceptions import ActorException
from retiqo.rti.rti_surrogate import RTISurrogate
from retiqo.rti.actor_surrogate import ActorSurrogate
from retiqo.rti.consensus_state import ConsensusState
from retiqo.rti.reflected_attributes import ReflectedAttributes
from retiqo.rti.received_interaction import ReceivedInteraction
from retiqo.rti.attribute_handle_set import AttributeHandleSet
from retiqo.exceptions import *


class BaseActor(ActorSurrogate):
    """Base actor implementing ActorSurrogate"""

    def __init__(self, rti: RTISurrogate, base_state: BaseState, actor_name: str):
        """Initialize base actor"""
        self.rti = rti
        self.base_state = base_state
        self.actor_name = actor_name
        self.sc_exec_name: Optional[str] = None
        self._remote_actor_sgx_public_key: Optional[bytes] = None

    def get_rti(self) -> RTISurrogate:
        """Get RTI surrogate"""
        return self.rti

    def set_rti(self, rti: RTISurrogate) -> None:
        """Set RTI surrogate"""
        self.rti = rti

    def get_base_state(self) -> BaseState:
        """Get base state"""
        return self.base_state

    def set_base_state(self, base_state: BaseState) -> None:
        """Set base state"""
        self.base_state = base_state

    def create_interaction_instance(self, interaction_class: int) -> Optional[BaseInteraction]:
        """Create interaction instance - override in derived class"""
        return None

    async def get_state_channel_executions(self) -> List[str]:
        """Get state channel executions"""
        try:
            executions = await self.rti.get_state_channel_executions()
            return executions if executions else []
        except Exception as e:
            raise ActorException(str(e), e)

    async def join_state_channel_execution(
        self, sc_execution_name: str, actor_type: str, public_key: bytes
    ) -> bytes:
        """Join state channel execution"""
        try:
            remote_key = await self.rti.join_state_channel_execution(
                actor_type, sc_execution_name, public_key, self
            )
            self.sc_exec_name = sc_execution_name
            self._remote_actor_sgx_public_key = remote_key
            return remote_key
        except Exception as e:
            raise ActorException(str(e), e)

    # ActorSurrogate implementation
    async def set_base_state(self, base_state: BaseState) -> None:
        """Set base state"""
        self.base_state = base_state

    async def get_base_state(self) -> Optional[BaseState]:
        """Get base state"""
        return self.base_state

    async def consensus_point_registration_failed(self, consensus_point_label: str) -> None:
        """Consensus point registration failed"""
        handler = self.base_state.consensus_point_registration_failed_event_handler
        if handler:
            await handler(consensus_point_label)

    async def consensus_point_registration_succeeded(self, consensus_point_label: str) -> None:
        """Consensus point registration succeeded"""
        handler = self.base_state.consensus_point_registration_succeeded_event_handler
        if handler:
            await handler(consensus_point_label)

    async def announce_consensus_point(self, consensus_point_label: str, user_supplied_tag: bytes) -> None:
        """Announce consensus point"""
        handler = self.base_state.consensus_point_announced_event_handler
        if handler:
            await handler(consensus_point_label, user_supplied_tag)

    async def state_channel_in_consensus(
        self, consensus_point_label: str, consensus_state: ConsensusState
    ) -> None:
        """State channel in consensus"""
        handler = self.base_state.state_channel_in_consensus_event_handler
        if handler:
            await handler(consensus_point_label, consensus_state)

    async def initiate_actor_save(self, label: str) -> None:
        """Initiate actor save"""
        pass  # Override in derived class

    async def state_channel_saved(self) -> None:
        """State channel saved"""
        pass  # Override in derived class

    async def state_channel_not_saved(self) -> None:
        """State channel not saved"""
        pass  # Override in derived class

    async def request_state_channel_restore_succeeded(self, label: str) -> None:
        """Request state channel restore succeeded"""
        pass  # Override in derived class

    async def request_state_channel_restore_failed(self, label: str, reason: str) -> None:
        """Request state channel restore failed"""
        pass  # Override in derived class

    async def state_channel_restore_begun(self) -> None:
        """State channel restore begun"""
        pass  # Override in derived class

    async def initiate_actor_restore(self, label: str, actor_handle: int) -> None:
        """Initiate actor restore"""
        pass  # Override in derived class

    async def state_channel_restored(self) -> None:
        """State channel restored"""
        pass  # Override in derived class

    async def state_channel_not_restored(self) -> None:
        """State channel not restored"""
        pass  # Override in derived class

    async def start_registration_for_object_class(self, the_class: int) -> None:
        """Start registration for object class"""
        handler = self.base_state.start_registration_for_object_class_event_handler
        if handler:
            await handler(the_class)

    async def stop_registration_for_object_class(self, the_class: int) -> None:
        """Stop registration for object class"""
        handler = self.base_state.stop_registration_for_object_class_event_handler
        if handler:
            await handler(the_class)

    async def turn_interactions_on(self, the_handle: int) -> None:
        """Turn interactions on"""
        pass  # Override in derived class

    async def turn_interactions_off(self, the_handle: int) -> None:
        """Turn interactions off"""
        pass  # Override in derived class

    async def discover_object_instance(
        self, the_object: int, the_object_class: int, object_name: Optional[str]
    ) -> None:
        """Discover object instance"""
        entity = self.base_state.get_entities().get(the_object)
        if entity is None:
            # Create entity if not exists
            entity = self.base_state.create_object_instance(the_object_class)
            if entity:
                entity.set_handle(the_object)
                if object_name:
                    entity.set_name(object_name)
                self.base_state.get_entities()[the_object] = entity

        handler = self.base_state.discover_object_instance_event_handler
        if handler and entity:
            await handler(entity)

    async def reflect_attribute_values(
        self, the_object: int, the_attributes: ReflectedAttributes, user_supplied_tag: bytes
    ) -> None:
        """Reflect attribute values"""
        entity = self.base_state.get_entities().get(the_object)
        if entity:
            # Update attribute values
            for i in range(the_attributes.size()):
                attr_handle = the_attributes.get_attribute_handle(i)
                value = the_attributes.get_value_reference(i)
                entity.set_attribute_value(attr_handle, value)

            handler = entity.reflect_attribute_values_event_handler
            if handler:
                attr_list = [the_attributes.get_attribute_handle(i) for i in range(the_attributes.size())]
                await handler(attr_list, user_supplied_tag)

    async def receive_interaction(
        self, the_interaction: int, the_parameters: ReceivedInteraction, user_supplied_tag: bytes
    ) -> None:
        """Receive interaction"""
        interaction = self.create_interaction_instance(the_interaction)
        if interaction:
            interaction.set_handle(the_interaction)
            # Set parameter values
            for i in range(the_parameters.size()):
                param_handle = the_parameters.get_parameter_handle(i)
                value = the_parameters.get_value_reference(i)
                interaction.set_parameter_value(param_handle, value)

            handler = self.base_state.get_received_interaction_event_handler()
            if handler:
                await handler(interaction, user_supplied_tag)

    async def remove_object_instance(self, the_object: int, user_supplied_tag: bytes) -> None:
        """Remove object instance"""
        entity = self.base_state.get_entities().get(the_object)
        if entity:
            handler = self.base_state.remove_object_instance_event_handler
            if handler:
                await handler(entity)
            # Remove from entities map
            self.base_state.get_entities().pop(the_object, None)

    async def attributes_in_scope(self, the_object: int, the_attributes: AttributeHandleSet) -> None:
        """Attributes in scope"""
        entity = self.base_state.get_entities().get(the_object)
        if entity:
            handler = entity.attributes_in_scope_event_handler
            if handler:
                attr_list = list(the_attributes.to_list())
                await handler(attr_list)

    async def attributes_out_of_scope(self, the_object: int, the_attributes: AttributeHandleSet) -> None:
        """Attributes out of scope"""
        entity = self.base_state.get_entities().get(the_object)
        if entity:
            handler = entity.attributes_out_of_scope_event_handler
            if handler:
                attr_list = list(the_attributes.to_list())
                await handler(attr_list)

    async def provide_attribute_value_update(
        self, the_object: int, the_attributes: AttributeHandleSet
    ) -> None:
        """Provide attribute value update"""
        entity = self.base_state.get_entities().get(the_object)
        if entity:
            # Request attribute update
            await entity.request_attribute_update(*list(the_attributes.to_list()))

    async def turn_updates_on_for_object_instance(
        self, the_object: int, the_attributes: AttributeHandleSet
    ) -> None:
        """Turn updates on for object instance"""
        pass  # Override in derived class

    async def turn_updates_off_for_object_instance(
        self, the_object: int, the_attributes: AttributeHandleSet
    ) -> None:
        """Turn updates off for object instance"""
        pass  # Override in derived class

    async def request_attribute_ownership_assumption(
        self, the_object: int, the_attributes: AttributeHandleSet, user_supplied_tag: bytes
    ) -> None:
        """Request attribute ownership assumption"""
        entity = self.base_state.get_entities().get(the_object)
        if entity:
            handler = entity.attribute_ownership_assumption_request_handler
            if handler:
                attr_list = list(the_attributes.to_list())
                await handler(attr_list, user_supplied_tag)

    async def attribute_ownership_divestiture_notification(
        self, the_object: int, the_attributes: AttributeHandleSet
    ) -> None:
        """Attribute ownership divestiture notification"""
        entity = self.base_state.get_entities().get(the_object)
        if entity:
            # Update ownership map
            for attr_handle in the_attributes.to_list():
                entity.set_attribute_ownership(attr_handle, False)

            handler = entity.attribute_ownership_divestiture_notification_event_handler
            if handler:
                attr_list = list(the_attributes.to_list())
                await handler(attr_list)

    async def attribute_ownership_acquisition_notification(
        self, the_object: int, the_attributes: AttributeHandleSet
    ) -> None:
        """Attribute ownership acquisition notification"""
        entity = self.base_state.get_entities().get(the_object)
        if entity:
            # Update ownership map
            for attr_handle in the_attributes.to_list():
                entity.set_attribute_ownership(attr_handle, True)

            handler = entity.attribute_ownership_acquisition_notification_event_handler
            if handler:
                attr_list = list(the_attributes.to_list())
                await handler(attr_list)

    async def attribute_ownership_unavailable(
        self, the_object: int, the_attributes: AttributeHandleSet
    ) -> None:
        """Attribute ownership unavailable"""
        entity = self.base_state.get_entities().get(the_object)
        if entity:
            handler = entity.attribute_ownership_unavailable_event_handler
            if handler:
                attr_list = list(the_attributes.to_list())
                await handler(attr_list)

    async def request_attribute_ownership_release(
        self, the_object: int, the_attributes: AttributeHandleSet, user_supplied_tag: bytes
    ) -> None:
        """Request attribute ownership release"""
        entity = self.base_state.get_entities().get(the_object)
        if entity:
            handler = entity.attribute_ownership_release_request_handler
            if handler:
                attr_list = list(the_attributes.to_list())
                await handler(attr_list, user_supplied_tag)

    async def confirm_attribute_ownership_acquisition_cancellation(
        self, the_object: int, the_attributes: AttributeHandleSet
    ) -> None:
        """Confirm attribute ownership acquisition cancellation"""
        entity = self.base_state.get_entities().get(the_object)
        if entity:
            handler = entity.confirm_attribute_ownership_acquisition_cancellation_event_handler
            if handler:
                attr_list = list(the_attributes.to_list())
                await handler(attr_list)

    async def inform_attribute_ownership(
        self, the_object: int, the_attribute: int, the_owner: int
    ) -> None:
        """Inform attribute ownership"""
        entity = self.base_state.get_entities().get(the_object)
        if entity:
            handler = entity.inform_attribute_ownership_handler
            if handler:
                await handler(the_attribute, the_owner)

    async def attribute_is_not_owned(self, the_object: int, the_attribute: int) -> None:
        """Attribute is not owned"""
        entity = self.base_state.get_entities().get(the_object)
        if entity:
            handler = entity.attribute_is_not_owned_event_handler
            if handler:
                await handler(the_attribute)

    async def attribute_owned_by_rti(self, the_object: int, the_attribute: int) -> None:
        """Attribute owned by RTI"""
        entity = self.base_state.get_entities().get(the_object)
        if entity:
            handler = entity.attribute_owned_by_rti_event_handler
            if handler:
                await handler(the_attribute)

