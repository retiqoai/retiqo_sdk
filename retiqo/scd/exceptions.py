# Copyright 2026 Loreum Digital Inc
# SPDX-License-Identifier: Apache-2.0
"""SCD exceptions"""


class EntityException(Exception):
    """Exception for entity operations"""
    def __init__(self, message: str = "", cause: Exception = None):
        self.message = message
        self.cause = cause
        super().__init__(self.message)

    def __str__(self):
        if self.cause:
            return f"{self.message} (caused by: {self.cause})"
        return self.message


class ActorException(Exception):
    """Exception for actor operations"""
    def __init__(self, message: str = "", cause: Exception = None):
        self.message = message
        self.cause = cause
        super().__init__(self.message)

    def __str__(self):
        if self.cause:
            return f"{self.message} (caused by: {self.cause})"
        return self.message


class InteractionException(Exception):
    """Exception for interaction operations"""
    def __init__(self, message: str = "", cause: Exception = None):
        self.message = message
        self.cause = cause
        super().__init__(self.message)

    def __str__(self):
        if self.cause:
            return f"{self.message} (caused by: {self.cause})"
        return self.message



