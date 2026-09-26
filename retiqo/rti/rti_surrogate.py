# Copyright 2026 Loreum Digital Inc
# SPDX-License-Identifier: Apache-2.0
"""
RTISurrogate interface - main RTI API
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from retiqo.rti.actor_surrogate import ActorSurrogate
from retiqo.rti.attribute_handle_set import AttributeHandleSet
from retiqo.rti.actor_handle_set import ActorHandleSet
from retiqo.rti.region import Region
from retiqo.rti.supplied_attributes import SuppliedAttributes
from retiqo.rti.supplied_parameters import SuppliedParameters


class RTISurrogate(ABC):
    """Main RTI interface - provides all RTI services"""

    # State Channel Management Services

    @abstractmethod
    async def create_state_channel_execution(
        self, execution_name: str, scd: str
    ) -> None:
        """Create a new state channel execution"""
        pass

    @abstractmethod
    async def destroy_state_channel_execution(self, execution_name: str) -> None:
        """Destroy a state channel execution"""
        pass

    @abstractmethod
    async def get_state_channel_executions(self) -> List[str]:
        """Get list of state channel executions"""
        pass

    @abstractmethod
    async def join_state_channel_execution(
        self,
        actor_type: str,
        state_channel_execution_name: str,
        public_key: bytes,
        actor_reference: ActorSurrogate,
    ) -> bytes:
        """Join a state channel execution"""
        pass

    @abstractmethod
    async def resign_state_channel_execution(self, resign_action: int) -> None:
        """Resign from state channel execution"""
        pass

    @abstractmethod
    async def register_state_channel_consensus_point(
        self, consensus_point_label: str, user_supplied_tag: bytes
    ) -> None:
        """Register a consensus point"""
        pass

    @abstractmethod
    async def register_state_channel_consensus_point_with_set(
        self,
        consensus_point_label: str,
        user_supplied_tag: bytes,
        consensus_set: ActorHandleSet,
    ) -> None:
        """Register a consensus point with actor set"""
        pass

    @abstractmethod
    async def consensus_point_achieved(
        self, consensus_point_label: str, consensus_hash: bytes, signature: bytes
    ) -> None:
        """Achieve a consensus point"""
        pass

    # Save/Restore Services

    @abstractmethod
    async def request_state_channel_save(self, label: str) -> None:
        """Request state channel save"""
        pass

    @abstractmethod
    async def request_state_channel_save_with_set(
        self, label: str, actor_set: ActorHandleSet
    ) -> None:
        """Request state channel save for actor set"""
        pass

    @abstractmethod
    async def actor_save_begun(self) -> None:
        """Notify that actor save has begun"""
        pass

    @abstractmethod
    async def actor_save_complete(self) -> None:
        """Notify that actor save is complete"""
        pass

    @abstractmethod
    async def actor_save_not_complete(self) -> None:
        """Notify that actor save is not complete"""
        pass

    @abstractmethod
    async def request_state_channel_restore(self, label: str) -> None:
        """Request state channel restore"""
        pass

    @abstractmethod
    async def actor_restore_complete(self) -> None:
        """Notify that actor restore is complete"""
        pass

    @abstractmethod
    async def actor_restore_not_complete(self) -> None:
        """Notify that actor restore is not complete"""
        pass

    # Declaration Management Services

    @abstractmethod
    async def publish_object_class(
        self, the_class: int, attribute_list: AttributeHandleSet
    ) -> None:
        """Publish an object class"""
        pass

    @abstractmethod
    async def unpublish_object_class(self, the_class: int) -> None:
        """Unpublish an object class"""
        pass

    @abstractmethod
    async def publish_interaction_class(self, the_interaction: int) -> None:
        """Publish an interaction class"""
        pass

    @abstractmethod
    async def unpublish_interaction_class(self, the_interaction: int) -> None:
        """Unpublish an interaction class"""
        pass

    @abstractmethod
    async def subscribe_object_class_attributes(
        self, the_class: int, attribute_list: AttributeHandleSet
    ) -> None:
        """Subscribe to object class attributes"""
        pass

    @abstractmethod
    async def subscribe_object_class_attributes_passively(
        self, the_class: int, attribute_list: AttributeHandleSet
    ) -> None:
        """Subscribe to object class attributes passively"""
        pass

    @abstractmethod
    async def unsubscribe_object_class(self, the_class: int) -> None:
        """Unsubscribe from object class"""
        pass

    @abstractmethod
    async def subscribe_interaction_class(self, the_class: int) -> None:
        """Subscribe to interaction class"""
        pass

    @abstractmethod
    async def subscribe_interaction_class_passively(self, the_class: int) -> None:
        """Subscribe to interaction class passively"""
        pass

    @abstractmethod
    async def unsubscribe_interaction_class(self, the_class: int) -> None:
        """Unsubscribe from interaction class"""
        pass

    # Object Management Services

    @abstractmethod
    async def register_object_instance(
        self, the_class: int, the_object_name: Optional[str] = None
    ) -> int:
        """Register an object instance"""
        pass

    @abstractmethod
    async def register_object_instance_with_region(
        self,
        the_class: int,
        the_object_name: Optional[str],
        the_attributes: AttributeHandleSet,
        the_regions: List[Region],
    ) -> int:
        """Register an object instance with region"""
        pass

    @abstractmethod
    async def update_attribute_values(
        self,
        the_object: int,
        the_attributes: SuppliedAttributes,
        user_supplied_tag: bytes,
    ) -> None:
        """Update attribute values"""
        pass

    @abstractmethod
    async def update_attribute_values_with_region(
        self,
        the_object: int,
        the_attributes: SuppliedAttributes,
        user_supplied_tag: bytes,
        the_region: Region,
    ) -> None:
        """Update attribute values with region"""
        pass

    @abstractmethod
    async def send_interaction(
        self,
        the_interaction: int,
        the_parameters: SuppliedParameters,
        user_supplied_tag: bytes,
    ) -> None:
        """Send an interaction"""
        pass

    @abstractmethod
    async def send_interaction_with_region(
        self,
        the_interaction: int,
        the_parameters: SuppliedParameters,
        user_supplied_tag: bytes,
        the_region: Region,
    ) -> None:
        """Send an interaction with region"""
        pass

    @abstractmethod
    async def delete_object_instance(
        self, the_object: int, user_supplied_tag: bytes
    ) -> None:
        """Delete an object instance"""
        pass

    # Region Management Services

    @abstractmethod
    async def create_region(self, space_handle: int, number_of_extents: int) -> Region:
        """Create a region"""
        pass

    @abstractmethod
    async def delete_region(self, the_region: Region) -> None:
        """Delete a region"""
        pass

    @abstractmethod
    async def notify_of_region_modification(self, the_region: Region) -> None:
        """Notify of region modification"""
        pass

    @abstractmethod
    async def get_region_token(self, the_region: Region) -> int:
        """Get region token"""
        pass

    @abstractmethod
    async def get_region(self, region_token: int) -> Region:
        """Get region from token"""
        pass

    @abstractmethod
    async def associate_region_for_updates(
        self,
        the_region: Region,
        the_object: int,
        the_attributes: AttributeHandleSet,
    ) -> None:
        """Associate region for updates"""
        pass

    @abstractmethod
    async def unassociate_region_for_updates(
        self,
        the_region: Region,
        the_object: int,
        the_attributes: Optional[AttributeHandleSet] = None,
    ) -> None:
        """Unassociate region for updates"""
        pass

    @abstractmethod
    async def subscribe_object_class_attributes_with_region(
        self,
        the_class: int,
        attribute_list: AttributeHandleSet,
        the_region: Region,
    ) -> None:
        """Subscribe to object class attributes with region"""
        pass

    @abstractmethod
    async def subscribe_interaction_class_with_region(
        self, the_class: int, the_region: Region
    ) -> None:
        """Subscribe to interaction class with region"""
        pass

    @abstractmethod
    async def request_class_attribute_value_update(
        self, the_class: int, the_attributes: AttributeHandleSet
    ) -> None:
        """Request class attribute value update"""
        pass

    @abstractmethod
    async def request_class_attribute_value_update_with_region(
        self,
        the_class: int,
        the_attributes: AttributeHandleSet,
        the_region: Region,
    ) -> None:
        """Request class attribute value update with region"""
        pass

    # Ownership Management Services

    @abstractmethod
    async def attribute_ownership_acquisition_if_available(
        self, the_object: int, desired_attributes: AttributeHandleSet
    ) -> None:
        """Acquire attribute ownership if available"""
        pass

    @abstractmethod
    async def cancel_attribute_ownership_acquisition(
        self, the_object: int, the_attributes: AttributeHandleSet
    ) -> None:
        """Cancel attribute ownership acquisition"""
        pass

    @abstractmethod
    async def query_attribute_ownership(
        self, the_object: int, the_attribute: int
    ) -> None:
        """Query attribute ownership"""
        pass

    @abstractmethod
    async def is_attribute_owned_by_actor(
        self, the_object: int, the_attribute: int
    ) -> bool:
        """Check if attribute is owned by actor"""
        pass

    @abstractmethod
    async def unconditional_attribute_ownership_divestiture(
        self, the_object: int, the_attributes: AttributeHandleSet
    ) -> None:
        """Unconditionally divest attribute ownership"""
        pass

    @abstractmethod
    async def negotiated_attribute_ownership_divestiture(
        self,
        the_object: int,
        the_attributes: AttributeHandleSet,
        user_supplied_tag: bytes,
    ) -> None:
        """Negotiate attribute ownership divestiture"""
        pass

    @abstractmethod
    async def cancel_negotiated_attribute_ownership_divestiture(
        self, the_object: int, the_attributes: AttributeHandleSet
    ) -> None:
        """Cancel negotiated attribute ownership divestiture"""
        pass

    # RTI Support Services

    @abstractmethod
    async def get_object_class_handle(self, the_object_class_name: str) -> int:
        """Get object class handle from name"""
        pass

    @abstractmethod
    async def get_object_class_name(self, the_object_class: int) -> str:
        """Get object class name from handle"""
        pass

    @abstractmethod
    async def get_attribute_handle(
        self, the_attribute_name: str, which_class: int
    ) -> int:
        """Get attribute handle from name"""
        pass

    @abstractmethod
    async def get_attribute_name(
        self, the_attribute: int, which_class: int
    ) -> str:
        """Get attribute name from handle"""
        pass

    @abstractmethod
    async def get_interaction_class_handle(
        self, the_interaction_class_name: str
    ) -> int:
        """Get interaction class handle from name"""
        pass

    @abstractmethod
    async def get_interaction_class_name(self, the_interaction_class: int) -> str:
        """Get interaction class name from handle"""
        pass

    @abstractmethod
    async def get_parameter_handle(
        self, the_parameter_name: str, which_class: int
    ) -> int:
        """Get parameter handle from name"""
        pass

    @abstractmethod
    async def get_parameter_name(
        self, the_parameter: int, which_class: int
    ) -> str:
        """Get parameter name from handle"""
        pass

    @abstractmethod
    async def get_routing_space_handle(self, the_routing_space_name: str) -> int:
        """Get routing space handle from name"""
        pass

    @abstractmethod
    async def get_routing_space_name(self, the_routing_space: int) -> str:
        """Get routing space name from handle"""
        pass

    @abstractmethod
    async def get_dimension_handle(
        self, the_dimension_name: str, which_space: int
    ) -> int:
        """Get dimension handle from name"""
        pass

    @abstractmethod
    async def get_dimension_name(
        self, the_dimension: int, which_space: int
    ) -> str:
        """Get dimension name from handle"""
        pass

    @abstractmethod
    async def get_object_instance_handle(self, the_object_name: str) -> int:
        """Get object instance handle from name"""
        pass

    @abstractmethod
    async def get_object_instance_name(self, the_object: int) -> str:
        """Get object instance name from handle"""
        pass

    @abstractmethod
    async def get_interaction_routing_space_handle(self, the_class: int) -> int:
        """Get interaction routing space handle"""
        pass

    @abstractmethod
    async def get_object_class_routing_space_handle(self, the_class: int) -> int:
        """Get object class routing space handle"""
        pass

    # Advisory Switches

    @abstractmethod
    async def enable_class_relevance_advisory_switch(self) -> None:
        """Enable class relevance advisory switch"""
        pass

    @abstractmethod
    async def disable_class_relevance_advisory_switch(self) -> None:
        """Disable class relevance advisory switch"""
        pass

    @abstractmethod
    async def enable_attribute_relevance_advisory_switch(self) -> None:
        """Enable attribute relevance advisory switch"""
        pass

    @abstractmethod
    async def disable_attribute_relevance_advisory_switch(self) -> None:
        """Disable attribute relevance advisory switch"""
        pass

    @abstractmethod
    async def enable_attribute_scope_advisory_switch(self) -> None:
        """Enable attribute scope advisory switch"""
        pass

    @abstractmethod
    async def disable_attribute_scope_advisory_switch(self) -> None:
        """Disable attribute scope advisory switch"""
        pass

    @abstractmethod
    async def enable_interaction_relevance_advisory_switch(self) -> None:
        """Enable interaction relevance advisory switch"""
        pass

    @abstractmethod
    async def disable_interaction_relevance_advisory_switch(self) -> None:
        """Disable interaction relevance advisory switch"""
        pass

