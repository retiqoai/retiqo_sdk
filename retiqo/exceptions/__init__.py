# Copyright 2026 Loreum Digital Inc
# SPDX-License-Identifier: Apache-2.0
"""
RTI Exception classes
"""

from retiqo.exceptions.base import RTIException, RTIInternalError, ArrayIndexOutOfBounds
from retiqo.exceptions.state_channel import (
    StateChannelExecutionDoesNotExist,
    StateChannelExecutionAlreadyExists,
    ActorsCurrentlyJoined,
    CouldNotOpenSCD,
    ErrorReadingSCD,
)
from retiqo.exceptions.actor import (
    ActorNotExecutionMember,
    ActorAlreadyExecutionMember,
    ActorOwnsAttributes,
    ActorInternalError,
)
from retiqo.exceptions.object_management import (
    ObjectNotKnown,
    ObjectAlreadyRegistered,
    ObjectClassNotDefined,
    ObjectClassNotKnown,
    ObjectClassNotPublished,
    ObjectClassNotSubscribed,
)
from retiqo.exceptions.attribute_management import (
    AttributeNotDefined,
    AttributeNotKnown,
    AttributeNotOwned,
    AttributeNotPublished,
)
from retiqo.exceptions.interaction import (
    InteractionClassNotDefined,
    InteractionClassNotKnown,
    InteractionClassNotPublished,
    InteractionClassNotSubscribed,
    InteractionParameterNotDefined,
    InteractionParameterNotKnown,
)
from retiqo.exceptions.region import (
    RegionNotKnown,
    RegionInUse,
    InvalidRegionContext,
    InvalidExtents,
    DimensionNotDefined,
    SpaceNotDefined,
)
from retiqo.exceptions.consensus import (
    ConsensusLabelNotAnnounced,
    ConsensusLabelOutstanding,
    ConsensusPointLabelWasNotAnnounced,
)
from retiqo.exceptions.save_restore import (
    SaveInProgress,
    RestoreInProgress,
    SaveNotInitiated,
    RestoreNotRequested,
    SpecifiedSaveLabelDoesNotExist,
    CouldNotRestore,
    UnableToPerformSave,
)
from retiqo.exceptions.ownership import (
    OwnershipAcquisitionPending,
    AttributeAlreadyOwned,
    AttributeAlreadyBeingAcquired,
    AttributeAlreadyBeingDivested,
    AttributeAcquisitionWasNotRequested,
    AttributeAcquisitionWasNotCanceled,
    AttributeDivestitureWasNotRequested,
    ActorWasNotAskedToReleaseAttribute,
)
from retiqo.exceptions.other import (
    InvalidResignAction,
    InvalidStateChannelTime,
    NameNotFound,
    EventNotKnown,
    CouldNotDiscover,
    CouldNotDecode,
    DeleteRightNotHeld,
    TooManyActors,
    UnimplementedService,
    AsynchronousDeliveryAlreadyEnabled,
    AsynchronousDeliveryAlreadyDisabled,
)

__all__ = [
    # Base
    "RTIException",
    "RTIInternalError",
    "ArrayIndexOutOfBounds",
    # State Channel
    "StateChannelExecutionDoesNotExist",
    "StateChannelExecutionAlreadyExists",
    "ActorsCurrentlyJoined",
    "CouldNotOpenSCD",
    "ErrorReadingSCD",
    # Actor
    "ActorNotExecutionMember",
    "ActorAlreadyExecutionMember",
    "ActorOwnsAttributes",
    "ActorInternalError",
    # Object Management
    "ObjectNotKnown",
    "ObjectAlreadyRegistered",
    "ObjectClassNotDefined",
    "ObjectClassNotKnown",
    "ObjectClassNotPublished",
    "ObjectClassNotSubscribed",
    # Attribute Management
    "AttributeNotDefined",
    "AttributeNotKnown",
    "AttributeNotOwned",
    "AttributeNotPublished",
    # Interaction
    "InteractionClassNotDefined",
    "InteractionClassNotKnown",
    "InteractionClassNotPublished",
    "InteractionClassNotSubscribed",
    "InteractionParameterNotDefined",
    "InteractionParameterNotKnown",
    # Region
    "RegionNotKnown",
    "RegionInUse",
    "InvalidRegionContext",
    "InvalidExtents",
    "DimensionNotDefined",
    "SpaceNotDefined",
    # Consensus
    "ConsensusLabelNotAnnounced",
    "ConsensusLabelOutstanding",
    "ConsensusPointLabelWasNotAnnounced",
    # Save/Restore
    "SaveInProgress",
    "RestoreInProgress",
    "SaveNotInitiated",
    "RestoreNotRequested",
    "SpecifiedSaveLabelDoesNotExist",
    "CouldNotRestore",
    "UnableToPerformSave",
    # Ownership
    "OwnershipAcquisitionPending",
    "AttributeAlreadyOwned",
    "AttributeAlreadyBeingAcquired",
    "AttributeAlreadyBeingDivested",
    "AttributeAcquisitionWasNotRequested",
    "AttributeAcquisitionWasNotCanceled",
    "AttributeDivestitureWasNotRequested",
    "ActorWasNotAskedToReleaseAttribute",
    # Other
    "InvalidResignAction",
    "InvalidStateChannelTime",
    "NameNotFound",
    "EventNotKnown",
    "CouldNotDiscover",
    "CouldNotDecode",
    "DeleteRightNotHeld",
    "TooManyActors",
    "UnimplementedService",
    "AsynchronousDeliveryAlreadyEnabled",
    "AsynchronousDeliveryAlreadyDisabled",
]

