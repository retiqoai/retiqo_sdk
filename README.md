<!-- Copyright 2026 Loreum Digital Inc. SPDX-License-Identifier: Apache-2.0 -->

# RetiQo Python SDK

**Models think. State remembers.**

RetiQo is the institutional intelligence platform for enterprises putting AI agents into real
workflows. It gives agents and people a shared, persistent state layer, so the work they do
together builds up over time instead of disappearing when a chat session ends.

This SDK lets Python agents join that state layer: share objects, exchange interactions, reach
signed consensus, and save or restore the state of a workflow.

## Why RetiQo?

Most agent systems keep what matters in prompts and chat transcripts. The next run, or the next
model, starts cold. There's no record of what was proposed, who reviewed it, which objections
were raised, or how the outcome compared with the plan.

RetiQo moves that into explicit, shared state:

- **Stateful institutional memory.** Decisions, reviews, objections, and outcomes become
  structured state that later agent runs can read and build on.
- **Agent orchestration.** Specialist agents coordinate through shared objects, interactions,
  and consensus points, not ad-hoc messages.
- **Model-neutral.** State lives in RetiQo, not in a model's context window. You can swap the
  model behind an agent without losing what the organization has learned.
- **Auditable by design.** Agents authenticate with their own keys, consensus is signed, and every
  state change is attributable to the agent that made it.

## Core concepts

| Concept | What it is |
|---|---|
| **State Channel Definition (SCD)** | Defines a workflow's shared state: the object classes and their attributes, and the interaction classes and their parameters. |
| **State channel execution** | A running instance of an SCD. Many agents can join the same execution and work on the same state. |
| **Actor** | An agent taking part in an execution. You implement `ActorSurrogate` to receive callbacks from RetiQo. |
| **Objects and attributes** | Shared, persistent records. Actors publish and subscribe to object classes, register instances, and update attributes. |
| **Interactions** | One-off events between actors, such as a request, a review, or an approval. |
| **Consensus points** | Checkpoints where participating actors agree on the current state and sign it. |
| **Save and restore** | Snapshot an execution's state under a label and restore it later. |

## Installation

```bash
pip install retiqo
```

Requires Python 3.8 or later.

## Quick start

Each agent is provisioned once. Provisioning gives it an address and a private key, which it
then uses to connect.

```python
import asyncio

from retiqo import RTI, ActorSurrogate, WebSocketTransportProvider, provision_device
from retiqo.crypto.ec_key import ECKey
from retiqo.rti.attribute_handle_set import AttributeHandleSetFactory

SERVER_URL = "ws://localhost:8080/ws"  # your RetiQo instance host


class ReviewAgent(ActorSurrogate):
    """Receives callbacks from RetiQo. Implement every abstract method of ActorSurrogate;
    see tests/test_rti_basic.py for a complete example."""

    async def discover_object_instance(self, the_object, the_object_class, object_name):
        print(f"New shared object: {object_name}")

    # ... remaining callbacks ...


async def main():
    # 1. Provision the agent (once) and keep the address and key somewhere safe.
    address, private_key = await provision_device(SERVER_URL, app_id="your-app-id", device_id="your-agent-id")

    # 2. Connect to RetiQo infrastructure.
    transport = WebSocketTransportProvider(SERVER_URL, address, private_key)
    await transport.connect()
    rti = await RTI.create_rti_surrogate_async(transport)

    # 3. Join a running workflow (state channel execution).
    public_key = ECKey.from_private(private_key).get_public_key_bytes()
    await rti.join_state_channel_execution(
        actor_type="ReviewAgent",
        state_channel_execution_name="vendor-selection",
        public_key=public_key,
        actor_reference=ReviewAgent(),
    )

    # 4. Work with shared state.
    await rti.subscribe_object_class_attributes(1, AttributeHandleSetFactory.create([2, 3]))
    decision = await rti.register_object_instance(1, "decision-42")
    print(f"Registered decision with handle {decision}")

    # 5. Clean up.
    RTI.destroy_rti_surrogate(rti)
    await transport.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
```

See [QUICK_START.md](QUICK_START.md) for a walkthrough of each step.

## Running the tests

```bash
pip install -e ".[dev]"
pytest -v
```

The tests run offline and don't need a RetiQo instance.

## License

Apache 2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE).
