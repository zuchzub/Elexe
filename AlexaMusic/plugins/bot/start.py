# Copyright (C) 2025 by Alexa_Help @ Github, < https://github.com/TheTeamAlexa >
# All rights reserved. © Alexa © Yukki.
# Düzenleme: Kumal Music / 2025 Türkçe Animasyonlu Giriş

"""
TheTeamAlexa is a project of Telegram bots with variety of purposes.
Bu sürüm Türkçe animasyonlu giriş mesajı ile güncellenmiştir.
"""

import asyncio
from pyrogram import filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from youtubesearchpython.__future__ import VideosSearch

import config
from config import BANNED_USERS
from config.config import OWNER_ID
from strings import get_command, get_string
from AlexaMusic import Telegram, YouTube, app
from AlexaMusic.misc import SUDOERS
from AlexaMusic.plugins.play.playlist import del_plist_msg
from AlexaMusic.plugins.sudo.sudoers import sudoers_list
from AlexaMusic.utils.database import (
    add_served_chat,
    is_served_user,
    add_served_user,
    blacklisted_chats,
    get_assistant,
    get_lang,
    get_userss,
    is_on_off,
    is_served_private_chat,
)
from AlexaMusic.utils.decorators.language import LanguageStart
from AlexaMusic.utils.inline import help_pannel, private_panel, start_pannel

loop = asyncio.get_running_loop()

# ───────────────────────────────────────────────
# 🎧 /start KOMUTU — ÖZEL MESAJDA ANİMASYONLU
# ───────────────────────────────────────────────
@app.on_message(filters.command(get_command("START_COMMAND")) & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_comm(client, message: Message, _):
    await add_served_user(message.from_user.id)

    # Eğer alt komut varsa (help, song, stats vs.) onları koruyoruz
    if len(message.text.split()) > 1:
        name = message.text.split(None, 1)[1]
        # (Aşağıdaki kısım senin orijinal dosyandaki gibi kalır ↓)
        if name[:4] == "help":
            keyboard = help_pannel(_)
            return await message.reply_text(_["help_1"], reply_markup=keyboard)
        if name[:4] == "song":
            return await message.reply_text(_["song_2"])
        if name[:3] == "sta":
            m = await message.reply_text(f"📊 İstatistikler alınıyor {config.MUSIC_BOT_NAME} sunucusundan...")
            stats = await get_userss(message.from_user.id)
            tot = len(stats)
            if not stats:
                await asyncio.sleep(1)
                return await m.edit(_["ustats_1"])

            def get_stats():
                msg = ""
                limit = 0
                results = {}
                for i in stats:
                    top_list = stats[i]["spot"]
                    results[str(i)] = top_list
                    list_arranged = dict(sorted(results.items(), key=lambda item: item[1], reverse=True))
                if not results:
                    return m.edit(_["ustats_1"])
                tota = 0
                videoid = None
                for vidid, count in list_arranged.items():
                    tota += count
                    if limit == 10:
                        continue
                    if limit == 0:
                        videoid = vidid
                    limit += 1
                    details = stats.get(vidid)
                    title = (details["title"][:35]).title()
                    msg += f"🎵 [{title}](https://www.youtube.com/watch?v={vidid}) **{count} kez oynatıldı**\n\n"
                msg = f"🎶 Toplam {tot} parça | {tota} kez çalındı.\n\n" + msg
                return videoid, msg

            videoid, msg = await loop.run_in_executor(None, get_stats)
            thumbnail = await YouTube.thumbnail(videoid, True)
            await m.delete()
            return await message.reply_photo(photo=thumbnail, caption=msg)

        if name[:3] == "sud":
            return await sudoers_list(client=client, message=message, _=_)

        if name[:3] == "lyr":
            query = (str(name)).replace("lyrics_", "", 1)
            lyrical = config.lyrical
            lyrics = lyrical.get(query)
            if lyrics:
                return await Telegram.send_split_text(message, lyrics)
            else:
                return await message.reply_text("❌ Şarkı sözleri bulunamadı.")

        if name[0:3] == "del":
            return await del_plist_msg(client=client, message=message, _=_)

        if name[0:3] == "inf":
            m = await message.reply_text("🔍 Bilgi alınıyor...")
            query = (str(name)).replace("info_", "", 1)
            query = f"https://www.youtube.com/watch?v={query}"
            results = VideosSearch(query, limit=1)
            for result in (await results.next())["result"]:
                title = result["title"]
                duration = result["duration"]
                views = result["viewCount"]["short"]
                thumbnail = result["thumbnails"][0]["url"].split("?")[0]
                channel = result["channel"]["name"]
                link = result["link"]
                published = result["publishedTime"]

            caption = f"""
🎵 **Şarkı Bilgisi**
📌 Başlık: {title}
⏱ Süre: {duration}
👁 Görüntüleme: {views}
📅 Yayın: {published}
🎙 Kanal: {channel}
"""
            await m.delete()
            return await app.send_photo(
                message.chat.id,
                photo=thumbnail,
                caption=caption,
                parse_mode=enums.ParseMode.MARKDOWN,
            )

    # Eğer /start normal kullanılırsa (yani alt komut yoksa)
    # → Türkçe animasyonlu özel giriş başlat
    frames = [
        "💫",
        "💫🎵",
        "💫🎵✨",
        "💫🎵✨🌙",
        "🎶 Başlatılıyor...",
        "🎧 Bağlantı kuruluyor...",
        "🌟 Sistem hazır!",
        f"🔥 {config.MUSIC_BOT_NAME} aktif! 🔥",
    ]
    m = await message.reply_text("🎶 Hazırlanıyor...")
    for frame in frames:
        await asyncio.sleep(0.4)
        await m.edit_text(frame)

    await asyncio.sleep(0.6)
    text = f"""
🎧 **Merhaba {message.from_user.mention}!**

✨ {config.MUSIC_BOT_NAME} müzik evrenine hoş geldin!

Burada:
• Şarkı çalabilir  
• Oynatma listeleri oluşturabilir  
• Komutlarla botu yönetebilirsin 🎶  

Keyifli müzikler! 🎧
"""
    await m.edit_text(text)

    if await is_on_off(config.LOG):
        try:
            await app.send_message(
                config.LOG_GROUP_ID,
                f"{message.from_user.mention} botu başlattı 🎵",
            )
        except:
            pass


# ───────────────────────────────────────────────
# 🎵 GRUPTA /start KOMUTU
# ───────────────────────────────────────────────
@app.on_message(filters.command(get_command("START_COMMAND")) & filters.group & ~BANNED_USERS)
@LanguageStart
async def testbot(client, message: Message, _):
    out = start_pannel(_)
    return await message.reply_text(
        _["start_1"].format(message.chat.title, config.MUSIC_BOT_NAME),
        reply_markup=InlineKeyboardMarkup(out),
    )


# ───────────────────────────────────────────────
# 👋 YENİ ÜYE KARŞILAMA
# ───────────────────────────────────────────────
welcome_group = 2

@app.on_message(filters.new_chat_members, group=welcome_group)
async def welcome(client, message: Message):
    chat_id = message.chat.id
    if config.PRIVATE_BOT_MODE == str(True):
        if not await is_served_private_chat(message.chat.id):
            await message.reply_text("❌ Bu sohbet yetkili değil, bot ayrılıyor.")
            return await app.leave_chat(message.chat.id)
    else:
        await add_served_chat(chat_id)

    for member in message.new_chat_members:
        try:
            language = await get_lang(message.chat.id)
            _ = get_string(language)
            if member.id == app.id:
                out = start_pannel(_)
                await message.reply_text(
                    _["start_3"].format(
                        config.MUSIC_BOT_NAME,
                        "asistan",
                        "id",
                    ),
                    reply_markup=InlineKeyboardMarkup(out),
                )
            elif member.id in config.OWNER_ID:
                await message.reply_text(_["start_4"].format(config.MUSIC_BOT_NAME, member.mention))
            elif member.id in SUDOERS:
                await message.reply_text(_["start_5"].format(config.MUSIC_BOT_NAME, member.mention))
        except:
            return