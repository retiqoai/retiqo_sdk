<!-- Copyright 2026 Loreum Digital Inc. SPDX-License-Identifier: Apache-2.0 -->

# RetiQo Python SDK: Quick Start

This guide walks through connecting a Python agent to RetiQo and working with a workflow's shared
state. For what RetiQo is and why it exists, see the [README](README.md).

## 1. Install

```bash
pip install retiqo
```

## 2. Provision the agent

Every agent has its own identity. Provisioning registers the agent with your application and
returns an address and a private key. Do this once per agent and store the key securely: it's
what authenticates the agent and signs its consensus.

```python
from retiqo import provision_device

address, private_key = await provision_device(
    "ws://localhost:8080/ws",   # your RetiQo instance host
    app_id="your-app-id",
    device_id="your-agent-id",
)
```

## 3. Implement an actor

An actor receives callbacks from RetiQo: new shared objects, attribute updates, interactions,
consensus announcements, and save/restore events. Subclass `ActorSurrogate` and implement all of
its abstract methods. `tests/test_rti_basic.py` has a complete implementation you can copy.

```python
from retiqo import ActorSurrogate


class ReviewAgent(ActorSurrogate):
    def __init__(self):
        self._base_state = None

    def set_base_state(self, base_state):
        self._base_state = base_state

    def get_base_state(self):
        return self._base_state

    async def discover_object_instance(self, the_object, the_object_class, object_name):
        print(f"New shared object: {object_name}")

    async def reflect_attribute_values(self, the_object, the_attributes, user_supplied_tag):
        print(f"Object {the_object} changed")

    # ... remaining callbacks ...
```

## 4. Connect and join a workflow

A workflow runs as a *state channel execution*: a live instance of a State Channel Definition
(SCD). Joining it makes your agent a participant.

```python
from retiqo import RTI, WebSocketTransportProvider
from retiqo.crypto.ec_key import ECKey

transport = WebSocketTransportProvider("ws://localhost:8080/ws", address, private_key)
await transport.connect()
rti = await RTI.create_rti_surrogate_async(transport)

await rti.join_state_channel_execution(
    actor_type="ReviewAgent",
    state_channel_execution_name="vendor-selection",
    public_key=ECKey.from_private(private_key).get_public_key_bytes(),
    actor_reference=ReviewAgent(),
)
```

## 5. Work with shared state

Class, attribute, and parameter handles are the numeric IDs defined in your SCD.

```python
from retiqo.rti.attribute_handle_set import AttributeHandleSetFactory
from retiqo.rti.supplied_attributes import SuppliedAttributesFactory

# Declare what this agent reads and writes.
attributes = AttributeHandleSetFactory.create([2, 3])
await rti.subscribe_object_class_attributes(1, attributes)
await rti.publish_object_class(1, attributes)

# Create a shared record and update it.
decision = await rti.register_object_instance(1, "decision-42")

values = SuppliedAttributesFactory.create()
values.add(2, b"approved")
await rti.update_attribute_values(decision, values, b"")
```

Other agents subscribed to the same class see the new object through `discover_object_instance`
and its changes through `reflect_attribute_values`.

## 6. Agree on state and keep a snapshot

- **Consensus points:** `register_state_channel_consensus_point(label, tag)` asks participating
  agents to agree on the current state. Each agent confirms with a signed
  `consensus_point_achieved(...)`.
- **Save and restore:** `request_state_channel_save(label)` snapshots the execution, and
  `request_state_channel_restore(label)` brings it back.

## 7. Clean up

```python
RTI.destroy_rti_surrogate(rti)
await transport.disconnect()
```

## Key components

- **`RTI`**: factory for creating connections to RetiQo infrastructure
- **`RTISurrogate`**: the main interface for every RetiQo service
- **`ActorSurrogate`**: the interface your agent implements to receive callbacks
- **`WebSocketTransportProvider`**: authenticated WebSocket transport
- **`retiqo.scd`**: higher-level base classes (`BaseState`, `BaseActor`, `BaseEntity`,
  `BaseInteraction`) for building agents on top of an SCD
- **`retiqo.exceptions`**: typed exceptions for every service
