#!/usr/bin/env python3
"""
𓆰𖤍𓆪 𝙎𝙏𝙔 ⚔️ COMPLETE FIGHTING BOT - FULLY FIXED
- Commands work in ANY chat (groups, DMs, channels)
- Uses USER's account to send messages, not bot
- Sessions saved permanently
"""

import asyncio
import json
import os
import sys
import random
import re
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from glob import glob

try:
    from telethon import TelegramClient, events
    from telethon.errors import FloodWaitError, ChatWriteForbiddenError, PhoneCodeInvalidError, SessionPasswordNeededError
    from telethon.tl.types import SendMessageTypingAction
    from telethon.tl.functions.channels import JoinChannelRequest, LeaveChannelRequest
    from colorama import init, Fore, Style
    init(autoreset=True)
except ImportError as e:
    print(f"Missing: {e}\nInstall: pip install telethon colorama")
    sys.exit(1)

# ==================== CONFIGURATION ====================

class Config:
    BOT_TOKEN = "8715561936:AAFYZzdxAgFwN_8eUprjYx8ZGyKQEFQ7NLI"
    API_ID = 33219790
    API_HASH = "ec80597289da7dbff8c96c907f2cfe31"
    
    CMD_PREFIX = "."
    USERS_DB_FILE = "sty_users.json"
    SESSIONS_DIR = "sty_sessions"
    SAVED_MEDIA_DIR = "saved_media"
    
    FIGHT_SPAM_COUNT = 30
    FIGHT_DELAY = 1.0
    DEFAULT_SPAM_DELAY = 1.0
    RAID_COUNT = 50
    
    @staticmethod
    def setup():
        os.makedirs(Config.SESSIONS_DIR, exist_ok=True)
        os.makedirs(Config.SAVED_MEDIA_DIR, exist_ok=True)

Config.setup()

# ==================== FIGHTING DATABASE ====================

AJA_LRNE_RESPONSES = [
    "aja lrne teri ma ki chut pharun 🤣🤣🤣😂",
    "teri ma ki chut aja lrne sale madarchod 🤣🤣🤣😂",
    "aa jaa bhosdike teri ma ki chut me dum hai toh 🤣🤣🤣😂",
    "sale teri ma ki chut me rehne wala keeda aja lrne 🤣🤣🤣😂",
    "bhenchod teri behan ki chut me mera lund aja lrne 🤣🤣🤣😂",
    "madarchod teri ma ki chut me kitne lund gaye aja 🤣🤣🤣😂"
]

SINGLE_WORD_RESPONSES = {
    "madarchod": "tere ma ki chut madarchod sale teri ma bhi madarchodini 🤣🤣🤣😂",
    "behenchod": "teri behan ki chut behenchod teri ma bhi randi 🤣🤣🤣😂",
    "bhosdike": "teri ma ka bhosda bhosdike tu bhi wahi se aaya 🤣🤣🤣😂",
    "harami": "teri ma ki chut harami sale poora khandan harami 🤣🤣🤣😂",
    "chutiya": "teri ma ki chut me chutiyapa mat kar sale 🤣🤣🤣😂",
    "randi": "teri ma randi teri behan randi teri aunty randi 🤣🤣🤣😂",
    "lund": "teri ma ki chut me lund leke aaja sale 🤣🤣🤣😂",
    "gaandu": "teri ma ki chut aur teri gaand dono sale 🤣🤣🤣😂",
    "bc": "bhenchod teri behan ki chut bc 🤣🤣🤣😂",
    "mc": "madarchod teri ma ki chut mc 🤣🤣🤣😂",
    "bsdk": "bhosdike teri ma ka bhosda bsdk 🤣🤣🤣😂",
    "sale": "sale teri ma ki chut sale tu bhi wahi ka 🤣🤣🤣😂",
    "kamine": "teri ma ki chut kamine sale poora khandan kamina 🤣🤣🤣😂",
    "hijda": "teri ma ki chut hijda tu hijda hai sale 🤣🤣🤣😂"
}

SPAM_MESSAGES = [
    "teri ma ki chut phar ke rakh dunga 🤣🤣🤣😂",
    "teri behan ki chut me mera lund 🤣🤣🤣😂",
    "sale teri ma kutiya hai aur tu uski kutia 🤣🤣🤣😂",
    "bhosdiwale teri ma ki chut me jhaadu marunga 🤣🤣🤣😂",
    "madarchod teri ma ki chut me kitne lund gaye 🤣🤣🤣😂"
]

GAALI_MESSAGES = [
    "teri ma ki chut phar ke rakh dunga",
    "teri behan ki chut mein mera lund",
    "sale teri ma kutiya hai aur tu uski kutia",
    "madarchod teri ma ki chut me kitne lund gaye",
    "bhenchod teri behan ki chut mein lund"
]

STYLES = {
    "bold": lambda x: ''.join(chr(0x1D400 + ord(c) - 0x41) if 'A' <= c <= 'Z' else chr(0x1D41A + ord(c) - 0x61) if 'a' <= c <= 'z' else c for c in x),
    "italic": lambda x: ''.join(chr(0x1D434 + ord(c) - 0x41) if 'A' <= c <= 'Z' else chr(0x1D44E + ord(c) - 0x61) if 'a' <= c <= 'z' else c for c in x)
}

# ==================== ACTIVE PROCESSES ====================

active_fights = {}
active_timed_spams = {}
active_raids = {}
active_tagalls = {}
active_clearalls = {}
user_login_states = {}

# ==================== DATABASE ====================

class UserDatabase:
    def __init__(self, db_file: str):
        self.db_file = db_file
        self.data = self.load()
    
    def load(self) -> Dict:
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r') as f:
                    return json.load(f)
            except:
                return {"users": {}, "total_users": 0, "sudo_users": [], "antisafe": {}, "autoreply": {}, "approved": []}
        return {"users": {}, "total_users": 0, "sudo_users": [], "antisafe": {}, "autoreply": {}, "approved": []}
    
    def save(self):
        with open(self.db_file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def add_user(self, user_id: str, user_data: Dict):
        if user_id not in self.data["users"]:
            self.data["total_users"] += 1
        self.data["users"][user_id] = user_data
        self.save()
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        return self.data["users"].get(str(user_id))
    
    def update_user(self, user_id: str, updates: Dict):
        if user_id in self.data["users"]:
            self.data["users"][user_id].update(updates)
            self.save()
    
    def get_all_users(self) -> Dict:
        return self.data["users"]
    
    def get_active_sessions(self) -> List[str]:
        active = []
        for uid, user in self.data["users"].items():
            if user.get("is_active", False):
                active.append(uid)
        return active
    
    def set_active(self, user_id: str, active: bool):
        self.update_user(user_id, {"is_active": active})
    
    def set_antisafe(self, user_id: str, enabled: bool):
        self.data["antisafe"][str(user_id)] = enabled
        self.save()
    
    def is_antisafe(self, user_id: str) -> bool:
        return self.data["antisafe"].get(str(user_id), False)
    
    def approve_user(self, user_id: str, target_id: str):
        key = f"{user_id}_{target_id}"
        if key not in self.data["approved"]:
            self.data["approved"].append(key)
            self.save()
    
    def is_approved(self, user_id: str, target_id: str) -> bool:
        return f"{user_id}_{target_id}" in self.data["approved"]
    
    def set_autoreply(self, user_id: str, message: str):
        self.data["autoreply"][str(user_id)] = message
        self.save()
    
    def get_autoreply(self, user_id: str) -> Optional[str]:
        return self.data["autoreply"].get(str(user_id))
    
    def clear_autoreply(self, user_id: str):
        if str(user_id) in self.data["autoreply"]:
            del self.data["autoreply"][str(user_id)]
            self.save()
    
    def set_setting(self, user_id: str, setting: str, value):
        user = self.get_user(user_id)
        if user:
            if "settings" not in user:
                user["settings"] = {}
            user["settings"][setting] = value
            self.update_user(user_id, {"settings": user["settings"]})
    
    def get_setting(self, user_id: str, setting: str, default=None):
        user = self.get_user(user_id)
        if user and "settings" in user:
            return user["settings"].get(setting, default)
        return default

db = UserDatabase(Config.USERS_DB_FILE)

# ==================== SESSION MANAGER ====================

class UserSessionManager:
    def __init__(self):
        self.clients: Dict[str, TelegramClient] = {}
    
    async def load_saved_sessions(self):
        """Load all saved sessions from disk on bot start"""
        session_files = glob(os.path.join(Config.SESSIONS_DIR, "user_*.session"))
        
        for session_path in session_files:
            filename = os.path.basename(session_path)
            user_id = filename.replace('user_', '').replace('.session', '')
            
            user_data = db.get_user(user_id)
            if not user_data:
                continue
            
            try:
                client = TelegramClient(session_path.replace('.session', ''), Config.API_ID, Config.API_HASH)
                await client.connect()
                
                if await client.is_user_authorized():
                    self.clients[user_id] = client
                    db.set_active(user_id, True)
                    me = await client.get_me()
                    print(f"{Fore.GREEN}[+] Loaded session for {me.first_name} (@{me.username}){Style.RESET_ALL}")
                else:
                    db.set_active(user_id, False)
                    print(f"{Fore.YELLOW}[!] Session expired for user {user_id}{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}[!] Failed to load session for {user_id}: {e}{Style.RESET_ALL}")
        
        print(f"{Fore.CYAN}[*] Loaded {len(self.clients)} active sessions{Style.RESET_ALL}")
    
    async def logout_user(self, user_id: str):
        if user_id in self.clients:
            if user_id in active_fights:
                for fight_id in list(active_fights[user_id].keys()):
                    active_fights[user_id][fight_id]["active"] = False
                del active_fights[user_id]
            await self.clients[user_id].disconnect()
            del self.clients[user_id]
        db.set_active(user_id, False)
    
    async def get_client(self, user_id: str) -> Optional[TelegramClient]:
        return self.clients.get(user_id)
    
    def is_active(self, user_id: str) -> bool:
        return user_id in self.clients

# ==================== MAIN BOT ====================

class StyFightBot:
    def __init__(self):
        self.session_manager = UserSessionManager()
        self.client = None
        self.start_time = time.time()
    
    def print_banner(self):
        banner = f"""
{Fore.RED}╔══════════════════════════════════════════════════════════════════════╗
║   {Fore.YELLOW}𓆰𖤍𓆪 𝙎𝙏𝙔 ⚔️ COMPLETE FIGHTING BOT{Fore.RED}                         ║
║   {Fore.CYAN}🔹 Commands work in ANY chat (Groups, DMs, Channels){Fore.RED}      ║
║   {Fore.CYAN}🔹 Uses YOUR account to send messages, not bot{Fore.RED}            ║
║   {Fore.CYAN}🔹 Sessions saved permanently - Logins survive restarts{Fore.RED}   ║
╚══════════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
        print(banner)
    
    async def init_main_bot(self):
        if Config.BOT_TOKEN:
            self.client = TelegramClient("sty_bot", Config.API_ID, Config.API_HASH)
            await self.client.start(bot_token=Config.BOT_TOKEN)
            me = await self.client.get_me()
            print(f"{Fore.GREEN}[+] Bot ready: @{me.username}{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}[!] No BOT_TOKEN{Style.RESET_ALL}")
            sys.exit(1)
        
        await self.session_manager.load_saved_sessions()
    
    def get_uptime(self):
        uptime = time.time() - self.start_time
        return f"{int(uptime//3600)}h {int((uptime%3600)//60)}m {int(uptime%60)}s"
    
    async def show_typing(self, client, chat_id, duration=2):
        try:
            async with client.action(chat_id, "typing"):
                await asyncio.sleep(duration)
        except:
            pass
    
    # ========== SAVE TO SAVED ==========
    async def save_to_saved(self, event, user_id: str):
        client = await self.session_manager.get_client(user_id)
        if not client:
            await event.reply("❌ Login first! Use /login")
            return
        
        if not event.is_reply:
            await event.reply("❌ Reply to a message with `.s` to save it!")
            return
        
        reply_msg = await event.get_reply_message()
        
        try:
            if reply_msg.text:
                saved = f"📝 Saved: {reply_msg.text}"
                await client.send_message("me", saved)
                await event.reply("✅ Text saved to Saved Messages!")
            elif reply_msg.media:
                path = await reply_msg.download_media(file=Config.SAVED_MEDIA_DIR)
                await client.send_file("me", path)
                await event.reply("✅ Media saved to Saved Messages!")
            else:
                await event.reply("⚠️ Cannot save this type of message!")
        except Exception as e:
            await event.reply(f"❌ Failed: {e}")
    
    # ========== FIGHTING COMMANDS ==========
    async def start_fight_attack(self, user_id: str, client, chat_id, target, is_reply=False, is_tag=False, reply_to_id=None):
        fight_id = f"{user_id}_{chat_id}_{int(time.time())}"
        
        if user_id not in active_fights:
            active_fights[user_id] = {}
        
        active_fights[user_id][fight_id] = {"active": True, "chat_id": chat_id, "is_reply": is_reply, "is_tag": is_tag, "reply_to_id": reply_to_id}
        
        count = 0
        while active_fights[user_id].get(fight_id, {}).get("active", False) and count < Config.FIGHT_SPAM_COUNT:
            msg = random.choice(SPAM_MESSAGES)
            await self.show_typing(client, chat_id, random.uniform(1, 2))
            
            try:
                if is_reply and reply_to_id:
                    await client.send_message(chat_id, msg, reply_to=reply_to_id)
                elif is_tag and isinstance(target, str):
                    await client.send_message(chat_id, f"@{target.replace('@', '')} {msg}")
                else:
                    await client.send_message(chat_id, msg)
                count += 1
            except Exception as e:
                print(f"Fight error: {e}")
            await asyncio.sleep(random.uniform(0.8, 1.5))
        
        if user_id in active_fights and fight_id in active_fights[user_id]:
            del active_fights[user_id][fight_id]
    
    async def handle_fighting(self, event, user_id: str, client, message_text: str):
        chat_id = event.chat_id
        is_reply = event.is_reply
        reply_msg = await event.get_reply_message() if is_reply else None
        
        target = None
        is_reply_mode = False
        is_tag_mode = False
        reply_to_id = None
        
        if is_reply and reply_msg:
            target = reply_msg.sender_id
            is_reply_mode = True
            reply_to_id = reply_msg.id
        else:
            mentions = re.findall(r'@(\w+)', message_text)
            if mentions:
                target = mentions[0]
                is_tag_mode = True
        
        msg_lower = message_text.lower()
        
        # "aja lrne"
        if "aja lrne" in msg_lower:
            response = random.choice(AJA_LRNE_RESPONSES)
            await self.show_typing(client, chat_id, random.uniform(1, 2))
            
            if is_reply_mode:
                await client.send_message(chat_id, response, reply_to=reply_msg.id)
            elif is_tag_mode:
                await client.send_message(chat_id, f"@{target} {response}")
            else:
                await client.send_message(chat_id, response)
            
            await event.reply(f"💀 FIGHT STARTED! {Config.FIGHT_SPAM_COUNT} messages...\nType `.ruk` to stop 💀")
            
            asyncio.create_task(self.start_fight_attack(
                user_id, client, chat_id, target or chat_id,
                is_reply=is_reply_mode, is_tag=is_tag_mode, reply_to_id=reply_to_id
            ))
            return True
        
        # Single words
        words = msg_lower.split()
        for word in words:
            if word in SINGLE_WORD_RESPONSES:
                response = SINGLE_WORD_RESPONSES[word]
                await self.show_typing(client, chat_id, random.uniform(0.8, 1.5))
                
                if is_reply_mode:
                    await client.send_message(chat_id, response, reply_to=reply_msg.id)
                elif is_tag_mode:
                    await client.send_message(chat_id, f"@{target} {response}")
                else:
                    await client.send_message(chat_id, response)
                return True
        
        return False
    
    # ========== RAID COMMAND ==========
    async def raid_command(self, event, user_id: str, client, args):
        if not event.is_reply:
            await event.reply("❌ Reply to a message with `.raid <count>` to start raid!")
            return
        
        count = int(args[0]) if args else 50
        reply_msg = await event.get_reply_message()
        chat_id = event.chat_id
        
        raid_id = f"{user_id}_{int(time.time())}"
        
        if user_id not in active_raids:
            active_raids[user_id] = {}
        active_raids[user_id][raid_id] = True
        
        await event.reply(f"🔥 RAID STARTED! Sending {count} messages!\nType `.ruk` to stop!")
        
        for i in range(count):
            if not active_raids[user_id].get(raid_id, False):
                break
            msg = random.choice(GAALI_MESSAGES)
            await self.show_typing(client, chat_id, random.uniform(0.5, 1))
            try:
                await reply_msg.reply(msg)
                await asyncio.sleep(random.uniform(0.3, 0.8))
            except:
                pass
        
        if raid_id in active_raids.get(user_id, {}):
            del active_raids[user_id][raid_id]
        await event.reply("✅ RAID COMPLETED!")
    
    # ========== STOP ALL (.ruk) ==========
    async def stop_all(self, event, user_id: str, chat_id: int):
        stopped = 0
        
        if user_id in active_fights:
            for fight_id in list(active_fights[user_id].keys()):
                if active_fights[user_id][fight_id]["chat_id"] == chat_id:
                    active_fights[user_id][fight_id]["active"] = False
                    stopped += 1
        
        if user_id in active_raids:
            for raid_id in list(active_raids[user_id].keys()):
                active_raids[user_id][raid_id] = False
                stopped += 1
        
        if user_id in active_timed_spams:
            for spam_id in list(active_timed_spams[user_id].keys()):
                active_timed_spams[user_id][spam_id] = False
                stopped += 1
        
        if user_id in active_tagalls:
            for tag_id in list(active_tagalls[user_id].keys()):
                active_tagalls[user_id][tag_id] = False
                stopped += 1
        
        if stopped > 0:
            await event.reply(f"🛑 STOPPED {stopped} active processes! 🛑")
        else:
            await event.reply("❌ No active processes to stop!")
    
    # ========== TIMED SPAM ==========
    async def timed_spam(self, event, user_id: str, client, args):
        if len(args) < 4:
            await event.reply(f"Usage: .tspam <sec> <target> <count> <msg>")
            return
        
        delay = float(args[0])
        target = args[1]
        count = int(args[2])
        message = " ".join(args[3:])
        
        spam_id = f"{user_id}_{int(time.time())}"
        
        if user_id not in active_timed_spams:
            active_timed_spams[user_id] = {}
        active_timed_spams[user_id][spam_id] = True
        
        await event.reply(f"⏰ Timed spam started!\nID: `{spam_id}`\nUse `.stopspam {spam_id}` to stop")
        
        for i in range(count):
            if not active_timed_spams[user_id].get(spam_id, False):
                break
            try:
                await client.send_message(target, f"[{i+1}/{count}] {message}")
                await asyncio.sleep(delay)
            except Exception as e:
                await event.reply(f"Error: {e}")
                break
        
        if spam_id in active_timed_spams.get(user_id, {}):
            del active_timed_spams[user_id][spam_id]
        await event.reply("✅ Timed spam completed!")
    
    # ========== CRAID ==========
    async def craid(self, event, user_id: str, client, args):
        if not event.is_reply:
            await event.reply("❌ Reply to a message with .craid <count>")
            return
        
        count = int(args[0]) if args else 50
        reply_msg = await event.get_reply_message()
        
        raid_id = f"{user_id}_{int(time.time())}"
        
        if user_id not in active_raids:
            active_raids[user_id] = {}
        active_raids[user_id][raid_id] = True
        
        await event.reply(f"🔥 CRAID started! Sending {count} replies\nUse `.ruk` to stop")
        
        for i in range(count):
            if not active_raids[user_id].get(raid_id, False):
                break
            gaali = random.choice(GAALI_MESSAGES)
            try:
                await reply_msg.reply(gaali)
                await asyncio.sleep(random.uniform(0.3, 0.8))
            except:
                pass
        
        if raid_id in active_raids.get(user_id, {}):
            del active_raids[user_id][raid_id]
        await event.reply("✅ CRAID completed!")
    
    # ========== TAGALL ==========
    async def tagall(self, event, user_id: str, client):
        chat_id = event.chat_id
        tag_id = f"{user_id}_{int(time.time())}"
        
        if user_id not in active_tagalls:
            active_tagalls[user_id] = {}
        active_tagalls[user_id][tag_id] = True
        
        await event.reply(f"🏷️ Tagall started! Use `.ruk` to stop")
        
        try:
            participants = await client.get_participants(chat_id, limit=200)
            tagged = 0
            for user in participants:
                if not active_tagalls[user_id].get(tag_id, False):
                    break
                if not user.bot and user.id != int(user_id):
                    try:
                        mention = f"[{user.first_name}](tg://user?id={user.id})"
                        await client.send_message(chat_id, f"{mention} get lost")
                        tagged += 1
                        await asyncio.sleep(0.3)
                    except:
                        pass
            await event.reply(f"✅ Tagged {tagged} members!")
        except Exception as e:
            await event.reply(f"❌ Error: {e}")
        
        if tag_id in active_tagalls.get(user_id, {}):
            del active_tagalls[user_id][tag_id]
    
    # ========== MODERATION ==========
    async def ban_user(self, event, client, args):
        if len(args) < 1:
            await event.reply("Usage: .ban @username [reason]")
            return
        username = args[0].replace('@', '')
        reason = " ".join(args[1:]) if len(args) > 1 else "No reason"
        try:
            await client.edit_permissions(event.chat_id, username, view_messages=False)
            await event.reply(f"✅ Banned @{username}\nReason: {reason}")
        except Exception as e:
            await event.reply(f"❌ Failed: {e}")
    
    async def unban_user(self, event, client, args):
        if len(args) < 1:
            await event.reply("Usage: .unban @username")
            return
        username = args[0].replace('@', '')
        try:
            await client.edit_permissions(event.chat_id, username, view_messages=True)
            await event.reply(f"✅ Unbanned @{username}")
        except Exception as e:
            await event.reply(f"❌ Failed: {e}")
    
    async def mute_user(self, event, client, args):
        if len(args) < 1:
            await event.reply("Usage: .mute @username [time] [reason]")
            return
        username = args[0].replace('@', '')
        duration = None
        reason = "No reason"
        if len(args) > 1:
            time_str = args[1]
            if time_str.endswith('s'):
                duration = int(time_str[:-1])
            elif time_str.endswith('m'):
                duration = int(time_str[:-1]) * 60
            elif time_str.endswith('h'):
                duration = int(time_str[:-1]) * 3600
            elif time_str.endswith('d'):
                duration = int(time_str[:-1]) * 86400
            else:
                reason = " ".join(args[1:])
        if len(args) > 2 and duration:
            reason = " ".join(args[2:])
        try:
            until_date = datetime.now() + timedelta(seconds=duration) if duration else None
            await client.edit_permissions(event.chat_id, username, send_messages=False, until_date=until_date)
            msg = f"✅ Muted @{username}\nReason: {reason}"
            if duration:
                msg += f"\nDuration: {args[1]}"
            await event.reply(msg)
        except Exception as e:
            await event.reply(f"❌ Failed: {e}")
    
    async def unmute_user(self, event, client, args):
        if len(args) < 1:
            await event.reply("Usage: .unmute @username")
            return
        username = args[0].replace('@', '')
        try:
            await client.edit_permissions(event.chat_id, username, send_messages=True)
            await event.reply(f"✅ Unmuted @{username}")
        except Exception as e:
            await event.reply(f"❌ Failed: {e}")
    
    async def kick_user(self, event, client, args):
        if len(args) < 1:
            await event.reply("Usage: .kick @username [reason]")
            return
        username = args[0].replace('@', '')
        reason = " ".join(args[1:]) if len(args) > 1 else "No reason"
        try:
            await client.kick_participant(event.chat_id, username)
            await event.reply(f"✅ Kicked @{username}\nReason: {reason}")
        except Exception as e:
            await event.reply(f"❌ Failed: {e}")
    
    async def clear_msgs(self, event, client, args):
        if len(args) < 1:
            await event.reply("Usage: .clear <count>")
            return
        count = int(args[0])
        await event.reply(f"🧹 Clearing {count} messages...")
        deleted = 0
        async for msg in client.iter_messages(event.chat_id, limit=count):
            await msg.delete()
            deleted += 1
            await asyncio.sleep(0.1)
        await event.reply(f"✅ Cleared {deleted} messages!")
    
    # ========== ANTISAFE ==========
    async def antisafe(self, event, user_id: str, args):
        if len(args) < 1:
            await event.reply("Usage: .antisafe on/off")
            return
        setting = args[0].lower()
        if setting == "on":
            db.set_antisafe(user_id, True)
            await event.reply("✅ AntiSafe ENABLED! DMs will be auto-deleted.")
        elif setting == "off":
            db.set_antisafe(user_id, False)
            await event.reply("❌ AntiSafe DISABLED!")
        else:
            await event.reply("Use `on` or `off`")
    
    async def approve(self, event, user_id: str):
        if event.is_private:
            target_id = str(event.chat_id)
            db.approve_user(user_id, target_id)
            await event.reply(f"✅ User approved! They can now DM you.")
        else:
            await event.reply("❌ Use this command in private chat with the user!")
    
    # ========== AUTOREPLY ==========
    async def autoreply(self, event, user_id: str, args):
        if len(args) < 1:
            await event.reply("Usage: .autoreply <message>")
            return
        message = " ".join(args)
        db.set_autoreply(user_id, message)
        await event.reply(f"✅ AutoReply set!\nReply: {message}")
    
    async def dautoreply(self, event, user_id: str):
        db.clear_autoreply(user_id)
        await event.reply("❌ AutoReply DISABLED!")
    
    # ========== BROADCAST ==========
    async def broadcast(self, event, user_id: str, client, args):
        if len(args) < 1:
            await event.reply("Usage: .broadcast <message>")
            return
        message = " ".join(args)
        await event.reply(f"📢 Broadcasting...")
        count = 0
        async for dialog in client.iter_dialogs():
            if dialog.is_group:
                try:
                    await client.send_message(dialog.id, f"📡 BROADCAST: {message}")
                    count += 1
                    await asyncio.sleep(0.5)
                except:
                    pass
        await event.reply(f"✅ Sent to {count} groups!")
    
    # ========== STYLISH ==========
    async def stylish(self, event, args):
        if len(args) < 1:
            await event.reply("Usage: .stylish <name>")
            return
        name = " ".join(args)
        result = "🎨 **Stylish Names:**\n\n"
        for style_name, style_func in STYLES.items():
            result += f"• **{style_name}:** {style_func(name)}\n"
        await event.reply(result)
    
    # ========== USER COMMANDS ==========
    async def handle_user_commands(self, event, user_id: str, cmd: str, args):
        client = await self.session_manager.get_client(user_id)
        if not client:
            await event.reply("❌ Login first! Use /login")
            return
        
        # Handle fighting commands (aja lrne, single words)
        fighting_handled = await self.handle_fighting(event, user_id, client, event.message.text)
        if fighting_handled:
            return
        
        # RAID command
        if cmd == "raid":
            await self.raid_command(event, user_id, client, args)
        
        # Stop all (.ruk)
        elif cmd == "ruk":
            await self.stop_all(event, user_id, event.chat_id)
        
        # Save
        elif cmd == "s":
            await self.save_to_saved(event, user_id)
        
        # Timed Spam
        elif cmd == "tspam":
            await self.timed_spam(event, user_id, client, args)
        elif cmd == "stopspam":
            if len(args) > 0 and user_id in active_timed_spams and args[0] in active_timed_spams[user_id]:
                active_timed_spams[user_id][args[0]] = False
                await event.reply(f"✅ Stopped spam {args[0]}")
        
        # CRAID
        elif cmd == "craid":
            await self.craid(event, user_id, client, args)
        
        # Tagall
        elif cmd == "tagall":
            await self.tagall(event, user_id, client)
        
        # Moderation
        elif cmd == "ban":
            await self.ban_user(event, client, args)
        elif cmd == "unban":
            await self.unban_user(event, client, args)
        elif cmd == "mute":
            await self.mute_user(event, client, args)
        elif cmd == "unmute":
            await self.unmute_user(event, client, args)
        elif cmd == "kick":
            await self.kick_user(event, client, args)
        elif cmd == "clear":
            await self.clear_msgs(event, client, args)
        
        # AntiSafe
        elif cmd == "antisafe":
            await self.antisafe(event, user_id, args)
        elif cmd == "approve":
            await self.approve(event, user_id)
        
        # AutoReply
        elif cmd == "autoreply":
            await self.autoreply(event, user_id, args)
        elif cmd == "dautoreply":
            await self.dautoreply(event, user_id)
        
        # Broadcast
        elif cmd == "broadcast":
            await self.broadcast(event, user_id, client, args)
        
        # Customization
        elif cmd == "stylish":
            await self.stylish(event, args)
        elif cmd == "setdelay":
            if len(args) > 0:
                db.set_setting(user_id, "spam_delay", float(args[0]))
                await event.reply(f"✅ Spam delay set to {args[0]}s")
        
        # Info
        elif cmd == "ping":
            start = time.time()
            await event.reply(f"🏓 Pong! `{round((time.time()-start)*1000)}ms`")
        elif cmd == "uptime":
            await event.reply(f"🕐 Uptime: {self.get_uptime()}")
        elif cmd == "info":
            me = await client.get_me()
            await event.reply(f"""
📊 **Your Info**

👤 **Name:** {me.first_name}
📝 **Username:** @{me.username or 'None'}
🆔 **ID:** `{me.id}`
💀 Active Fights: {len(active_fights.get(user_id, {}))}
""")
        elif cmd == "help":
            await event.reply(f"""
{Fore.CYAN}━━━━ {Fore.RED}𓆰𖤍𓆪 𝙎𝙏𝙔 ⚔️ FIGHTING BOT {Fore.CYAN}━━━━{Style.RESET_ALL}

{Fore.RED}💀 FIGHTING COMMANDS:{Style.RESET_ALL}
├ `aja lrne` - Start {Config.FIGHT_SPAM_COUNT}-message spam attack
├ `aja lrne @user` - Tag user + attack
├ `Reply + aja lrne` - Reply attack
├ `madarchod`, `behenchod`, etc. - Single word replies

{Fore.YELLOW}🔥 RAID COMMANDS:{Style.RESET_ALL}
├ `.raid 50` (reply) - Start raid on replied message
├ `.craid 50` (reply) - Reply raid
└ `.ruk` - Stop everything

{Fore.GREEN}💢 SPAM/SAVE:{Style.RESET_ALL}
├ `.tspam 1 @user 5 Hello` - Timed spam
├ `.stopspam <id>` - Stop timed spam
└ `.s` (reply) - Save to Saved Messages

{Fore.CYAN}🏷️ TAG:{Style.RESET_ALL}
└ `.tagall` - Tag all members

{Fore.MAGENTA}🛡️ MODERATION:{Style.RESET_ALL}
├ `.ban @user`, `.unban @user`
├ `.mute @user 1h`, `.unmute @user`
├ `.kick @user`, `.clear 10`

{Fore.BLUE}🔒 ANTI/AUTO:{Style.RESET_ALL}
├ `.antisafe on/off` - DM protection
├ `.approve` - Approve user (in DM)
├ `.autoreply Hello` - Auto reply
└ `.dautoreply` - Disable

{Fore.YELLOW}📢 OTHER:{Style.RESET_ALL}
├ `.broadcast Hello` - Broadcast to groups
├ `.stylish Name` - Stylish name
├ `.ping` - Check bot speed
├ `.info` - Your info
└ `.help` - This menu

{Fore.RED}🔧 SYSTEM:{Style.RESET_ALL}
├ `/login` - Login your account
├ `/logout` - Logout
├ `/users` - Show users
└ `/stats` - Bot statistics

💡 Commands work in ANY chat (Groups, DMs, Channels)!
""")
        else:
            await event.reply(f"❌ Unknown command! Type `.help`")
    
    # ========== MAIN COMMANDS (Login, etc.) ==========
    async def handle_main_commands(self, event):
        msg = event.message.text
        if not msg:
            return
        
        user_id = str(event.sender_id)
        cmd = msg.split()[0].lower()
        
        if "@" in cmd:
            cmd = cmd.split('@')[0]
        
        # LOGIN
        if cmd == "/login":
            if self.session_manager.is_active(user_id):
                await event.reply("✅ Already logged in! Use /logout first")
                return
            
            user_login_states[user_id] = {"step": "awaiting_phone"}
            await event.reply(
                "🔐 **Login to Telegram Account** 🔐\n\n"
                "Send phone number with country code.\n"
                "Example: `+919876543210`\n\n"
                "Send `/cancel` to cancel."
            )
            return
        
        # Handle login
        if user_id in user_login_states:
            state = user_login_states[user_id]
            
            if state["step"] == "awaiting_phone":
                phone = msg.strip()
                if phone.lower() == "/cancel":
                    del user_login_states[user_id]
                    await event.reply("❌ Cancelled")
                    return
                if not phone.startswith('+'):
                    await event.reply("❌ Use +919876543210 format")
                    return
                
                state["phone"] = phone
                state["step"] = "awaiting_code"
                await event.reply("📱 Sending OTP...")
                
                try:
                    temp_client = TelegramClient(f"temp_{user_id}", Config.API_ID, Config.API_HASH)
                    await temp_client.connect()
                    result = await temp_client.send_code_request(phone)
                    state["temp_client"] = temp_client
                    state["phone_code_hash"] = result.phone_code_hash
                    await event.reply("✅ OTP sent! Send code (spaces allowed):")
                except Exception as e:
                    await event.reply(f"❌ Failed: {e}")
                    del user_login_states[user_id]
                return
            
            elif state["step"] == "awaiting_code":
                code = msg.strip()
                if code.lower() == "/cancel":
                    del user_login_states[user_id]
                    await event.reply("❌ Cancelled")
                    return
                
                code = re.sub(r'\D', '', code)
                if not code.isdigit():
                    await event.reply("❌ Send numbers only")
                    return
                
                await event.reply("🔐 Verifying...")
                
                try:
                    temp_client = state["temp_client"]
                    await temp_client.sign_in(state["phone"], code, phone_code_hash=state.get("phone_code_hash"))
                    me = await temp_client.get_me()
                    
                    # Save session permanently
                    session_path = os.path.join(Config.SESSIONS_DIR, f"user_{user_id}")
                    client = TelegramClient(session_path, Config.API_ID, Config.API_HASH)
                    await client.connect()
                    await client.sign_in(state["phone"], code)
                    
                    db.add_user(user_id, {
                        "user_id": user_id, "phone": state["phone"],
                        "first_name": me.first_name, "username": me.username,
                        "telegram_id": me.id, "is_active": True,
                        "login_time": datetime.now().isoformat(), "settings": {}
                    })
                    self.session_manager.clients[user_id] = client
                    del user_login_states[user_id]
                    
                    await event.reply(f"""
✅ **LOGIN SUCCESSFUL!** ✅

Welcome {me.first_name} (@{me.username or 'No username'})!

💀 **Commands work in ANY chat (Groups, DMs, Channels)!**

Type `.help` for all commands or `aja lrne` to start fighting!
""")
                except SessionPasswordNeededError:
                    state["step"] = "awaiting_password"
                    await event.reply("🔐 2FA enabled! Send password:")
                except Exception as e:
                    await event.reply(f"❌ Failed: {e}")
                    del user_login_states[user_id]
                return
            
            elif state["step"] == "awaiting_password":
                password = msg.strip()
                if password.lower() == "/cancel":
                    del user_login_states[user_id]
                    await event.reply("❌ Cancelled")
                    return
                
                await event.reply("🔐 Verifying 2FA...")
                
                try:
                    temp_client = state["temp_client"]
                    await temp_client.sign_in(password=password)
                    me = await temp_client.get_me()
                    
                    # Save session permanently
                    session_path = os.path.join(Config.SESSIONS_DIR, f"user_{user_id}")
                    client = TelegramClient(session_path, Config.API_ID, Config.API_HASH)
                    await client.connect()
                    await client.sign_in(state["phone"])
                    
                    db.add_user(user_id, {
                        "user_id": user_id, "phone": state["phone"],
                        "first_name": me.first_name, "username": me.username,
                        "telegram_id": me.id, "is_active": True,
                        "login_time": datetime.now().isoformat(), "settings": {}
                    })
                    self.session_manager.clients[user_id] = client
                    del user_login_states[user_id]
                    
                    await event.reply(f"""
✅ **LOGIN SUCCESSFUL!** ✅

Welcome {me.first_name}!

💀 Type `aja lrne` to start fighting in ANY chat!
""")
                except Exception as e:
                    await event.reply(f"❌ Wrong password: {e}")
                return
        
        # LOGOUT
        if cmd == "/logout":
            if self.session_manager.is_active(user_id):
                await self.session_manager.logout_user(user_id)
                await event.reply("✅ Logged out!")
            else:
                await event.reply("❌ Not logged in")
            return
        
        # USERS
        if cmd == "/users":
            users = db.get_all_users()
            if not users:
                await event.reply("No users")
                return
            active = db.get_active_sessions()
            result = "📊 Users:\n"
            for uid, user in users.items():
                status = "🟢" if uid in active else "🔴"
                result += f"{status} {user.get('first_name')} (@{user.get('username')})\n"
            await event.reply(result)
            return
        
        # STATS
        if cmd == "/stats":
            users = db.get_all_users()
            await event.reply(f"""
📊 Bot Stats
👥 Total Users: {len(users)}
🟢 Active: {len(db.get_active_sessions())}
💀 Active Fights: {sum(len(v) for v in active_fights.values())}
🔥 Active Raids: {sum(len(v) for v in active_raids.values())}
""")
            return
        
        # START / HELP
        if cmd == "/start" or cmd == "/help":
            await event.reply(f"""
{Fore.RED}𓆰𖤍𓆪 𝙎𝙏𝙔 ⚔️ FIGHTING BOT{Style.RESET_ALL}

💀 **Commands work in ANY chat!**

🔐 **TO START:** Send `/login` and follow prompts!

📝 **Commands after login:**
• `aja lrne` - Start 30-message spam attack
• `.raid 50` (reply) - Raid on replied message
• `.craid 50` (reply) - Reply raid
• `.ruk` - Stop everything
• `.s` (reply) - Save to Saved Messages
• `.tagall` - Tag all members
• `.ban`, `.unban`, `.mute`, `.kick`, `.clear`
• `.antisafe on/off` - DM protection
• `.autoreply Hello` - Auto reply
• `.broadcast` - Broadcast to groups
• `.stylish` - Stylish name
• `.ping`, `.info`, `.help`

⚡ **IMPORTANT:** After login, commands work in ANY chat using YOUR account!
""")
    
    # ========== RUN ==========
    async def run(self):
        self.print_banner()
        await self.init_main_bot()
        
        print(f"{Fore.GREEN}[+] Bot running!{Style.RESET_ALL}")
        print(f"{Fore.CYAN}[*] Send /start to the bot{Style.RESET_ALL}")
        print(f"{Fore.CYAN}[*] Send /login to login your account{Style.RESET_ALL}")
        print(f"{Fore.CYAN}[*] After login, commands work in ANY chat using YOUR account!{Style.RESET_ALL}")
        
        @self.client.on(events.NewMessage)
        async def message_handler(event):
            if event.out:
                return
            
            user_id = str(event.sender_id)
            message_text = event.message.text or ""
            
            # Check if user is logging in
            if user_id in user_login_states:
                await self.handle_main_commands(event)
                return
            
            # Handle commands in ANY chat (not just bot DM)
            if message_text.startswith(Config.CMD_PREFIX) or "aja lrne" in message_text.lower():
                if self.session_manager.is_active(user_id):
                    client = await self.session_manager.get_client(user_id)
                    if client:
                        if message_text.startswith(Config.CMD_PREFIX):
                            parts = message_text.split()
                            cmd = parts[0][1:].lower()
                            args = parts[1:]
                            await self.handle_user_commands(event, user_id, cmd, args)
                        else:
                            # Handle "aja lrne" without dot
                            await self.handle_user_commands(event, user_id, "aja_lrne", [])
                    else:
                        await event.reply("❌ Login first! Use /login in bot DM")
                else:
                    # Only send login message in bot DM, not in groups
                    if event.is_private:
                        await event.reply("❌ Login first! Use /login")
            else:
                # Handle slash commands (only in bot DM)
                if event.is_private:
                    await self.handle_main_commands(event)
        
        await self.client.run_until_disconnected()

async def main():
    bot = StyFightBot()
    await bot.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[!] Stopped{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[!] Error: {e}{Style.RESET_ALL}")