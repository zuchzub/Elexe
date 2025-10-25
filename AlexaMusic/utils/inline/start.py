# Copyright (C) 2025 by Alexa_Help @ Github, < https://github.com/TheTeamAlexa >
# Subscribe On YT < Jankari Ki Duniya >. All rights reserved. © Alexa © Yukki.

"""
TheTeamAlexa is a project of Telegram bots with variety of purposes.
This program is free software: you can redistribute it and modify
as you want or collab if you have new ideas.
"""

from typing import Union
from pyrogram.types import InlineKeyboardButton
from config import GITHUB_REPO, SUPPORT_CHANNEL, SUPPORT_GROUP, OWNER_ID
from AlexaMusic import app


def start_pannel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_1"],
                url=f"https://t.me/{app.username}?start=help",
            ),
            InlineKeyboardButton(text=_["S_B_2"], callback_data="settings_helper"),
        ],
    ]

    if SUPPORT_CHANNEL:
        buttons.append([InlineKeyboardButton(text=_["S_B_4"], url=SUPPORT_CHANNEL)])
    if SUPPORT_GROUP:
        buttons.append([InlineKeyboardButton(text=_["S_B_3"], url=SUPPORT_GROUP)])

    return buttons


def private_panel(_, BOT_USERNAME, OWNER: Union[bool, int] = None):
    buttons = [
        [InlineKeyboardButton(text=_["S_B_8"], callback_data="settings_back_helper")],
    ]

    # Destek bağlantıları
    if SUPPORT_CHANNEL:
        buttons.append([InlineKeyboardButton(text=_["S_B_4"], url=SUPPORT_CHANNEL)])
    if SUPPORT_GROUP:
        buttons.append([InlineKeyboardButton(text=_["S_B_3"], url=SUPPORT_GROUP)])

    # Gruba ekle
    buttons.append(
        [
            InlineKeyboardButton(
                text=_["S_B_5"],
                url=f"https://t.me/{BOT_USERNAME}?startgroup=true",
            )
        ]
    )

    # Owner ve GitHub butonlarını birbirinden ayırdık
    if OWNER_ID:
        buttons.append(
            [InlineKeyboardButton(text=_["S_B_7"], user_id=OWNER_ID)]
        )

    if GITHUB_REPO:
        buttons.append(
            [InlineKeyboardButton(text=_["S_B_6"], url=https://t.me/maviduyuru]
        )

    return buttons