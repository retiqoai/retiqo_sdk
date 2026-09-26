# Copyright 2026 Loreum Digital Inc
# SPDX-License-Identifier: Apache-2.0
"""
RTI Callback Method IDs
"""


class RTICallbackMethodIds:
    """Callback method ID constants"""

    CallbackMethodId_Null = 0

    CallbackMethodId_consensusPointRegistrationFailed = 1
    CallbackMethodId_consensusPointRegistrationSucceeded = 2
    CallbackMethodId_announceConsensusPoint = 3
    CallbackMethodId_stateChannelInConsensus = 4
    CallbackMethodId_initiateActorSave = 5
    CallbackMethodId_stateChannelSaved = 6
    CallbackMethodId_stateChannelNotSaved = 7
    CallbackMethodId_requestStateChannelRestoreSucceeded = 8
    CallbackMethodId_requestStateChannelRestoreFailed = 9
    CallbackMethodId_stateChannelRestoreBegun = 10
    CallbackMethodId_initiateActorRestore = 11
    CallbackMethodId_stateChannelRestored = 12
    CallbackMethodId_stateChannelNotRestored = 13
    CallbackMethodId_startRegistrationForObjectClass = 14
    CallbackMethodId_stopRegistrationForObjectClass = 15
    CallbackMethodId_turnInteractionsOn = 16
    CallbackMethodId_turnInteractionsOff = 17
    CallbackMethodId_discoverObjectInstance = 18
    CallbackMethodId_reflectAttributeValues_1 = 19
    CallbackMethodId_reflectAttributeValues_2 = 20
    CallbackMethodId_receiveInteraction_1 = 21
    CallbackMethodId_receiveInteraction_2 = 22
    CallbackMethodId_removeObjectInstance_1 = 23
    CallbackMethodId_removeObjectInstance_2 = 24
    CallbackMethodId_attributesInScope = 25
    CallbackMethodId_attributesOutOfScope = 26
    CallbackMethodId_provideAttributeValueUpdate = 27
    CallbackMethodId_turnUpdatesOnForObjectInstance = 28
    CallbackMethodId_turnUpdatesOffForObjectInstance = 29
    CallbackMethodId_requestAttributeOwnershipAssumption = 30
    CallbackMethodId_attributeOwnershipDivestitureNotification = 31
    CallbackMethodId_attributeOwnershipAcquisitionNotification = 32
    CallbackMethodId_attributeOwnershipUnavailable = 33
    CallbackMethodId_requestAttributeOwnershipRelease = 34
    CallbackMethodId_confirmAttributeOwnershipAcquisitionCancellation = 35
    CallbackMethodId_informAttributeOwnership = 36
    CallbackMethodId_attributeIsNotOwned = 37
    CallbackMethodId_attributeOwnedByRTI = 38



