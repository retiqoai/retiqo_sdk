# Copyright 2026 Loreum Digital Inc
# SPDX-License-Identifier: Apache-2.0
"""
ConsensusState - consensus state information
"""
from typing import Optional, Dict, List


class ConsensusState:
    """Consensus state"""

    def __init__(self):
        """Initialize consensus state"""
        self._state: Optional[int] = None
        self._data: Dict = {}

    def get_state(self) -> Optional[int]:
        """Get consensus state value"""
        return self._state

    def set_state(self, state: int) -> None:
        """Set consensus state value"""
        self._state = state

    @classmethod
    def from_vector(cls, vector: List) -> "ConsensusState":
        """Create from vector format"""
        instance = cls()
        if vector and len(vector) > 0:
            instance._state = vector[0] if isinstance(vector[0], int) else 0
            # Parse additional data if present
            if len(vector) > 1:
                instance._data = vector[1] if isinstance(vector[1], dict) else {}
        return instance

