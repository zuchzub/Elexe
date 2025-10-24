# Copyright (C) 2025 by Alexa_Help @ Github, < https://github.com/TheTeamAlexa >
# Subscribe On YT < Jankari Ki Duniya >. All rights reserved. © Alexa © Yukki.

"""
TheTeamAlexa is a project of Telegram bots with variety of purposes.
Copyright (c) 2021 ~ Present Team Alexa <https://github.com/TheTeamAlexa>

This program is free software: you can redistribute it and can modify
as you want or you can collabe if you have new ideas.
"""

from typing import Dict, List, Union
from AlexaMusic.core.mongo import mongodb

queriesdb = mongodb.queries
userdb = mongodb.userstats
chattopdb = mongodb.chatstats
authuserdb = mongodb.authuser
gbansdb = mongodb.gban
sudoersdb = mongodb.sudoers
chatsdb = mongodb.chats
blacklist_chatdb = mongodb.blacklistChat
usersdb = mongodb.tgusersdb
playlistdb = mongodb.playlist
blockeddb = mongodb.blockedusers
privatedb = mongodb.privatechats


# Playlist
async def _get_playlists(chat_id: int) -> Dict[str, int]:
    _notes = await playlistdb.find_one({"chat_id": chat_id})
    return _notes["notes"] if _notes else {}

async def get_playlist_names(chat_id: int) -> List[str]:
    return list(await _get_playlists(chat_id))

async def get_playlist(chat_id: int, name: str) -> Union[bool, dict]:
    _notes = await _get_playlists(chat_id)
    return _notes[name] if name in _notes else False

async def save_playlist(chat_id: int, name: str, note: dict):
    _notes = await _get_playlists(chat_id)
    _notes[name] = note
    await playlistdb.update_one({"chat_id": chat_id}, {"$set": {"notes": _notes}}, upsert=True)

async def delete_playlist(chat_id: int, name: str) -> bool:
    notesd = await _get_playlists(chat_id)
    if name in notesd:
        del notesd[name]
        await playlistdb.update_one({"chat_id": chat_id}, {"$set": {"notes": notesd}}, upsert=True)
        return True
    return False


# Users
async def is_served_user(user_id: int) -> bool:
    user = await usersdb.find_one({"user_id": user_id})
    return bool(user)

async def get_served_users() -> list:
    users_list = []
    async for user in usersdb.find({"user_id": {"$gt": 0}}):
        users_list.append(user)
    return users_list

async def add_served_user(user_id: int):
    is_served = await is_served_user(user_id)
    if not is_served:
        return await usersdb.insert_one({"user_id": user_id})


# Served Chats
async def get_served_chats() -> list:
    chats_list = []
    async for chat in chatsdb.find({"chat_id": {"$lt": 0}}):
        chats_list.append(chat)
    return chats_list

async def is_served_chat(chat_id: int) -> bool:
    chat = await chatsdb.find_one({"chat_id": chat_id})
    return bool(chat)

async def add_served_chat(chat_id: int):
    if not await is_served_chat(chat_id):
        return await chatsdb.insert_one({"chat_id": chat_id})

async def delete_served_chat(chat_id: int):
    await chatsdb.delete_one({"chat_id": chat_id})


# Blacklisted Chats
async def blacklisted_chats() -> list:
    chats_list = []
    async for chat in blacklist_chatdb.find({"chat_id": {"$lt": 0}}):
        chats_list.append(chat["chat_id"])
    return chats_list

async def blacklist_chat(chat_id: int) -> bool:
    if not await blacklist_chatdb.find_one({"chat_id": chat_id}):
        await blacklist_chatdb.insert_one({"chat_id": chat_id})
        return True
    return False

async def whitelist_chat(chat_id: int) -> bool:
    if await blacklist_chatdb.find_one({"chat_id": chat_id}):
        await blacklist_chatdb.delete_one({"chat_id": chat_id})
        return True
    return False


# Private Chats
async def get_private_served_chats() -> list:
    chats_list = []
    async for chat in privatedb.find({"chat_id": {"$lt": 0}}):
        chats_list.append(chat)
    return chats_list

async def is_served_private_chat(chat_id: int) -> bool:
    chat = await privatedb.find_one({"chat_id": chat_id})
    return bool(chat)

async def add_private_chat(chat_id: int):
    if not await is_served_private_chat(chat_id):
        return await privatedb.insert_one({"chat_id": chat_id})

async def remove_private_chat(chat_id: int):
    if await is_served_private_chat(chat_id):
        return await privatedb.delete_one({"chat_id": chat_id})


# Auth Users
async def _get_authusers(chat_id: int) -> Dict[str, int]:
    _notes = await authuserdb.find_one({"chat_id": chat_id})
    return _notes["notes"] if _notes else {}

async def get_authuser_names(chat_id: int) -> List[str]:
    return list(await _get_authusers(chat_id))

async def get_authuser(chat_id: int, name: str) -> Union[bool, dict]:
    _notes = await _get_authusers(chat_id)
    return _notes[name] if name in _notes else False

async def save_authuser(chat_id: int, name: str, note: dict):
    _notes = await _get_authusers(chat_id)
    _notes[name] = note
    await authuserdb.update_one({"chat_id": chat_id}, {"$set": {"notes": _notes}}, upsert=True)

async def delete_authuser(chat_id: int, name: str) -> bool:
    notesd = await _get_authusers(chat_id)
    if name in notesd:
        del notesd[name]
        await authuserdb.update_one({"chat_id": chat_id}, {"$set": {"notes": notesd}}, upsert=True)
        return True
    return False


# Gbans / Blocked Users
async def get_gbanned() -> list:
    results = []
    async for user in gbansdb.find({"user_id": {"$gt": 0}}):
        results.append(user["user_id"])
    return results

async def is_gbanned_user(user_id: int) -> bool:
    user = await gbansdb.find_one({"user_id": user_id})
    return bool(user)

async def add_gban_user(user_id: int):
    if not await is_gbanned_user(user_id):
        return await gbansdb.insert_one({"user_id": user_id})

async def remove_gban_user(user_id: int):
    if await is_gbanned_user(user_id):
        return await gbansdb.delete_one({"user_id": user_id})


# Sudoers
async def get_sudoers() -> list:
    sudoers = await sudoersdb.find_one({"sudo": "sudo"})
    return sudoers["sudoers"] if sudoers else []

async def add_sudo(user_id: int) -> bool:
    sudoers = await get_sudoers()
    sudoers.append(user_id)
    await sudoersdb.update_one({"sudo": "sudo"}, {"$set": {"sudoers": sudoers}}, upsert=True)
    return True

async def remove_sudo(user_id: int) -> bool:
    sudoers = await get_sudoers()
    sudoers.remove(user_id)
    await sudoersdb.update_one({"sudo": "sudo"}, {"$set": {"sudoers": sudoers}}, upsert=True)
    return True


# Queries
async def get_queries() -> int:
    chat_id = 98324
    mode = await queriesdb.find_one({"chat_id": chat_id})
    return mode["mode"] if mode else 0

async def set_queries(mode: int):
    chat_id = 98324
    queries = await queriesdb.find_one({"chat_id": chat_id})
    if queries:
        mode = queries["mode"] + mode
    return await queriesdb.update_one({"chat_id": chat_id}, {"$set": {"mode": mode}}, upsert=True)


# ===============================================================
# 🔁 Otomatik Yeniden Başlatma Ayarları (Auto Restart System)
# ===============================================================

restart_settings = {
    "enabled": False,  # Varsayılan: kapalı
    "interval": 360,   # Varsayılan: 6 saat (dakika cinsinden)
}

async def get_restart_settings() -> dict:
    """Geçerli yeniden başlatma ayarlarını döndürür."""
    return restart_settings

async def update_restart_settings(enabled: bool = None, interval: int = None) -> dict:
    """Otomatik yeniden başlatma ayarlarını günceller."""
    if enabled is not None:
        restart_settings["enabled"] = enabled
    if interval is not None:
        restart_settings["interval"] = interval
    return restart_settings