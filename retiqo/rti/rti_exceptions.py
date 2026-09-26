# Copyright 2026 Loreum Digital Inc
# SPDX-License-Identifier: Apache-2.0
"""
RTI Exception constants
"""


class RTIExceptions:
    """Exception codes returned by RetiQo infrastructure"""

    Exception_Null = 0

    Exception_ArrayIndexOutOfBounds = 1
    Exception_AsynchronousDeliveryAlreadyDisabled = 2
    Exception_AsynchronousDeliveryAlreadyEnabled = 3
    Exception_AttributeAcquisitionWasNotCanceled = 4
    Exception_AttributeAcquisitionWasNotRequested = 5
    Exception_AttributeAlreadyBeingAcquired = 6
    Exception_AttributeAlreadyBeingDivested = 7
    Exception_AttributeAlreadyOwned = 8
    Exception_AttributeDivestitureWasNotRequested = 9
    Exception_AttributeNotDefined = 10
    Exception_AttributeNotKnown = 11
    Exception_AttributeNotOwned = 12
    Exception_AttributeNotPublished = 13
    Exception_CouldNotDecode = 14
    Exception_CouldNotDiscover = 15
    Exception_CouldNotOpenSCD = 16
    Exception_CouldNotRestore = 17
    Exception_DeleteRightNotHeld = 18
    Exception_DimensionNotDefined = 19

    Exception_ErrorReadingSCD = 24
    Exception_EventNotKnown = 25
    Exception_ActorAlreadyExecutionMember = 26
    Exception_ActorInternalError = 27
    Exception_ActorLoggingServiceCalls = 28
    Exception_ActorNotExecutionMember = 29
    Exception_ActorNotInConsensusSet = 30
    Exception_ActorNotSubscribed = 31
    Exception_ActorOwnsAttributes = 32
    Exception_ActorsCurrentlyJoined = 33
    Exception_ActorWasNotAskedToReleaseAttribute = 34
    Exception_StateChannelExecutionAlreadyExists = 35
    Exception_StateChannelExecutionDoesNotExist = 36
    Exception_StateChannelTimeAlreadyPassed = 37

    Exception_InteractionClassNotDefined = 39
    Exception_InteractionClassNotKnown = 40
    Exception_InteractionClassNotPublished = 41
    Exception_InteractionClassNotSubscribed = 42
    Exception_InteractionParameterNotDefined = 43
    Exception_InteractionParameterNotKnown = 44
    Exception_InvalidExtents = 45

    Exception_InvalidRegionContext = 49
    Exception_InvalidResignAction = 50

    Exception_NameNotFound = 53
    Exception_ObjectAlreadyRegistered = 54
    Exception_ObjectClassNotDefined = 55
    Exception_ObjectClassNotKnown = 56
    Exception_ObjectClassNotPublished = 57
    Exception_ObjectClassNotSubscribed = 58
    Exception_ObjectNotKnown = 59
    Exception_OwnershipAcquisitionPending = 60
    Exception_RegionInUse = 61
    Exception_RegionNotKnown = 62
    Exception_RestoreInProgress = 63
    Exception_RestoreNotRequested = 64
    Exception_RTIinternalError = 65
    Exception_SaveInProgress = 66
    Exception_SaveNotInitiated = 67
    Exception_SpaceNotDefined = 68
    Exception_SpecifiedSaveLabelDoesNotExist = 69
    Exception_ConsensusLabelNotAnnounced = 70
    Exception_ConsensusLabelOutstanding = 71
    Exception_ConsensusPointLabelWasNotAnnounced = 72
    Exception_TooManyActors = 79
    Exception_UnableToPerformSave = 80
    Exception_UnimplementedService = 81

