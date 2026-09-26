# Copyright 2026 Loreum Digital Inc
# SPDX-License-Identifier: Apache-2.0
"""
BaseEntity - represents an object in the state channel
"""
from typing import Dict, Optional, Callable, List
from retiqo.scd.base_state import BaseState
from retiqo.rti.rti_surrogate import RTISurrogate
from retiqo.rti.attribute_handle_set import AttributeHandleSet, AttributeHandleSetFactory
from retiqo.rti.supplied_attributes import SuppliedAttributes, SuppliedAttributesFactory
from retiqo.scd.exceptions import EntityException
from retiqo.exceptions import *


class BaseEntity:
    """Base entity representing an object"""

    # Event handler type definitions
    AttributeIsNotOwnedEvent = Callable[[int], None]
    AttributeOwnedByRTIEvent = Callable[[int], None]
    AttributeOwnershipAcquisitionNotificationEvent = Callable[[List[int]], None]
    AttributeOwnershipDivestitureNotificationEvent = Callable[[List[int]], None]
    AttributeOwnershipUnavailableEvent = Callable[[List[int]], None]
    AttributesInScopeEvent = Callable[[List[int]], None]
    AttributesOutOfScopeEvent = Callable[[List[int]], None]
    ConfirmAttributeOwnershipAcquisitionCancellationEvent = Callable[[List[int]], None]
    InformAttributeOwnershipEvent = Callable[[int, int], None]
    AttributeOwnershipAssumptionRequestEvent = Callable[[List[int], bytes], None]
    AttributeOwnershipReleaseRequestEvent = Callable[[List[int], bytes], None]
    ReflectAttributeValuesEvent = Callable[[List[int], bytes], None]

    def __init__(self, base_state: BaseState):
        """Initialize base entity"""
        self.base_state = base_state
        self.rti = base_state.get_rti()
        self.handle = -1
        self.name = ""
        self.attribute_values: Dict[int, bytes] = {}
        self.attribute_ownership_map: Dict[int, bool] = {}

        # Event handlers
        self.attribute_is_not_owned_event_handler: Optional[BaseEntity.AttributeIsNotOwnedEvent] = None
        self.attribute_owned_by_rti_event_handler: Optional[BaseEntity.AttributeOwnedByRTIEvent] = None
        self.attribute_ownership_acquisition_notification_event_handler: Optional[BaseEntity.AttributeOwnershipAcquisitionNotificationEvent] = None
        self.attribute_ownership_divestiture_notification_event_handler: Optional[BaseEntity.AttributeOwnershipDivestitureNotificationEvent] = None
        self.attribute_ownership_unavailable_event_handler: Optional[BaseEntity.AttributeOwnershipUnavailableEvent] = None
        self.attributes_in_scope_event_handler: Optional[BaseEntity.AttributesInScopeEvent] = None
        self.attributes_out_of_scope_event_handler: Optional[BaseEntity.AttributesOutOfScopeEvent] = None
        self.confirm_attribute_ownership_acquisition_cancellation_event_handler: Optional[BaseEntity.ConfirmAttributeOwnershipAcquisitionCancellationEvent] = None
        self.inform_attribute_ownership_handler: Optional[BaseEntity.InformAttributeOwnershipEvent] = None
        self.attribute_ownership_assumption_request_handler: Optional[BaseEntity.AttributeOwnershipAssumptionRequestEvent] = None
        self.attribute_ownership_release_request_handler: Optional[BaseEntity.AttributeOwnershipReleaseRequestEvent] = None
        self.reflect_attribute_values_event_handler: Optional[BaseEntity.ReflectAttributeValuesEvent] = None

    def get_base_state(self) -> BaseState:
        """Get base state"""
        return self.base_state

    def get_handle(self) -> int:
        """Get object handle"""
        return self.handle

    def set_handle(self, handle: int) -> None:
        """Set object handle"""
        self.handle = handle

    def get_name(self) -> str:
        """Get object name"""
        return self.name

    def set_name(self, name: str) -> None:
        """Set object name"""
        self.name = name

    def get_class_handle(self) -> int:
        """Get class handle - override in derived class"""
        return -1

    def get_attribute_values(self) -> Dict[int, bytes]:
        """Get attribute values"""
        return self.attribute_values

    def set_attribute_value(self, attribute_handle: int, value: bytes) -> None:
        """Set attribute value"""
        self.attribute_values[attribute_handle] = value

    def get_attribute_value(self, attribute_handle: int) -> Optional[bytes]:
        """Get attribute value"""
        return self.attribute_values.get(attribute_handle)

    def set_attribute_ownership(self, attribute_handle: int, owned: bool) -> None:
        """Set attribute ownership"""
        self.attribute_ownership_map[attribute_handle] = owned

    def get_attribute_ownership(self, attribute_handle: int) -> bool:
        """Get attribute ownership"""
        return self.attribute_ownership_map.get(attribute_handle, False)

    @staticmethod
    async def register_instance(base_state: BaseState, the_class: int, the_object_name: Optional[str] = None) -> Optional["BaseEntity"]:
        """Register object instance"""
        try:
            handle = await base_state.get_rti().register_object_instance(the_class, the_object_name)
            if handle >= 0:
                entity = base_state.create_object_instance(the_class)
                if entity is not None:
                    entity.set_handle(handle)
                    base_state.get_entities()[handle] = entity
                    return entity
        except (ObjectClassNotDefined, ObjectClassNotPublished, ActorNotExecutionMember, SaveInProgress, RestoreInProgress, RTIInternalError, ObjectAlreadyRegistered) as e:
            raise EntityException(str(e), e)
        return None

    @staticmethod
    async def destroy_instance(base_state: BaseState, entity: Optional["BaseEntity"], user_supplied_tag: bytes) -> None:
        """Destroy object instance"""
        try:
            if entity is not None:
                object_handle = entity.get_handle()
                await base_state.get_rti().delete_object_instance(object_handle, user_supplied_tag)
                base_state.get_entities().pop(object_handle, None)
        except (ObjectNotKnown, DeleteRightNotHeld, ActorNotExecutionMember, SaveInProgress, RestoreInProgress, RTIInternalError) as e:
            raise EntityException(str(e), e)

    @staticmethod
    async def publish(base_state: BaseState, the_class: int, *attribute_list: int) -> None:
        """Publish object class"""
        try:
            attr_set = AttributeHandleSetFactory.create(list(attribute_list))
            await base_state.get_rti().publish_object_class(the_class, attr_set)
        except (ObjectClassNotDefined, AttributeNotDefined, OwnershipAcquisitionPending, ActorNotExecutionMember, SaveInProgress, RestoreInProgress, RTIInternalError) as e:
            raise EntityException(str(e), e)

    @staticmethod
    async def unpublish(base_state: BaseState, the_class: int) -> None:
        """Unpublish object class"""
        try:
            await base_state.get_rti().unpublish_object_class(the_class)
        except (ObjectClassNotDefined, ObjectClassNotPublished, OwnershipAcquisitionPending, ActorNotExecutionMember, SaveInProgress, RestoreInProgress, RTIInternalError) as e:
            raise EntityException(str(e), e)

    @staticmethod
    async def subscribe(base_state: BaseState, the_class: int, *attribute_list: int) -> None:
        """Subscribe to object class"""
        try:
            attr_set = AttributeHandleSetFactory.create(list(attribute_list))
            await base_state.get_rti().subscribe_object_class_attributes(the_class, attr_set)
        except (ObjectClassNotDefined, AttributeNotDefined, ActorNotExecutionMember, SaveInProgress, RestoreInProgress, RTIInternalError) as e:
            raise EntityException(str(e), e)

    @staticmethod
    async def subscribe_passively(base_state: BaseState, the_class: int, *attribute_list: int) -> None:
        """Subscribe passively to object class"""
        try:
            attr_set = AttributeHandleSetFactory.create(list(attribute_list))
            await base_state.get_rti().subscribe_object_class_attributes_passively(the_class, attr_set)
        except (ObjectClassNotDefined, AttributeNotDefined, ActorNotExecutionMember, SaveInProgress, RestoreInProgress, RTIInternalError) as e:
            raise EntityException(str(e), e)

    @staticmethod
    async def unsubscribe(base_state: BaseState, the_class: int) -> None:
        """Unsubscribe from object class"""
        try:
            await base_state.get_rti().unsubscribe_object_class(the_class)
        except (ObjectClassNotDefined, ObjectClassNotSubscribed, ActorNotExecutionMember, SaveInProgress, RestoreInProgress, RTIInternalError) as e:
            raise EntityException(str(e), e)

    @staticmethod
    async def request_class_attribute_value_update(base_state: BaseState, the_class: int, *attribute_list: int) -> None:
        """Request class attribute value update"""
        try:
            attr_set = AttributeHandleSetFactory.create(list(attribute_list))
            await base_state.get_rti().request_class_attribute_value_update(the_class, attr_set)
        except (ObjectClassNotDefined, AttributeNotDefined, ActorNotExecutionMember, SaveInProgress, RestoreInProgress, RTIInternalError) as e:
            raise EntityException(str(e), e)

    async def update(self, user_supplied_tag: bytes) -> None:
        """Update all attribute values"""
        await self.update_attributes(self.attribute_values, user_supplied_tag)

    async def update_attributes(self, attribute_value_pairs: Dict[int, bytes], user_supplied_tag: bytes) -> None:
        """Update specific attribute values"""
        try:
            supplied_attrs = SuppliedAttributesFactory.create()
            for attr_handle, value in attribute_value_pairs.items():
                supplied_attrs.add(attr_handle, value)
            
            await self.rti.update_attribute_values(self.handle, supplied_attrs, user_supplied_tag)
        except (ObjectNotKnown, AttributeNotDefined, AttributeNotOwned, ActorNotExecutionMember, SaveInProgress, RestoreInProgress, RTIInternalError) as e:
            raise EntityException(str(e), e)

    async def request_attribute_update(self, *attributes: int) -> None:
        """Request attribute value update"""
        try:
            attr_set = AttributeHandleSetFactory.create(list(attributes))
            await self.rti.request_object_attribute_value_update(self.handle, attr_set)
        except (ObjectNotKnown, AttributeNotDefined, ActorNotExecutionMember, SaveInProgress, RestoreInProgress, RTIInternalError) as e:
            raise EntityException(str(e), e)

    async def acquire_attribute_ownership(self, user_supplied_tag: bytes, *the_attributes: int) -> None:
        """Acquire attribute ownership"""
        try:
            attr_set = AttributeHandleSetFactory.create(list(the_attributes))
            await self.rti.attribute_ownership_acquisition(self.handle, attr_set, user_supplied_tag)
        except (ObjectNotKnown, ObjectClassNotPublished, AttributeNotDefined, AttributeNotPublished, ActorOwnsAttributes, ActorNotExecutionMember, SaveInProgress, RestoreInProgress, RTIInternalError) as e:
            raise EntityException(str(e), e)

    async def acquire_attribute_ownership_if_available(self, *the_attributes: int) -> None:
        """Acquire attribute ownership if available"""
        try:
            attr_set = AttributeHandleSetFactory.create(list(the_attributes))
            await self.rti.attribute_ownership_acquisition_if_available(self.handle, attr_set)
        except (ObjectNotKnown, ObjectClassNotPublished, AttributeNotDefined, AttributeNotPublished, ActorOwnsAttributes, AttributeAlreadyBeingAcquired, ActorNotExecutionMember, SaveInProgress, RestoreInProgress, RTIInternalError) as e:
            raise EntityException(str(e), e)

    # Event handler setters/getters (simplified - full implementation would include all handlers)
    def set_attribute_is_not_owned_event_handler(self, handler: AttributeIsNotOwnedEvent) -> None:
        self.attribute_is_not_owned_event_handler = handler

    def set_attribute_owned_by_rti_event_handler(self, handler: AttributeOwnedByRTIEvent) -> None:
        self.attribute_owned_by_rti_event_handler = handler

    # ... (other event handler setters/getters would follow the same pattern)



