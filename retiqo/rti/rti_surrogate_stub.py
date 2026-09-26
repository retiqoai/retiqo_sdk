# Copyright 2026 Loreum Digital Inc
# SPDX-License-Identifier: Apache-2.0
"""
RTISurrogateStub - stub for making RTI method calls
"""
from typing import List, Optional, Any
from retiqo.transport.base_session import BaseSession
from retiqo.streams.marshaller import MarshallerException


class _VectorParam:
    """Wrapper to force vector serialization for method parameters"""
    def __init__(self, items):
        self._items = items
    def __iter__(self):
        return iter(self._items)
    def __len__(self):
        return len(self._items)
    def __getitem__(self, i):
        return self._items[i]


class RTISurrogateStub:
    """Stub for RTI surrogate method calls"""

    # Method IDs
    Method_createStateChannelExecution = 1
    Method_destroyStateChannelExecution = 2
    Method_getStateChannelExecutions = 3
    Method_getStateChannelDefinition = 4
    Method_joinStateChannelExecution = 5
    Method_resignStateChannelExecution = 6
    Method_registerStateChannelConsensusPoint_1 = 7
    Method_registerStateChannelConsensusPoint_2 = 8
    Method_consensusPointAchieved = 9
    Method_requestStateChannelSave = 10
    Method_requestStateChannelSave1 = 11
    Method_actorSaveBegun = 12
    Method_actorSaveComplete = 13
    Method_actorSaveNotComplete = 14
    Method_requestStateChannelRestore = 15
    Method_actorRestoreComplete = 16
    Method_actorRestoreNotComplete = 17
    Method_publishObjectClass = 18
    Method_unpublishObjectClass = 19
    Method_publishInteractionClass = 20
    Method_unpublishInteractionClass = 21
    Method_subscribeObjectClassAttributes = 22
    Method_subscribeObjectClassAttributesPassively = 23
    Method_unsubscribeObjectClass = 24
    Method_subscribeInteractionClass = 25
    Method_subscribeInteractionClassPassively = 26
    Method_unsubscribeInteractionClass = 27
    Method_registerObjectInstance = 28
    Method_registerObjectInstance1 = 29
    Method_updateAttributeValues = 30
    Method_updateAttributeValues1 = 31
    Method_sendInteraction = 32
    Method_sendInteraction1 = 33
    Method_deleteObjectInstance = 34
    Method_deleteObjectInstance1 = 35
    Method_localDeleteObjectInstance = 36
    Method_requestObjectAttributeValueUpdate = 39
    Method_requestClassAttributeValueUpdate = 40
    Method_unconditionalAttributeOwnershipDivestiture = 41
    Method_negotiatedAttributeOwnershipDivestiture = 42
    Method_attributeOwnershipAcquisition = 43
    Method_attributeOwnershipAcquisitionIfAvailable = 44
    Method_attributeOwnershipReleaseResponse = 45
    Method_cancelNegotiatedAttributeOwnershipDivestiture = 46
    Method_cancelAttributeOwnershipAcquisition = 47
    Method_queryAttributeOwnership = 48
    Method_isAttributeOwnedByActor = 49
    Method_createRegion = 69
    Method_notifyOfRegionModification = 70
    Method_deleteRegion = 71
    Method_registerObjectInstanceWithRegion = 72
    Method_registerObjectInstanceWithRegion1 = 73
    Method_associateRegionForUpdates = 74
    Method_unassociateRegionForUpdates = 75
    Method_subscribeObjectClassAttributesWithRegion = 76
    Method_subscribeObjectClassAttributesPassivelyWithRegion = 77
    Method_unsubscribeObjectClassWithRegion = 78
    Method_subscribeInteractionClassWithRegion = 79
    Method_subscribeInteractionClassPassivelyWithRegion = 80
    Method_unsubscribeInteractionClassWithRegion = 81
    Method_sendInteractionWithRegion = 82
    Method_sendInteractionWithRegion1 = 83
    Method_requestClassAttributeValueUpdateWithRegion = 84
    Method_getObjectClassHandle = 85
    Method_getObjectClassName = 86
    Method_getAttributeHandle = 87
    Method_getAttributeName = 88
    Method_getInteractionClassHandle = 89
    Method_getInteractionClassName = 90
    Method_getParameterHandle = 91
    Method_getParameterName = 92
    Method_getObjectInstanceHandle = 93
    Method_getObjectInstanceName = 94
    Method_getRoutingSpaceHandle = 95
    Method_getRoutingSpaceName = 96
    Method_getDimensionHandle = 97
    Method_getDimensionName = 98
    Method_getAttributeRoutingSpaceHandle = 99
    Method_getObjectClass = 100
    Method_getInteractionRoutingSpaceHandle = 101
    Method_enableClassRelevanceAdvisorySwitch = 102
    Method_disableClassRelevanceAdvisorySwitch = 103
    Method_enableAttributeRelevanceAdvisorySwitch = 104
    Method_disableAttributeRelevanceAdvisorySwitch = 105
    Method_enableAttributeScopeAdvisorySwitch = 106
    Method_disableAttributeScopeAdvisorySwitch = 107
    Method_enableInteractionRelevanceAdvisorySwitch = 108
    Method_disableInteractionRelevanceAdvisorySwitch = 109
    Method_getRegion = 110
    Method_getRegionToken = 111

    def __init__(self, session: BaseSession):
        """Initialize stub with session"""
        self._session = session

    def get_session(self) -> BaseSession:
        """Get session"""
        return self._session

    async def create_state_channel_execution(self, execution_name: str, scd: str) -> Optional[List[Any]]:
        """Create state channel execution"""
        v = [execution_name, scd]
        return await self._session.send_object_recv_object(self.Method_createStateChannelExecution, v, False)

    async def destroy_state_channel_execution(self, execution_name: str) -> Optional[List[Any]]:
        """Destroy state channel execution"""
        return await self._session.send_object_recv_object(self.Method_destroyStateChannelExecution, execution_name, True)

    async def get_state_channel_executions(self) -> Optional[List[Any]]:
        """Get state channel executions"""
        return await self._session.send_void_recv_object(self.Method_getStateChannelExecutions)

    async def join_state_channel_execution(
        self, actor_type: str, execution_name: str, public_key: bytes
    ) -> Optional[List[Any]]:
        """Join state channel execution"""
        v = [actor_type, execution_name, public_key]
        return await self._session.send_object_recv_object(self.Method_joinStateChannelExecution, v, False)

    async def resign_state_channel_execution(self, resign_action: int) -> Optional[List[Any]]:
        """Resign from state channel execution"""
        return await self._session.send_object_recv_object(
            self.Method_resignStateChannelExecution, resign_action, True
        )

    async def register_state_channel_consensus_point(
        self, consensus_point_label: str, user_supplied_tag: bytes, consensus_set: Optional[List[int]] = None
    ) -> Optional[List[Any]]:
        """Register state channel consensus point"""
        if consensus_set is None:
            v = [consensus_point_label, user_supplied_tag]
            return await self._session.send_object_recv_object(
                self.Method_registerStateChannelConsensusPoint_1, v, False
            )
        else:
            v = [consensus_point_label, user_supplied_tag, consensus_set]
            return await self._session.send_object_recv_object(
                self.Method_registerStateChannelConsensusPoint_2, v, False
            )

    async def consensus_point_achieved(
        self, consensus_point_label: str, consensus_hash: bytes, signature: bytes
    ) -> Optional[List[Any]]:
        """Achieve consensus point"""
        v = [consensus_point_label, consensus_hash, signature]
        return await self._session.send_object_recv_object(self.Method_consensusPointAchieved, v, False)

    async def request_state_channel_save(self, label: str, actor_set: Optional[List[int]] = None) -> Optional[List[Any]]:
        """Request state channel save"""
        if actor_set is None:
            return await self._session.send_object_recv_object(self.Method_requestStateChannelSave, label, True)
        else:
            v = [label, actor_set]
            return await self._session.send_object_recv_object(self.Method_requestStateChannelSave1, v, False)

    async def actor_save_begun(self) -> Optional[List[Any]]:
        """Actor save begun"""
        return await self._session.send_void_recv_object(self.Method_actorSaveBegun)

    async def actor_save_complete(self) -> Optional[List[Any]]:
        """Actor save complete"""
        return await self._session.send_void_recv_object(self.Method_actorSaveComplete)

    async def actor_save_not_complete(self) -> Optional[List[Any]]:
        """Actor save not complete"""
        return await self._session.send_void_recv_object(self.Method_actorSaveNotComplete)

    async def request_state_channel_restore(self, label: str) -> Optional[List[Any]]:
        """Request state channel restore"""
        return await self._session.send_object_recv_object(self.Method_requestStateChannelRestore, label, True)

    async def actor_restore_complete(self) -> Optional[List[Any]]:
        """Actor restore complete"""
        return await self._session.send_void_recv_object(self.Method_actorRestoreComplete)

    async def actor_restore_not_complete(self) -> Optional[List[Any]]:
        """Actor restore not complete"""
        return await self._session.send_void_recv_object(self.Method_actorRestoreNotComplete)

    async def publish_object_class(self, the_class: int, attribute_list: List[int]) -> Optional[List[Any]]:
        """Publish object class"""
        v = [the_class, attribute_list]
        return await self._session.send_object_recv_object(self.Method_publishObjectClass, v, False)

    async def unpublish_object_class(self, the_class: int) -> Optional[List[Any]]:
        """Unpublish object class"""
        return await self._session.send_object_recv_object(self.Method_unpublishObjectClass, the_class, True)

    async def publish_interaction_class(self, the_interaction: int) -> Optional[List[Any]]:
        """Publish interaction class"""
        return await self._session.send_object_recv_object(self.Method_publishInteractionClass, the_interaction, True)

    async def unpublish_interaction_class(self, the_interaction: int) -> Optional[List[Any]]:
        """Unpublish interaction class"""
        return await self._session.send_object_recv_object(self.Method_unpublishInteractionClass, the_interaction, True)

    async def subscribe_object_class_attributes(
        self, the_class: int, attribute_list: List[int], passively: bool = False
    ) -> Optional[List[Any]]:
        """Subscribe to object class attributes"""
        v = [the_class, attribute_list]
        method_id = (
            self.Method_subscribeObjectClassAttributesPassively if passively else self.Method_subscribeObjectClassAttributes
        )
        return await self._session.send_object_recv_object(method_id, v, False)

    async def unsubscribe_object_class(self, the_class: int, the_region: Optional[Any] = None) -> Optional[List[Any]]:
        """Unsubscribe from object class"""
        if the_region is None:
            return await self._session.send_object_recv_object(self.Method_unsubscribeObjectClass, the_class, True)
        else:
            v = [the_class, the_region]
            return await self._session.send_object_recv_object(self.Method_unsubscribeObjectClassWithRegion, v, False)

    async def subscribe_interaction_class(self, the_class: int, passively: bool = False) -> Optional[List[Any]]:
        """Subscribe to interaction class"""
        method_id = (
            self.Method_subscribeInteractionClassPassively if passively else self.Method_subscribeInteractionClass
        )
        return await self._session.send_object_recv_object(method_id, the_class, True)

    async def unsubscribe_interaction_class(self, the_class: int, the_region: Optional[Any] = None) -> Optional[List[Any]]:
        """Unsubscribe from interaction class"""
        if the_region is None:
            return await self._session.send_object_recv_object(self.Method_unsubscribeInteractionClass, the_class, True)
        else:
            v = [the_class, the_region]
            return await self._session.send_object_recv_object(self.Method_unsubscribeInteractionClassWithRegion, v, False)

    async def register_object_instance(
        self, the_class: int, the_object_name: Optional[str] = None
    ) -> Optional[List[Any]]:
        """Register object instance"""
        if the_object_name is None:
            return await self._session.send_object_recv_object(self.Method_registerObjectInstance, the_class, True)
        else:
            v = [the_class, the_object_name]
            return await self._session.send_object_recv_object(self.Method_registerObjectInstance1, v, False)

    async def register_object_instance_with_region(
        self, the_class: int, the_object_name: Optional[str], the_attributes: List[int], the_regions: List[Any]
    ) -> Optional[List[Any]]:
        """Register object instance with region"""
        # Extract region handles
        region_handles = []
        for region in the_regions:
            if isinstance(region, int):
                region_handles.append(region)
            elif hasattr(region, 'get_handle'):
                region_handles.append(region.get_handle())
            else:
                region_handles.append(-1)
        
        if the_object_name is None:
            v = [the_class, the_attributes, region_handles]
            return await self._session.send_object_recv_object(self.Method_registerObjectInstanceWithRegion, v, False)
        else:
            v = [the_class, the_object_name, the_attributes, region_handles]
            return await self._session.send_object_recv_object(self.Method_registerObjectInstanceWithRegion1, v, False)

    async def update_attribute_values(
        self, the_object: int, the_attributes: Any, user_supplied_tag: bytes, the_region: Optional[Any] = None
    ) -> Optional[List[Any]]:
        """Update attribute values"""
        if the_region is None:
            v = [the_object, the_attributes, user_supplied_tag]
            return await self._session.send_object_recv_object(self.Method_updateAttributeValues, v, False)
        else:
            v = [the_object, the_attributes, user_supplied_tag, the_region]
            return await self._session.send_object_recv_object(self.Method_updateAttributeValues1, v, False)

    async def send_interaction(
        self, the_interaction: int, the_parameters: Any, user_supplied_tag: bytes, the_region: Optional[Any] = None
    ) -> Optional[List[Any]]:
        """Send interaction"""
        if the_region is None:
            v = [the_interaction, the_parameters, user_supplied_tag]
            return await self._session.send_object_recv_object(self.Method_sendInteraction, v, False)
        else:
            v = [the_interaction, the_parameters, user_supplied_tag, the_region]
            return await self._session.send_object_recv_object(self.Method_sendInteractionWithRegion, v, False)

    async def send_interaction_with_region(
        self, the_interaction: int, the_parameters: Any, user_supplied_tag: bytes, the_region: Any
    ) -> Optional[List[Any]]:
        """Send interaction with region"""
        # Server expects: (interaction handle, parameter vector, user-supplied tag, region handle)
        # Extract region handle
        if isinstance(the_region, int):
            region_handle = the_region
        else:
            region_handle = the_region.get_handle() if hasattr(the_region, 'get_handle') else -1
        v = [the_interaction, the_parameters, user_supplied_tag, region_handle]
        return await self._session.send_object_recv_object(self.Method_sendInteractionWithRegion, v, False)

    async def delete_object_instance(self, the_object: int, user_supplied_tag: bytes) -> Optional[List[Any]]:
        """Delete object instance"""
        v = [the_object, user_supplied_tag]
        return await self._session.send_object_recv_object(self.Method_deleteObjectInstance, v, False)

    async def create_region(self, space_handle: int, number_of_extents: int) -> Optional[List[Any]]:
        """Create region"""
        # Server expects (int, int) - two separate int parameters, not a list
        # Use _VectorParam to force vector serialization
        v = [space_handle, number_of_extents]
        v_wrapped = _VectorParam(v)
        return await self._session.send_object_recv_object(self.Method_createRegion, v_wrapped, False)

    async def delete_region(self, region_handle: int) -> Optional[List[Any]]:
        """Delete region"""
        # The server takes the region handle, not a Region object
        return await self._session.send_object_recv_object(self.Method_deleteRegion, region_handle, True)

    async def notify_of_region_modification(self, the_region: Any) -> Optional[List[Any]]:
        """Notify of region modification"""
        # The argument is sent as a primitive object
        # This tells the server to treat the Vector as a single parameter, not unpack it
        return await self._session.send_object_recv_object(self.Method_notifyOfRegionModification, the_region, True)

    async def get_region_token(self, region_vector: Any) -> Optional[List[Any]]:
        """Get region token"""
        # The server takes the region vector, not a Region object
        # region_vector should be a _VectorParam wrapper
        # Use is_primitive_obj_in=True to treat Vector as a single parameter (not unpack it)
        return await self._session.send_object_recv_object(self.Method_getRegionToken, region_vector, True)

    async def get_region(self, region_token: int) -> Optional[List[Any]]:
        """Get region from token"""
        return await self._session.send_object_recv_object(self.Method_getRegion, region_token, True)

    async def associate_region_for_updates(
        self, the_region: Any, the_object: int, the_attributes: List[int]
    ) -> Optional[List[Any]]:
        """Associate region for updates"""
        v = [the_region, the_object, the_attributes]
        return await self._session.send_object_recv_object(self.Method_associateRegionForUpdates, v, False)

    async def unassociate_region_for_updates(
        self, the_region: Any, the_object: int, the_attributes: Optional[List[int]] = None
    ) -> Optional[List[Any]]:
        """Unassociate region for updates"""
        # Server expects: (region handle, object handle)
        # Server expects two separate int parameters, not an array
        # Use _VectorParam to force vector serialization with two int elements
        if isinstance(the_region, int):
            region_handle = the_region
        else:
            region_handle = the_region.get_handle() if hasattr(the_region, 'get_handle') else -1
        v = [region_handle, the_object]
        v_wrapped = _VectorParam(v)
        return await self._session.send_object_recv_object(self.Method_unassociateRegionForUpdates, v_wrapped, False)

    async def subscribe_object_class_attributes_with_region(
        self, the_class: int, attribute_list: List[int], the_region: Any
    ) -> Optional[List[Any]]:
        """Subscribe to object class attributes with region"""
        v = [the_class, attribute_list, the_region]
        return await self._session.send_object_recv_object(self.Method_subscribeObjectClassAttributesWithRegion, v, False)

    async def subscribe_interaction_class_with_region(self, the_class: int, the_region: Any) -> Optional[List[Any]]:
        """Subscribe to interaction class with region"""
        v = [the_class, the_region]
        return await self._session.send_object_recv_object(self.Method_subscribeInteractionClassWithRegion, v, False)

    async def request_object_attribute_value_update(
        self, the_object: int, the_attributes: List[int]
    ) -> Optional[List[Any]]:
        """Request object attribute value update"""
        v = [the_object, the_attributes]
        return await self._session.send_object_recv_object(self.Method_requestObjectAttributeValueUpdate, v, False)

    async def request_class_attribute_value_update(
        self, the_class: int, the_attributes: List[int], the_region: Optional[Any] = None
    ) -> Optional[List[Any]]:
        """Request class attribute value update"""
        if the_region is None:
            v = [the_class, the_attributes]
            return await self._session.send_object_recv_object(self.Method_requestClassAttributeValueUpdate, v, False)
        else:
            # Use the dedicated method for region version
            return await self.request_class_attribute_value_update_with_region(the_class, the_attributes, the_region)

    async def request_class_attribute_value_update_with_region(
        self, the_class: int, the_attributes: List[int], the_region: Any
    ) -> Optional[List[Any]]:
        """Request class attribute value update with region"""
        # Server expects: (class handle, attribute handles, region handle)
        # Extract region handle
        if isinstance(the_region, int):
            region_handle = the_region
        else:
            region_handle = the_region.get_handle() if hasattr(the_region, 'get_handle') else -1
        v = [the_class, the_attributes, region_handle]
        return await self._session.send_object_recv_object(
            self.Method_requestClassAttributeValueUpdateWithRegion, v, False
        )

    async def attribute_ownership_acquisition(
        self, the_object: int, desired_attributes: List[int], user_supplied_tag: bytes
    ) -> Optional[List[Any]]:
        """Acquire attribute ownership"""
        v = [the_object, desired_attributes, user_supplied_tag]
        return await self._session.send_object_recv_object(self.Method_attributeOwnershipAcquisition, v, False)

    async def attribute_ownership_acquisition_if_available(
        self, the_object: int, desired_attributes: List[int]
    ) -> Optional[List[Any]]:
        """Acquire attribute ownership if available"""
        v = [the_object, desired_attributes]
        return await self._session.send_object_recv_object(self.Method_attributeOwnershipAcquisitionIfAvailable, v, False)

    async def cancel_attribute_ownership_acquisition(
        self, the_object: int, the_attributes: List[int]
    ) -> Optional[List[Any]]:
        """Cancel attribute ownership acquisition"""
        v = [the_object, the_attributes]
        return await self._session.send_object_recv_object(self.Method_cancelAttributeOwnershipAcquisition, v, False)

    async def unconditional_attribute_ownership_divestiture(
        self, the_object: int, the_attributes: List[int]
    ) -> Optional[List[Any]]:
        """Unconditionally divest attribute ownership"""
        v = [the_object, the_attributes]
        return await self._session.send_object_recv_object(self.Method_unconditionalAttributeOwnershipDivestiture, v, False)

    async def query_attribute_ownership(self, the_object: int, the_attribute: int) -> Optional[List[Any]]:
        """Query attribute ownership"""
        # Force vector serialization (not int array) - server expects vector with two int elements
        # We need to serialize as TC_VECTOR, not TC_INT | TC_FLAG_ARRAY
        v = [the_object, the_attribute]
        v_wrapped = _VectorParam(v)
        return await self._session.send_object_recv_object(self.Method_queryAttributeOwnership, v_wrapped, False)

    async def is_attribute_owned_by_actor(self, the_object: int, the_attribute: int) -> Optional[List[Any]]:
        """Check if attribute is owned by actor"""
        # Force vector serialization (not int array) - server expects vector with two int elements
        v = [the_object, the_attribute]
        v_wrapped = _VectorParam(v)
        return await self._session.send_object_recv_object(self.Method_isAttributeOwnedByActor, v_wrapped, False)

    async def negotiated_attribute_ownership_divestiture(
        self, the_object: int, the_attributes: List[int], user_supplied_tag: bytes
    ) -> Optional[List[Any]]:
        """Negotiate attribute ownership divestiture"""
        v = [the_object, the_attributes, user_supplied_tag]
        return await self._session.send_object_recv_object(self.Method_negotiatedAttributeOwnershipDivestiture, v, False)

    async def cancel_negotiated_attribute_ownership_divestiture(
        self, the_object: int, the_attributes: List[int]
    ) -> Optional[List[Any]]:
        """Cancel negotiated attribute ownership divestiture"""
        v = [the_object, the_attributes]
        return await self._session.send_object_recv_object(
            self.Method_cancelNegotiatedAttributeOwnershipDivestiture, v, False
        )

    async def get_object_class_handle(self, the_object_class_name: str) -> Optional[List[Any]]:
        """Get object class handle from name"""
        return await self._session.send_object_recv_object(self.Method_getObjectClassHandle, the_object_class_name, True)

    async def get_object_class_name(self, the_object_class: int) -> Optional[List[Any]]:
        """Get object class name from handle"""
        return await self._session.send_object_recv_object(self.Method_getObjectClassName, the_object_class, True)

    async def get_attribute_handle(self, the_attribute_name: str, which_class: int) -> Optional[List[Any]]:
        """Get attribute handle from name"""
        v = [the_attribute_name, which_class]
        return await self._session.send_object_recv_object(self.Method_getAttributeHandle, v, False)

    async def get_attribute_name(self, the_attribute: int, which_class: int) -> Optional[List[Any]]:
        """Get attribute name from handle"""
        # Force vector serialization (not int array) - server expects vector with two int elements
        v = [the_attribute, which_class]
        v_wrapped = _VectorParam(v)
        return await self._session.send_object_recv_object(self.Method_getAttributeName, v_wrapped, False)

    async def get_interaction_class_handle(self, the_interaction_class_name: str) -> Optional[List[Any]]:
        """Get interaction class handle from name"""
        return await self._session.send_object_recv_object(
            self.Method_getInteractionClassHandle, the_interaction_class_name, True
        )

    async def get_interaction_class_name(self, the_interaction_class: int) -> Optional[List[Any]]:
        """Get interaction class name from handle"""
        return await self._session.send_object_recv_object(self.Method_getInteractionClassName, the_interaction_class, True)

    async def get_parameter_handle(self, the_parameter_name: str, which_class: int) -> Optional[List[Any]]:
        """Get parameter handle from name"""
        v = [the_parameter_name, which_class]
        return await self._session.send_object_recv_object(self.Method_getParameterHandle, v, False)

    async def get_parameter_name(self, the_parameter: int, which_class: int) -> Optional[List[Any]]:
        """Get parameter name from handle"""
        # Force vector serialization (not int array) - server expects vector with two int elements
        v = [the_parameter, which_class]
        v_wrapped = _VectorParam(v)
        return await self._session.send_object_recv_object(self.Method_getParameterName, v_wrapped, False)

    async def get_routing_space_handle(self, the_routing_space_name: str) -> Optional[List[Any]]:
        """Get routing space handle from name"""
        return await self._session.send_object_recv_object(self.Method_getRoutingSpaceHandle, the_routing_space_name, True)

    async def get_routing_space_name(self, the_routing_space: int) -> Optional[List[Any]]:
        """Get routing space name from handle"""
        return await self._session.send_object_recv_object(self.Method_getRoutingSpaceName, the_routing_space, True)

    async def get_dimension_handle(self, the_dimension_name: str, which_space: int) -> Optional[List[Any]]:
        """Get dimension handle from name"""
        v = [the_dimension_name, which_space]
        return await self._session.send_object_recv_object(self.Method_getDimensionHandle, v, False)

    async def get_dimension_name(self, the_dimension: int, which_space: int) -> Optional[List[Any]]:
        """Get dimension name from handle"""
        # Force vector serialization (not int array) - server expects vector with two int elements
        # We need to serialize as TC_VECTOR, not TC_INT | TC_FLAG_ARRAY
        v = [the_dimension, which_space]
        v_wrapped = _VectorParam(v)
        return await self._session.send_object_recv_object(self.Method_getDimensionName, v_wrapped, False)

    async def get_object_instance_handle(self, the_object_name: str) -> Optional[List[Any]]:
        """Get object instance handle from name"""
        return await self._session.send_object_recv_object(self.Method_getObjectInstanceHandle, the_object_name, True)

    async def get_object_instance_name(self, the_object: int) -> Optional[List[Any]]:
        """Get object instance name from handle"""
        return await self._session.send_object_recv_object(self.Method_getObjectInstanceName, the_object, True)

    async def get_interaction_routing_space_handle(self, the_class: int) -> Optional[List[Any]]:
        """Get interaction routing space handle"""
        return await self._session.send_object_recv_object(self.Method_getInteractionRoutingSpaceHandle, the_class, True)

    async def get_attribute_routing_space_handle(self, the_handle: int, which_class: int) -> Optional[List[Any]]:
        """Get attribute routing space handle"""
        # Force vector serialization (not int array) - server expects vector with two int elements
        v = [the_handle, which_class]
        v_wrapped = _VectorParam(v)
        return await self._session.send_object_recv_object(self.Method_getAttributeRoutingSpaceHandle, v_wrapped, False)

    async def get_object_class_routing_space_handle(self, the_class: int) -> Optional[List[Any]]:
        """Get object class routing space handle"""
        return await self._session.send_object_recv_object(self.Method_getAttributeRoutingSpaceHandle, the_class, True)

    async def enable_class_relevance_advisory_switch(self) -> Optional[List[Any]]:
        """Enable class relevance advisory switch"""
        return await self._session.send_void_recv_object(self.Method_enableClassRelevanceAdvisorySwitch)

    async def disable_class_relevance_advisory_switch(self) -> Optional[List[Any]]:
        """Disable class relevance advisory switch"""
        return await self._session.send_void_recv_object(self.Method_disableClassRelevanceAdvisorySwitch)

    async def enable_attribute_relevance_advisory_switch(self) -> Optional[List[Any]]:
        """Enable attribute relevance advisory switch"""
        return await self._session.send_void_recv_object(self.Method_enableAttributeRelevanceAdvisorySwitch)

    async def disable_attribute_relevance_advisory_switch(self) -> Optional[List[Any]]:
        """Disable attribute relevance advisory switch"""
        return await self._session.send_void_recv_object(self.Method_disableAttributeRelevanceAdvisorySwitch)

    async def enable_attribute_scope_advisory_switch(self) -> Optional[List[Any]]:
        """Enable attribute scope advisory switch"""
        return await self._session.send_void_recv_object(self.Method_enableAttributeScopeAdvisorySwitch)

    async def disable_attribute_scope_advisory_switch(self) -> Optional[List[Any]]:
        """Disable attribute scope advisory switch"""
        return await self._session.send_void_recv_object(self.Method_disableAttributeScopeAdvisorySwitch)

    async def enable_interaction_relevance_advisory_switch(self) -> Optional[List[Any]]:
        """Enable interaction relevance advisory switch"""
        return await self._session.send_void_recv_object(self.Method_enableInteractionRelevanceAdvisorySwitch)

    async def disable_interaction_relevance_advisory_switch(self) -> Optional[List[Any]]:
        """Disable interaction relevance advisory switch"""
        return await self._session.send_void_recv_object(self.Method_disableInteractionRelevanceAdvisorySwitch)

