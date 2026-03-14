from typing import Optional

from pyrogram import enums
from pyrogram.types import (
    ForceReply, KeyboardButton, KeyboardButtonPollType, KeyboardButtonRequestChat,
    KeyboardButtonRequestUsers, ReplyKeyboardMarkup, ReplyKeyboardRemove, WebAppInfo,
)

class ReplyKeyboard(ReplyKeyboardMarkup):
    def __init__(self, resize_keyboard=None, one_time_keyboard=None,
                 selective=None, placeholder=None, row_width=3):
        self.keyboard = list()
        super().__init__(
            keyboard=self.keyboard,
            resize_keyboard=resize_keyboard,
            one_time_keyboard=one_time_keyboard,
            selective=selective,
            placeholder=placeholder
        )
        self.row_width = row_width

    def add(self, *args, row_width=None):
        row_width = row_width or self.row_width
        rows = [
            args[i:i + row_width]
            for i in range(0, len(args), row_width)
        ]

        for row in rows:
            self.keyboard.append(row)
    
    def clear(self):
        self.keyboard.clear()

    def row(self, *args):
        self.keyboard.append([button for button in args])

class ReplyKeyboard(ReplyKeyboardMarkup):
    def __init__(
        self,
        is_persistent: Optional[bool] = None,
        resize_keyboard: Optional[bool] = None,
        one_time_keyboard: Optional[bool] = None,
        input_field_placeholder: Optional[str] = None,
        selective: Optional[bool] = None,
        placeholder: Optional[str] = None,
        row_width: int = 3,
    ):
        self.keyboard = list()
        super().__init__(
            keyboard=self.keyboard,
            is_persistent=is_persistent,
            resize_keyboard=resize_keyboard,
            one_time_keyboard=one_time_keyboard,
            input_field_placeholder=input_field_placeholder,
            selective=selective,
            placeholder=placeholder,
        )
        self.row_width = row_width

    def add(self, *args, row_width=None):
        row_width = row_width or self.row_width
        rows = [args[i:i + row_width] for i in range(0, len(args), row_width)]
        for row in rows:
            self.keyboard.append(row)

    def clear(self):
        self.keyboard.clear()

    def row(self, *args):
        self.keyboard.append([button for button in args])


class ReplyButton(KeyboardButton):
    def __init__(
        self,
        text: str = None,
        request_contact: Optional[bool] = None,
        request_location: Optional[bool] = None,
        request_poll: Optional[KeyboardButtonPollType] = None,
        web_app: Optional[WebAppInfo] = None,
        request_users: Optional[KeyboardButtonRequestUsers] = None,
        request_chat: Optional[KeyboardButtonRequestChat] = None,
        icon_custom_emoji_id: Optional[int] = None,
        style: enums.ButtonStyle = enums.ButtonStyle.DEFAULT,
    ):
        super().__init__(
            text=text,
            request_contact=request_contact,
            request_location=request_location,
            request_poll=request_poll,
            web_app=web_app,
            request_users=request_users,
            request_chat=request_chat,
            icon_custom_emoji_id=icon_custom_emoji_id,
            style=style,
        )


class ReplyKeyboardRemove(ReplyKeyboardRemove):
    def __init__(self, selective: Optional[bool] = None):
        super().__init__(selective=selective)


class ForceReply(ForceReply):
    def __init__(
        self,
        selective: Optional[bool] = None,
        placeholder: Optional[str] = None,
    ):
        super().__init__(selective=selective, placeholder=placeholder)

