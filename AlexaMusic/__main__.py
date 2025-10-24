# Copyright (C) 2025 by Alexa_Help @ Github, < https://github.com/TheTeamAlexa >
# Subscribe On YT < Jankari Ki Duniya >. All rights reserved. © Alexa © Yukki.

"""
AlexaMusic Otomatik Yeniden Başlatma Sürümü
--------------------------------------------
Bu sürüm, ArchMusic'in oto-restart sistemini AlexaMusic yapısına tam uyumlu şekilde entegre eder.
Komut: /autorestart [on/off/saat]
"""

import asyncio
import importlib
import sys
import os
from typing import Any

from pyrogram import idle, filters
from pytgcalls.exceptions import NoActiveGroupCall

import config
from config import BANNED_USERS
from AlexaMusic import LOGGER, app, userbot
from AlexaMusic.core.call import Alexa
from AlexaMusic.misc import sudo
from AlexaMusic.plugins import ALL_MODULES
from AlexaMusic.utils.database import (
    get_banned_users,
    get_gbanned,
    get_active_chats,
    get_restart_settings,
    update_restart_settings
)
from AlexaMusic.core.cookies import save_cookies


# -------------------------------
# Global değişkenler
# -------------------------------
loop = asyncio.get_event_loop_policy().get_event_loop()
auto_restart_task = None


# -------------------------------
# Otomatik yeniden başlatma
# -------------------------------
async def auto_restart(interval_minutes: int):
    """Belirtilen aralıkta botu otomatik yeniden başlatır."""
    while True:
        settings = await get_restart_settings()
        if not settings["enabled"]:
            break
        await asyncio.sleep(interval_minutes * 60)
        await restart_bot()


async def restart_bot():
    """Tüm aktif sohbetlere mesaj gönderir ve botu yeniden başlatır."""
    served_chats = await get_active_chats()
    for chat_id in served_chats:
        try:
            await app.send_message(
                chat_id,
                f"**{config.MUSIC_BOT_NAME} yeniden başlatılıyor...**\n"
                f"10-15 saniye içinde tekrar aktif olacaktır. 🎵"
            )
        except Exception:
            pass

    try:
        await app.send_message(
            config.LOG_GROUP_ID,
            f"🔁 **{config.MUSIC_BOT_NAME} otomatik yeniden başlatılıyor.**"
        )
    except Exception:
        pass

    os.system(f"kill -9 {os.getpid()} && bash start")


# -------------------------------
# Komut: /autorestart
# -------------------------------
@app.on_message(filters.command("autorestart") & filters.user(config.OWNER_ID))
async def auto_restart_command(_, message):
    """Otomatik yeniden başlatmayı yönetmek için komut."""
    global auto_restart_task

    if len(message.command) == 1:
        settings = await get_restart_settings()
        status = "✅ Açık" if settings["enabled"] else "❌ Kapalı"
        hours = settings["interval"] // 60
        await message.reply_text(
            f"🔁 **Otomatik Yeniden Başlatma Durumu:** {status}\n"
            f"⏰ **Aralık:** {hours} saat\n\n"
            "Kullanım:\n"
            "`/autorestart on` — Aç\n"
            "`/autorestart off` — Kapat\n"
            "`/autorestart [saat]` — Aralık belirle"
        )
        return

    arg = message.command[1].lower()
    if arg == "on":
        settings = await update_restart_settings(enabled=True)
        if auto_restart_task is None or auto_restart_task.done():
            auto_restart_task = asyncio.create_task(auto_restart(settings["interval"]))
        await message.reply_text("✅ Otomatik yeniden başlatma **aktif** edildi.")

    elif arg == "off":
        await update_restart_settings(enabled=False)
        if auto_restart_task and not auto_restart_task.done():
            auto_restart_task.cancel()
        await message.reply_text("❌ Otomatik yeniden başlatma **devre dışı** bırakıldı.")

    else:
        try:
            hours = int(float(arg))
            if hours <= 0:
                raise ValueError
            minutes = hours * 60
            settings = await update_restart_settings(interval=minutes)

            if settings["enabled"]:
                if auto_restart_task and not auto_restart_task.done():
                    auto_restart_task.cancel()
                auto_restart_task = asyncio.create_task(auto_restart(minutes))

            await message.reply_text(f"⏰ Yeniden başlatma aralığı **{hours} saat** olarak ayarlandı.")
        except ValueError:
            await message.reply_text("❌ Geçersiz değer! Lütfen geçerli bir saat girin.")


# -------------------------------
# Ana Başlatıcı
# -------------------------------
async def init() -> None:
    """AlexaMusic başlangıç döngüsü"""
    if all(not getattr(config, f"STRING{i}") for i in range(1, 6)):
        LOGGER("AlexaMusic").error("Add Pyrogram string session and then try...")
        exit()

    await sudo()
    try:
        for user_id in await get_gbanned():
            BANNED_USERS.add(user_id)
        for user_id in await get_banned_users():
            BANNED_USERS.add(user_id)
    except Exception:
        pass

    await app.start()
    await save_cookies()
    for module in ALL_MODULES:
        importlib.import_module(f"AlexaMusic.plugins{module}")
    LOGGER("AlexaMusic.plugins").info("Necessary Modules Imported Successfully.")
    await userbot.start()
    await Alexa.start()

    try:
        await Alexa.stream_call("https://telegra.ph/file/b60b80ccb06f7a48f68b5.mp4")
    except NoActiveGroupCall:
        LOGGER("AlexaMusic").error(
            "[ERROR] - \n\nTurn on group voice chat and don't put it off otherwise I'll stop working thanks."
        )
        exit()
    except Exception:
        pass

    await Alexa.decorators()
    LOGGER("AlexaMusic").info("Alexa Music Bot Started Successfully")

    # Oto restart kontrolü
    settings = await get_restart_settings()
    if settings["enabled"]:
        global auto_restart_task
        auto_restart_task = asyncio.create_task(auto_restart(settings["interval"]))

    await idle()
    await app.stop()
    await userbot.stop()
    LOGGER("AlexaMusic").info("Stopping Alexa Music Bot...")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(init())
    LOGGER("AlexaMusic").info("Stopping Music Bot")