from typing import Optional, Union, List

import asyncio
import pyrogram

from .client import Client
from ..types import ListenerTypes
from ..utils import patch_into, should_patch


@patch_into(pyrogram.types.messages_and_media.message.Message)
class Message(pyrogram.types.messages_and_media.message.Message):
    _client = Client

    @should_patch()
    async def wait_for_click(
        self,
        from_user_id: Optional[Union[Union[int, str], List[Union[int, str]]]] = None,
        timeout: Optional[int] = None,
        filters=None,
        alert: Union[str, bool] = True,
    ) -> pyrogram.types.CallbackQuery:
        message_id = getattr(self, "id", getattr(self, "message_id", None))

        return await self._client.listen(
            listener_type=ListenerTypes.CALLBACK_QUERY,
            timeout=timeout,
            filters=filters,
            unallowed_click_alert=alert,
            chat_id=self.chat.id,
            user_id=from_user_id,
            message_id=message_id,
        )

    @should_patch()
    async def wait_for_response(
        self,
        from_user_id: Optional[Union[Union[int, str], List[Union[int, str]]]] = None,
        timeout: Optional[int] = None,
        reply_only:bool=False,
        filters=None,

    ) -> pyrogram.types.Message:
        message_id = getattr(self, "id", getattr(self, "message_id", None))

        return await self._client.listen(
            listener_type=ListenerTypes.MESSAGE,
            timeout=timeout,
            filters=filters,
            chat_id=self.chat.id,
            user_id=from_user_id,
            message_id=message_id if reply_only else None,
        )
    
    @should_patch()
    async def wait_for_click_or_response(
        self,
        from_user_id: Optional[Union[Union[int, str], List[Union[int, str]]]] = None,
        timeout: Optional[int] = None,
        filters=None,
        alert: Union[str, bool] = True,
        reply_only: bool = False,
    ) -> Union[pyrogram.types.CallbackQuery, pyrogram.types.Message]:
        message_id = getattr(self, "id", getattr(self, "message_id", None))

        click_task = asyncio.ensure_future(
            self._client.listen(
                listener_type=ListenerTypes.CALLBACK_QUERY,
                timeout=timeout,
                filters=filters,
                unallowed_click_alert=alert,
                chat_id=self.chat.id,
                user_id=from_user_id,
                message_id=message_id,
            )
        )

        response_task = asyncio.ensure_future(
            self._client.listen(
                listener_type=ListenerTypes.MESSAGE,
                timeout=timeout,
                filters=filters,
                chat_id=self.chat.id,
                user_id=from_user_id,
                message_id=message_id if reply_only else None,
            )
        )

        done, pending = await asyncio.wait(
            [click_task, response_task],
            return_when=asyncio.FIRST_COMPLETED,
        )

        # Cancel listener yang kalah
        for task in pending:
            task.cancel()
            try:
                await task
            except (asyncio.CancelledError, Exception):
                pass

        # Return hasil yang duluan selesai
        return done.pop().result()

    @should_patch()
    async def delete_delay(self, delay:int=5, revoke: bool = True):
        async def do_task():
            await asyncio.sleep(delay)
            await self.delete(revoke)
        asyncio.create_task(do_task())
