from pyrogram.emoji import *
from pyrogram import enums
from pyrogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, LoginUrl,
    SwitchInlineQueryChosenChat, CopyTextButton, CallbackGame
)
from typing import Optional, Union, List

class InlineKeyboard(InlineKeyboardMarkup):
    _SYMBOL_FIRST_PAGE = '« {}'
    _SYMBOL_PREVIOUS_PAGE = '‹ {}'
    _SYMBOL_CURRENT_PAGE = '· {} ·'
    _SYMBOL_NEXT_PAGE = '{} ›'
    _SYMBOL_LAST_PAGE = '{} »'
    _LOCALES = {
        'be_BY': f'{FLAG_BELARUS} Беларуская',          # Belarusian - Belarus
        'de_DE': f'{FLAG_GERMANY} Deutsch',             # German - Germany
        'zh_CN': f'{FLAG_CHINA} 中文',                  # Chinese - China
        'en_US': f'{FLAG_UNITED_KINGDOM} English',      # English - United States
        'fr_FR': f'{FLAG_FRANCE} Français',             # French - France
        'id_ID': f'{FLAG_INDONESIA} Bahasa Indonesia',  # Indonesian - Indonesia
        'it_IT': f'{FLAG_ITALY} Italiano',              # Italian - Italy
        'ko_KR': f'{FLAG_SOUTH_KOREA} 한국어',           # Korean - Korea
        'tr_TR': f'{FLAG_TURKEY} Türkçe',               # Turkish - Turkey
        'ru_RU': f'{FLAG_RUSSIA} Русский',              # Russian - Russia
        'es_ES': f'{FLAG_SPAIN} Español',               # Spanish - Spain
        'uk_UA': f'{FLAG_UKRAINE} Українська',          # Ukrainian - Ukraine
        'uz_UZ': f'{FLAG_UZBEKISTAN} Oʻzbekcha',        # Uzbek - Uzbekistan
    }

    def __init__(self, row_width=3):
        self.inline_keyboard = list()
        super().__init__(inline_keyboard=self.inline_keyboard)
        self.row_width = row_width

    def add(self, *args, row_width=None):
        row_width = row_width or self.row_width
        rows = [
            args[i:i + row_width]
            for i in range(0, len(args), row_width)
        ]

        for row in rows:
            self.inline_keyboard.append(row)
    
    def clear(self):
        self.inline_keyboard.clear()

    def row(self, *args):
        self.inline_keyboard.append([button for button in args])

    def _add_button(self, text, callback_data):
        return InlineKeyboardButton(
            text=text,
            callback_data=self.callback_pattern.format(
                number=callback_data)
        )

    @property
    def _left_pagination(self):
        return [
            self._add_button(
                self._SYMBOL_CURRENT_PAGE.format(number), number)
            if number == self.current_page else self._add_button(
                self._SYMBOL_NEXT_PAGE.format(number), number)
            if number == 4 else self._add_button(
                self._SYMBOL_LAST_PAGE.format(self.count_pages),
                self.count_pages)
            if number == 5 else self._add_button(number, number)
            for number in range(1, 6)
        ]

    @property
    def _middle_pagination(self):
        return [
            self._add_button(
                self._SYMBOL_FIRST_PAGE.format(1), 1),
            self._add_button(
                self._SYMBOL_PREVIOUS_PAGE.format(self.current_page - 1),
                self.current_page - 1),
            self._add_button(
                self._SYMBOL_CURRENT_PAGE.format(self.current_page),
                self.current_page),
            self._add_button(
                self._SYMBOL_NEXT_PAGE.format(self.current_page + 1),
                self.current_page + 1),
            self._add_button(
                self._SYMBOL_LAST_PAGE.format(self.count_pages),
                self.count_pages)
        ]

    @property
    def _right_pagination(self):
        return [
            self._add_button(
                self._SYMBOL_FIRST_PAGE.format(1), 1),
            self._add_button(
                self._SYMBOL_PREVIOUS_PAGE.format(self.count_pages - 3),
                self.count_pages - 3)
        ] + [
            self._add_button(
                self._SYMBOL_CURRENT_PAGE.format(number), number)
            if number == self.current_page else self._add_button(number, number)
            for number in range(self.count_pages - 2, self.count_pages + 1)
        ]

    @property
    def _full_pagination(self):
        return [
            self._add_button(number, number)
            if number != self.current_page else self._add_button(
                self._SYMBOL_CURRENT_PAGE.format(number), number)
            for number in range(1, self.count_pages + 1)
        ]

    @property
    def _build_pagination(self):
        if self.count_pages <= 5:
            return self._full_pagination
        else:
            if self.current_page <= 3:
                return self._left_pagination
            elif self.current_page > self.count_pages - 3:
                return self._right_pagination
            else:
                return self._middle_pagination

    def _clamp_page(self, n: int) -> int:
        return max(1, min(self.count_pages, n))

    @property
    def _jump_row(self):
        # Teks menunjukkan target halaman hasil lompat
        to_m10 = self._clamp_page(self.current_page - 10)
        to_m5  = self._clamp_page(self.current_page - 5)
        to_p5  = self._clamp_page(self.current_page + 5)
        to_p10 = self._clamp_page(self.current_page + 10)
        return [
            self._add_button(f'« {to_m10}', to_m10),
            self._add_button(f'‹ {to_m5}',  to_m5),
            self._add_button(f'{to_p5} ›',  to_p5),
            self._add_button(f'{to_p10} »', to_p10),
        ]
    
    def paginate(self, count_pages: int, current_page: int, callback_pattern: str, jump_row:bool=False):
        self.count_pages = count_pages
        self.current_page = current_page
        self.callback_pattern = callback_pattern

        self.inline_keyboard.append(self._build_pagination)

        if jump_row and self.count_pages >= 50:
            self.inline_keyboard.append(self._jump_row)
        
        return self.inline_keyboard

    def languages(self, callback_pattern: str, locales: Union[str, List[str]],
                  row_width: int = 2):
        locales = locales if isinstance(locales, list) else [locales]

        buttons = [
            InlineKeyboardButton(
                text=self._LOCALES.get(locales[i], 'Invalid locale'),
                callback_data=callback_pattern.format(locale=locales[i])
            )
            for i in range(0, len(locales))
        ]

        self.inline_keyboard = [
            buttons[i:i + row_width]
            for i in range(0, len(buttons), row_width)
        ]

class InlineButton(InlineKeyboardButton):
    def __init__(
        self,
        text: str = None,
        callback_data: Optional[Union[str, bytes]] = None,
        url: Optional[str] = None,
        web_app: Optional[WebAppInfo] = None,
        login_url: Optional[LoginUrl] = None,
        user_id: Optional[int] = None,
        switch_inline_query: Optional[str] = None,
        switch_inline_query_current_chat: Optional[str] = None,
        switch_inline_query_chosen_chat: Optional[SwitchInlineQueryChosenChat] = None,
        copy_text: Optional[CopyTextButton|str] = None,
        callback_game: Optional[CallbackGame] = None,
        pay: Optional[bool] = None,
        callback_data_with_password: Optional[bytes] = None,
        icon_custom_emoji_id: Optional[int] = None,
        style: enums.ButtonStyle = enums.ButtonStyle.DEFAULT,
    ):
        
        if isinstance(copy_text, str):
            copy_text = CopyTextButton(text=copy_text)
            
        super().__init__(
            text=text,
            callback_data=callback_data,
            url=url,
            web_app=web_app,
            login_url=login_url,
            user_id=user_id,
            switch_inline_query=switch_inline_query,
            switch_inline_query_current_chat=switch_inline_query_current_chat,
            switch_inline_query_chosen_chat=switch_inline_query_chosen_chat,
            copy_text=copy_text,
            callback_game=callback_game,
            pay=pay,
            callback_data_with_password=callback_data_with_password,
            icon_custom_emoji_id=icon_custom_emoji_id,
            style=style,
        )

