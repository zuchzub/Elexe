import asyncio
import importlib
import sys
import os

from pyrogram import idle, filters
from pytgcalls.exceptions import NoActiveGroupCall

import config
from config import BANNED_USERS
from ArchMusic import LOGGER, app, userbot
from ArchMusic.core.call import ArchMusic
from ArchMusic.plugins import ALL_MODULES
from ArchMusic.utils.database import (
     get_banned_users, 
     get_gbanned, 
     get_active_chats,
     get_restart_settings, 
     update_restart_settings
)
     

loop = asyncio.get_event_loop_policy().get_event_loop()
auto_restart_task = None

async def auto_restart(interval_minutes):
    while True:
        settings = await get_restart_settings()
        if not settings["enabled"]:
            break
            
        await asyncio.sleep(interval_minutes * 60)
        await restart_bot()

async def restart_bot():
    served_chats = await get_active_chats()
    for x in served_chats:
        try:
            await app.send_message(
                x,
                f"**{config.MUSIC_BOT_NAME} kendini yeniden başlattı. Sorun için özür dileriz.\n\n10-15 saniye sonra yeniden müzik çalmaya başlayabilirsiniz.**",
            )
        except Exception:
            pass
    try:
        await app.send_message(
            config.LOG_GROUP_ID,
            f"**{config.MUSIC_BOT_NAME} kendini otomatik olarak yeniden başlatıyor.**",
        )
    except Exception:
        pass
    os.system(f"kill -9 {os.getpid()} && bash start")

@app.on_message(filters.command("autorestart") & filters.user(config.OWNER_ID))
async def auto_restart_command(_, message):
    if len(message.command) == 1:
        settings = await get_restart_settings()
        status = "✅ Açık" if settings["enabled"] else "❌ Kapalı"
        
        interval_hours = settings["interval"] // 60 
        await message.reply_text(
            f"🔄 Otomatik Yeniden Başlatma: {status}\n"
            f"⏰ Yeniden Başlatma Aralığı: {interval_hours} saat\n\n"
            "Kullanım:\n"
            "`/autorestart on` - Otomatik yeniden başlatmayı açar\n"
            "`/autorestart off` - Otomatik yeniden başlatmayı kapatır\n"
            "`/autorestart [saat]` - Yeniden başlatma aralığını ayarlar"
        )
        return

    arg = message.command[1].lower()
    
    if arg == "on":
        settings = await update_restart_settings(enabled=True)
        global auto_restart_task
        if auto_restart_task is None or auto_restart_task.done():
            auto_restart_task = asyncio.create_task(auto_restart(settings["interval"]))
        await message.reply_text("✅ Otomatik yeniden başlatma açıldı.")
        
    elif arg == "off":
        await update_restart_settings(enabled=False)
        if auto_restart_task and not auto_restart_task.done():
            auto_restart_task.cancel()
        await message.reply_text("❌ Otomatik yeniden başlatma kapatıldı.")
        
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
            
            await message.reply_text(f"⏰ Yeniden başlatma aralığı {hours} saat olarak ayarlandı.")
        except ValueError:
            await message.reply_text("❌ Geçersiz değer! Lütfen geçerli bir saat değeri girin.")

async def init():
    if (
        not config.STRING1
        and not config.STRING2
        and not config.STRING3
        and not config.STRING4
        and not config.STRING5
    ):
        LOGGER("ArchMusic").error(
            "Hiçbir Asistan İstemci Değişkeni Tanımlanmamış!.. Süreç Sonlandırılıyor."
        )
        return
    if (
        not config.SPOTIFY_CLIENT_ID
        and not config.SPOTIFY_CLIENT_SECRET
    ):
        LOGGER("ArchMusic").warning(
            "Hiçbir Spotify Değişkeni tanımlanmamış. Botunuz spotify sorgularını çalamayacak."
        )
    try:
        users = await get_gbanned()
        for user_id in users:
            BANNED_USERS.add(user_id)
        users = await get_banned_users()
        for user_id in users:
            BANNED_USERS.add(user_id)
    except:
        pass
    await app.start()
    for all_module in ALL_MODULES:
        importlib.import_module("ArchMusic.plugins" + all_module)
    LOGGER("ArchMusic.plugins").info(
        "Modüller Başarıyla İthal Edildi"
    )
    await userbot.start()
    await ArchMusic.start()
    try:
        await ArchMusic.stream_call(
            "http://docs.evostream.com/sample_content/assets/sintel1m720p.mp4"
        )
    except NoActiveGroupCall:
        LOGGER("ArchMusic").error(
            "[HATA] - \n\nLütfen Günlük Grubunuzun Sesli Aramasını Açın. Günlük grubunuzda sesli aramayı asla kapatmadığınızdan emin olun"
        )
        sys.exit()
    except:
        pass
    await ArchMusic.decorators()
    LOGGER("ArchMusic").info("Arch Music Bot Başarıyla Başlatıldı")
    
    settings = await get_restart_settings()
    if settings["enabled"]:
        global auto_restart_task
        auto_restart_task = asyncio.create_task(auto_restart(settings["interval"]))
    
    await idle()

if __name__ == "__main__":
    loop.run_until_complete(init())
    LOGGER("ArchMusic").info("Arch Music Bot Durduruluyor! Hoşçakalın")
     
