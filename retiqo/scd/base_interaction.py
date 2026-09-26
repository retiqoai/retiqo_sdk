# Copyright 2026 Loreum Digital Inc
# SPDX-License-Identifier: Apache-2.0
"""
BaseInteraction - represents an interaction
"""
from typing import Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from retiqo.scd.base_actor import BaseActor
from retiqo.rti.rti_surrogate import RTISurrogate
from retiqo.rti.supplied_parameters import SuppliedParameters, SuppliedParametersFactory
from retiqo.scd.exceptions import InteractionException
from retiqo.exceptions import *


class BaseInteraction:
    """Base interaction"""

    def __init__(self, base_actor: "BaseActor"):
        """Initialize base interaction"""
        self.base_actor = base_actor
        self.rti = base_actor.get_rti()
        self.handle = -1
        self.parameter_values: Dict[int, bytes] = {}

    def get_handle(self) -> int:
        """Get interaction handle"""
        return self.handle

    def set_handle(self, handle: int) -> None:
        """Set interaction handle"""
        self.handle = handle

    def get_class_handle(self) -> int:
        """Get class handle - override in derived class"""
        return -1

    def get_base_actor(self) -> "BaseActor":
        """Get base actor"""
        return self.base_actor

    def get_parameter_values(self) -> Dict[int, bytes]:
        """Get parameter values"""
        return self.parameter_values

    def set_parameter_value(self, parameter_handle: int, value: bytes) -> None:
        """Set parameter value"""
        self.parameter_values[parameter_handle] = value

    def get_parameter_value(self, parameter_handle: int) -> Optional[bytes]:
        """Get parameter value"""
        return self.parameter_values.get(parameter_handle)

    @staticmethod
    async def publish(base_actor: "BaseActor", the_class: int) -> None:
        """Publish interaction class"""
        try:
            await base_actor.get_rti().publish_interaction_class(the_class)
        except (InteractionClassNotDefined, ActorNotExecutionMember, SaveInProgress, RestoreInProgress, RTIInternalError) as e:
            raise InteractionException(str(e), e)

    @staticmethod
    async def unpublish(base_actor: "BaseActor", the_class: int) -> None:
        """Unpublish interaction class"""
        try:
            await base_actor.get_rti().unpublish_interaction_class(the_class)
        except (InteractionClassNotDefined, InteractionClassNotPublished, ActorNotExecutionMember, SaveInProgress, RestoreInProgress, RTIInternalError) as e:
            raise InteractionException(str(e), e)

    @staticmethod
    async def subscribe(base_actor: "BaseActor", the_class: int) -> None:
        """Subscribe to interaction class"""
        try:
            await base_actor.get_rti().subscribe_interaction_class(the_class)
        except (InteractionClassNotDefined, ActorNotExecutionMember, ActorLoggingServiceCalls, SaveInProgress, RestoreInProgress, RTIInternalError) as e:
            raise InteractionException(str(e), e)

    @staticmethod
    async def subscribe_passively(base_actor: "BaseActor", the_class: int) -> None:
        """Subscribe passively to interaction class"""
        try:
            await base_actor.get_rti().subscribe_interaction_class_passively(the_class)
        except (InteractionClassNotDefined, ActorNotExecutionMember, ActorLoggingServiceCalls, SaveInProgress, RestoreInProgress, RTIInternalError) as e:
            raise InteractionException(str(e), e)

    @staticmethod
    async def unsubscribe(base_actor: "BaseActor", the_class: int) -> None:
        """Unsubscribe from interaction class"""
        try:
            await base_actor.get_rti().unsubscribe_interaction_class(the_class)
        except (InteractionClassNotDefined, InteractionClassNotSubscribed, ActorNotExecutionMember, SaveInProgress, RestoreInProgress, RTIInternalError) as e:
            raise InteractionException(str(e), e)

    def init_parameter_values(self, *parameters: int) -> None:
        """Initialize parameter values"""
        if parameters:
            for param_handle in parameters:
                self.set_parameter_value(param_handle, b"")

    async def send(self, user_supplied_tag: bytes) -> None:
        """Send interaction"""
        try:
            supplied_params = SuppliedParametersFactory.create()
            for param_handle, value in self.parameter_values.items():
                supplied_params.add(param_handle, value)
            
            await self.rti.send_interaction(self.handle, supplied_params, user_supplied_tag)
        except (InteractionParameterNotDefined, InteractionClassNotDefined, InteractionClassNotPublished, ActorNotExecutionMember, SaveInProgress, RestoreInProgress, RTIInternalError) as e:
            raise InteractionException(str(e), e)

