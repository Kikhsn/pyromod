from inspect import iscoroutinefunction
from typing import Callable

import pyrogram
from pyrogram.filters import Filter
from pyrogram.types import Message

from .client import Client
from ..types import ListenerTypes, Identifier
from ..utils import should_patch, patch_into


@patch_into(pyrogram.handlers.message_handler.MessageHandler)
class MessageHandler(pyrogram.handlers.message_handler.MessageHandler):
    filters: Filter
    old__init__: Callable

    @should_patch()
    def __init__(self, callback: Callable, filters: Filter = None):
        self.original_callback = callback
        self.old__init__(self.resolve_future_or_callback, filters)

    @should_patch()
    async def check_if_has_matching_listener(self, client: Client, message: Message):
        from_user = message.from_user
        from_user_id = from_user.id if from_user else None
        from_user_username = from_user.username if from_user else None

        reply_to_id = getattr(getattr(message, "reply_to_message", None), "id", None)
        cur_id = getattr(message, "id", getattr(message, "message_id", None))

        chat = message.chat
        chat_id = chat.id if chat else None
        chat_username = chat.username if chat else None

        patterns = (
            Identifier(message_id=reply_to_id, chat_id=[chat_id, chat_username],
                       from_user_id=[from_user_id, from_user_username]),
            Identifier(message_id=None, chat_id=[chat_id, chat_username],
                       from_user_id=[from_user_id, from_user_username]),
            Identifier(message_id=cur_id, chat_id=[chat_id, chat_username],
                       from_user_id=[from_user_id, from_user_username]),
        )

        listener = None
        for pat in patterns:
            listener = client.get_listener_matching_with_data(pat, ListenerTypes.MESSAGE)
            if listener:
                break

        listener_does_match = False
        if listener:
            flt = listener.filters
            if callable(flt):
                if iscoroutinefunction(flt.__call__):
                    listener_does_match = await flt(client, message)
                else:
                    listener_does_match = await client.loop.run_in_executor(None, flt, client, message)
            else:
                listener_does_match = True

        return listener_does_match, listener

    @should_patch()
    async def check(self, client: Client, message: Message):
        listener_does_match = (
            await self.check_if_has_matching_listener(client, message)
        )[0]

        if callable(self.filters):
            if iscoroutinefunction(self.filters.__call__):
                handler_does_match = await self.filters(client, message)
            else:
                handler_does_match = await client.loop.run_in_executor(
                    None, self.filters, client, message
                )
        else:
            handler_does_match = True

        # let handler get the chance to handle if listener
        # exists but its filters doesn't match
        return listener_does_match or handler_does_match

    @should_patch()
    async def resolve_future_or_callback(self, client: Client, message: Message, *args):
        listener_does_match, listener = await self.check_if_has_matching_listener(
            client, message
        )

        if listener and listener_does_match:
            client.remove_listener(listener)

            if listener.future and not listener.future.done():
                listener.future.set_result(message)

                raise pyrogram.StopPropagation
            elif listener.callback:
                if iscoroutinefunction(listener.callback):
                    await listener.callback(client, message, *args)
                else:
                    listener.callback(client, message, *args)

                raise pyrogram.StopPropagation
            else:
                raise ValueError("Listener must have either a future or a callback")
        else:
            await self.original_callback(client, message, *args)
