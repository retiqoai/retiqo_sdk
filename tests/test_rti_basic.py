# Copyright 2026 Loreum Digital Inc
# SPDX-License-Identifier: Apache-2.0
"""
Basic RTI tests - placeholder for comprehensive test suite
"""
import pytest
import asyncio
from retiqo import RTI, ActorSurrogate
from retiqo.rti.attribute_handle_set import AttributeHandleSet, AttributeHandleSetFactory
from retiqo.rti.supplied_attributes import SuppliedAttributes, SuppliedAttributesFactory


class MyTestActorSurrogate(ActorSurrogate):
    """Test implementation of ActorSurrogate"""

    def __init__(self):
        self._base_state = None
        self._callbacks_received = []

    def set_base_state(self, base_state):
        self._base_state = base_state

    def get_base_state(self):
        return self._base_state

    # Implement all required callback methods (stubs for now)
    async def consensus_point_registration_failed(self, consensus_point_label: str) -> None:
        self._callbacks_received.append(("consensus_point_registration_failed", consensus_point_label))

    async def consensus_point_registration_succeeded(self, consensus_point_label: str) -> None:
        self._callbacks_received.append(("consensus_point_registration_succeeded", consensus_point_label))

    async def announce_consensus_point(self, consensus_point_label: str, user_supplied_tag: bytes) -> None:
        self._callbacks_received.append(("announce_consensus_point", consensus_point_label, user_supplied_tag))

    async def state_channel_in_consensus(self, consensus_point_label: str, consensus_state) -> None:
        self._callbacks_received.append(("state_channel_in_consensus", consensus_point_label, consensus_state))

    async def initiate_actor_save(self, label: str) -> None:
        self._callbacks_received.append(("initiate_actor_save", label))

    async def state_channel_saved(self) -> None:
        self._callbacks_received.append(("state_channel_saved",))

    async def state_channel_not_saved(self) -> None:
        self._callbacks_received.append(("state_channel_not_saved",))

    async def request_state_channel_restore_succeeded(self, label: str) -> None:
        self._callbacks_received.append(("request_state_channel_restore_succeeded", label))

    async def request_state_channel_restore_failed(self, label: str, reason: str) -> None:
        self._callbacks_received.append(("request_state_channel_restore_failed", label, reason))

    async def state_channel_restore_begun(self) -> None:
        self._callbacks_received.append(("state_channel_restore_begun",))

    async def initiate_actor_restore(self, label: str, actor_handle: int) -> None:
        self._callbacks_received.append(("initiate_actor_restore", label, actor_handle))

    async def state_channel_restored(self) -> None:
        self._callbacks_received.append(("state_channel_restored",))

    async def state_channel_not_restored(self) -> None:
        self._callbacks_received.append(("state_channel_not_restored",))

    async def start_registration_for_object_class(self, the_class: int) -> None:
        self._callbacks_received.append(("start_registration_for_object_class", the_class))

    async def stop_registration_for_object_class(self, the_class: int) -> None:
        self._callbacks_received.append(("stop_registration_for_object_class", the_class))

    async def turn_interactions_on(self, the_handle: int) -> None:
        self._callbacks_received.append(("turn_interactions_on", the_handle))

    async def turn_interactions_off(self, the_handle: int) -> None:
        self._callbacks_received.append(("turn_interactions_off", the_handle))

    async def discover_object_instance(self, the_object: int, the_object_class: int, object_name: str) -> None:
        self._callbacks_received.append(("discover_object_instance", the_object, the_object_class, object_name))

    async def reflect_attribute_values(self, the_object: int, the_attributes, user_supplied_tag: bytes) -> None:
        self._callbacks_received.append(("reflect_attribute_values", the_object, the_attributes, user_supplied_tag))

    async def receive_interaction(self, interaction_class: int, the_interaction, user_supplied_tag: bytes) -> None:
        self._callbacks_received.append(("receive_interaction", interaction_class, the_interaction, user_supplied_tag))

    async def remove_object_instance(self, the_object: int, user_supplied_tag: bytes) -> None:
        self._callbacks_received.append(("remove_object_instance", the_object, user_supplied_tag))

    async def attributes_in_scope(self, the_object: int, the_attributes) -> None:
        self._callbacks_received.append(("attributes_in_scope", the_object, the_attributes))

    async def attributes_out_of_scope(self, the_object: int, the_attributes) -> None:
        self._callbacks_received.append(("attributes_out_of_scope", the_object, the_attributes))

    async def provide_attribute_value_update(self, the_object: int, the_attributes) -> None:
        self._callbacks_received.append(("provide_attribute_value_update", the_object, the_attributes))

    async def turn_updates_on_for_object_instance(self, the_object: int, the_attributes) -> None:
        self._callbacks_received.append(("turn_updates_on_for_object_instance", the_object, the_attributes))

    async def turn_updates_off_for_object_instance(self, the_object: int, the_attributes) -> None:
        self._callbacks_received.append(("turn_updates_off_for_object_instance", the_object, the_attributes))

    async def request_attribute_ownership_assumption(self, the_object: int, offered_attributes, user_supplied_tag: bytes) -> None:
        self._callbacks_received.append(("request_attribute_ownership_assumption", the_object, offered_attributes, user_supplied_tag))

    async def attribute_ownership_divestiture_notification(self, the_object: int, released_attributes) -> None:
        self._callbacks_received.append(("attribute_ownership_divestiture_notification", the_object, released_attributes))

    async def attribute_ownership_acquisition_notification(self, the_object: int, secured_attributes) -> None:
        self._callbacks_received.append(("attribute_ownership_acquisition_notification", the_object, secured_attributes))

    async def attribute_ownership_unavailable(self, the_object: int, the_attributes) -> None:
        self._callbacks_received.append(("attribute_ownership_unavailable", the_object, the_attributes))

    async def request_attribute_ownership_release(self, the_object: int, candidate_attributes, user_supplied_tag: bytes) -> None:
        self._callbacks_received.append(("request_attribute_ownership_release", the_object, candidate_attributes, user_supplied_tag))

    async def confirm_attribute_ownership_acquisition_cancellation(self, the_object: int, the_attributes) -> None:
        self._callbacks_received.append(("confirm_attribute_ownership_acquisition_cancellation", the_object, the_attributes))

    async def inform_attribute_ownership(self, the_object: int, the_attribute: int, the_owner: int) -> None:
        self._callbacks_received.append(("inform_attribute_ownership", the_object, the_attribute, the_owner))

    async def attribute_is_not_owned(self, the_object: int, the_attribute: int) -> None:
        self._callbacks_received.append(("attribute_is_not_owned", the_object, the_attribute))

    async def attribute_owned_by_rti(self, the_object: int, the_attribute: int) -> None:
        self._callbacks_received.append(("attribute_owned_by_rti", the_object, the_attribute))


def test_rti_initialization():
    """Test RTI initialization"""
    # This is a placeholder test - full implementation needed
    # rti = RTI(server_url="ws://localhost:8080/ws")
    # assert rti is not None
    pass


@pytest.mark.asyncio
async def test_actor_surrogate_callbacks():
    """Test that ActorSurrogate callbacks can be called"""
    actor = MyTestActorSurrogate()
    
    # Test a few callbacks
    await actor.consensus_point_registration_succeeded("test-label")
    await actor.state_channel_saved()
    await actor.discover_object_instance(1, 2, "test-object")
    
    assert len(actor._callbacks_received) == 3
    assert actor._callbacks_received[0][0] == "consensus_point_registration_succeeded"
    assert actor._callbacks_received[1][0] == "state_channel_saved"
    assert actor._callbacks_received[2][0] == "discover_object_instance"


def test_attribute_handle_set():
    """Test AttributeHandleSet"""
    handles = AttributeHandleSetFactory.create([1, 2, 3])
    assert handles.size() == 3
    assert handles.is_member(1)
    assert not handles.is_member(4)
    
    handles.add(4)
    assert handles.size() == 4
    assert handles.is_member(4)


def test_supplied_attributes():
    """Test SuppliedAttributes"""
    attrs = SuppliedAttributesFactory.create()
    attrs.add(1, b"value1")
    attrs.add(2, b"value2")
    
    assert attrs.size() == 2
    assert attrs.get(1) == b"value1"
    assert attrs.get(2) == b"value2"

