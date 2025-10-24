# Copyright (C) 2025 by Alexa_Help @ Github
# AlexaMusic - Otomatik Yeniden Başlatma Destekli Ana Modül

import asyncio
import importlib
import sys
import os

from pyrogram import idle, filters
from pytgcalls.exceptions import NoActiveGroupCall

import config
from config import BANNED_USERS
from AlexaMusic import LOGGER, app, userbot
from AlexaMusic.core.call import AlexaMusic
from AlexaMusic.plugins import ALL_MODULES
from AlexaMusic.utils.database import (
    get_banned_users,
    get_gbanned,
    get_active_chats,
    get_restart_settings,
    update_restart_settings
)

# -----------------------------------------------------------
# Global Değişkenler
# -----------------------------------------------------------
loop = asyncio.get_event_loop_policy().get_event_loop()
auto_restart_task = None


# -----------------------------------------------------------
# Otomatik Yeniden Başlatma Döngüsü
# -----------------------------------------------------------
async def auto_restart(interval_minutes: int):
    """Belirtilen aralıkta botu otomatik yeniden başlatır."""
    while True:
        settings = await get_restart_settings()
        if not settings["enabled"]:
            break
        await asyncio.sleep(interval_minutes * 60)
        await restart_bot()


async def restart_bot():
    """Tüm aktif sohbetlere ve log grubuna bildirim gönderip yeniden başlatır."""
    served_chats = await get_active_chats()
    for chat_id in served_chats:
        try:
            await app.send_message(
                chat_id,
                f"**{config.MUSIC_BOT_NAME} kendini yeniden başlatıyor...**\n"
                f"10-15 saniye içinde müzik tekrar çalmaya başlayacaktır 🎵"
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


# -----------------------------------------------------------
# Komut: /autorestart
# -----------------------------------------------------------
@app.on_message(filters.command("autorestart") & filters.user(config.OWNER_ID))
async def auto_restart_command(_, message):
    """Otomatik yeniden başlatma komutu (/autorestart)."""
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


# -----------------------------------------------------------
# Başlatıcı Fonksiyon
# -----------------------------------------------------------
async def init():
    """Botu başlatır, modülleri yükler, sesli aramayı etkinleştirir."""
    if (
        not config.STRING1
        and not config.STRING2
        and not config.STRING3
        and not config.STRING4
        and not config.STRING5
    ):
        LOGGER("AlexaMusic").error("Hiçbir asistan oturumu (STRING) tanımlanmamış. Süreç sonlandırılıyor.")
        return

    if not config.SPOTIFY_CLIENT_ID or not config.SPOTIFY_CLIENT_SECRET:
        LOGGER("AlexaMusic").warning("Spotify değişkenleri tanımlı değil. Spotify sorguları devre dışı kalacak.")

    try:
        for uid in await get_gbanned():
            BANNED_USERS.add(uid)
        for uid in await get_banned_users():
            BANNED_USERS.add(uid)
    except:
        pass

    await app.start()
    for module in ALL_MODULES:
        importlib.import_module("AlexaMusic.plugins" + module)
    LOGGER("AlexaMusic.plugins").info("Tüm modüller başarıyla yüklendi ✅")

    await userbot.start()
    await AlexaMusic.start()

    try:
        await AlexaMusic.stream_call("http://docs.evostream.com/sample_content/assets/sintel1m720p.mp4")
    except NoActiveGroupCall:
        LOGGER("AlexaMusic").error("⚠️ Lütfen log grubundaki sesli aramayı açık tutun.")
        sys.exit()
    except:
        pass

    await AlexaMusic.decorators()
    LOGGER("AlexaMusic").info("Alexa Music Bot başarıyla başlatıldı 🎶")

    settings = await get_restart_settings()
    if settings["enabled"]:
        global auto_restart_task
        auto_restart_task = asyncio.create_task(auto_restart(settings["interval"]))

    await idle()


# -----------------------------------------------------------
# Giriş Noktası
# -----------------------------------------------------------
if __name__ == "__main__":
    loop.run_until_complete(init())
    LOGGER("AlexaMusic").info("Alexa Music Bot durduruluyor... Hoşçakalın 💫")