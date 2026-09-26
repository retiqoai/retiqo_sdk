# Copyright 2026 Loreum Digital Inc
# SPDX-License-Identifier: Apache-2.0
"""
Base RTI exception classes
"""


class RTIException(Exception):
    """Base class for all RTI exceptions"""

    def __init__(self, message: str = "", cause: Exception = None):
        super().__init__(message)
        self.message = message
        self.cause = cause

    def __str__(self) -> str:
        if self.cause:
            return f"{self.message} (caused by: {self.cause})"
        return self.message


class RTIInternalError(RTIException):
    """Internal RTI error"""

    def __init__(self, message: str = "", cause: Exception = None):
        super().__init__(f"RTI internal error: {message}", cause)


class ArrayIndexOutOfBounds(RTIException):
    """Array index out of bounds"""

    def __init__(self, message: str = "", cause: Exception = None):
        super().__init__(f"Array index out of bounds: {message}", cause)

