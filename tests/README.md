<!-- Copyright 2026 Loreum Digital Inc. SPDX-License-Identifier: Apache-2.0 -->

# RetiQo SDK Tests

The tests in this directory are offline unit tests. They don't need a running RetiQo infrastructure host.

```bash
pip install -e ".[dev]"
pytest -v
```

- `test_rti_basic.py`: `ActorSurrogate` callbacks, `AttributeHandleSet` and `SuppliedAttributes`
- `test_crypto.py`: ECDSA signing, verification and tamper detection
