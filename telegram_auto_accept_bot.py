#!/usr/bin/env python3
"""
Telegram Auto Join Request Accepter Bot
Simple bot jo automatically join requests accept karta hai
"""

import json
import os
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ChatJoinRequestHandler, ContextTypes

# ============= BOT CONFIGURATION =============
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # Apna bot token yahan paste karein
BOT_USERNAME = "@YourBotUsername"   # Apna bot username yahan dalein

# ============= DATABASE FILE =============
DB_FILE = "auto_accept_db.json"

# ============= LOGGING SETUP =============
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# ============= DATABASE FUNCTIONS =============
def load_db():
    """Database load karta hai"""
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"groups": {}, "channels": {}, "stats": {"total_accepted": 0}}
    return {"groups": {}, "channels": {}, "stats": {"total_accepted": 0}}


def save_db(data):
    """Database save karta hai"""
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ============= COMMAND HANDLERS =============
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler"""
    user = update.effective_user
    
    # Inline buttons banao
    keyboard = [
        [
            InlineKeyboardButton("➕ Add to Group", url=f"https://t.me/{BOT_USERNAME.replace('@', '')}?startgroup=true"),
            InlineKeyboardButton("📢 Add to Channel", url=f"https://t.me/{BOT_USERNAME.replace('@', '')}?startchannel=true")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = f"""
👋 **Welcome {user.first_name}!**

🤖 Main ek Auto Join Request Accepter Bot hoon.

✅ **Main kya karta hoon:**
• Group aur Channel ke join requests automatically accept karta hoon
• Silently kaam karta hoon, koi spam nahi

📌 **Use kaise karein:**
Niche diye gaye buttons se mujhe apne group ya channel mein add karein.

💡 Setup help ke liye /help command use karein.
"""
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command handler"""
    
    help_text = """
📖 **Setup Guide**

**Group mein setup kaise karein:**

1️⃣ Bot ko apne group mein add karein
2️⃣ Bot ko **Admin** banayein
3️⃣ **Zaruri Permissions:**
   ✅ Invite users via link

**Bas itna hi!** Bot automatically join requests accept karne lagega.

---

**Channel mein setup kaise karein:**

1️⃣ Bot ko apne channel mein add karein
2️⃣ Bot ko **Admin** banayein
3️⃣ **Zaruri Permissions:**
   ✅ Invite users via link

**Ho gaya!** Bot ab requests accept karega.

---

⚠️ **Note:**
• Bot silently kaam karta hai
• Koi message post nahi karta
• Automatically sab requests accept ho jayengi
• Group/Channel private hona chahiye (join request ke liye)

🔧 **Commands:**
/start - Bot start karein
/help - Ye help message
/stats - Statistics dekhein
"""
    
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Statistics dikhata hai"""
    db = load_db()
    
    total_groups = len(db.get("groups", {}))
    total_channels = len(db.get("channels", {}))
    total_accepted = db.get("stats", {}).get("total_accepted", 0)
    
    stats_text = f"""
📊 **Bot Statistics**

👥 Active Groups: {total_groups}
📢 Active Channels: {total_channels}
✅ Total Requests Accepted: {total_accepted}

🤖 Bot smoothly chal raha hai!
"""
    
    await update.message.reply_text(stats_text, parse_mode='Markdown')


# ============= JOIN REQUEST HANDLER =============
async def handle_join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Join request automatically accept karta hai"""
    try:
        chat_join_request = update.chat_join_request
        chat = chat_join_request.chat
        user = chat_join_request.from_user
        
        # Request approve karo
        await chat_join_request.approve()
        
        # Database update karo
        db = load_db()
        
        chat_id = str(chat.id)
        chat_type = chat.type
        
        # Stats update
        if "stats" not in db:
            db["stats"] = {"total_accepted": 0}
        db["stats"]["total_accepted"] += 1
        
        # Chat info save karo
        if chat_type in ["group", "supergroup"]:
            if "groups" not in db:
                db["groups"] = {}
            if chat_id not in db["groups"]:
                db["groups"][chat_id] = {
                    "name": chat.title,
                    "added_on": datetime.now().isoformat(),
                    "accepted_count": 0
                }
            db["groups"][chat_id]["accepted_count"] += 1
            db["groups"][chat_id]["last_request"] = datetime.now().isoformat()
            
        elif chat_type == "channel":
            if "channels" not in db:
                db["channels"] = {}
            if chat_id not in db["channels"]:
                db["channels"][chat_id] = {
                    "name": chat.title,
                    "added_on": datetime.now().isoformat(),
                    "accepted_count": 0
                }
            db["channels"][chat_id]["accepted_count"] += 1
            db["channels"][chat_id]["last_request"] = datetime.now().isoformat()
        
        save_db(db)
        
        logger.info(f"✅ Join request accepted: {user.first_name} ({user.id}) in {chat.title}")
        
    except Exception as e:
        logger.error(f"❌ Error accepting join request: {e}")


# ============= MAIN FUNCTION =============
def main():
    """Bot start karta hai"""
    
    # Check karein bot token diya gaya hai ya nahi
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ ERROR: Please add your BOT_TOKEN in the script!")
        print("📝 Line 18 par apna bot token paste karein")
        return
    
    if BOT_USERNAME == "@YourBotUsername":
        print("⚠️ WARNING: Please add your BOT_USERNAME in the script!")
        print("📝 Line 19 par apna bot username dalein (e.g., @MyBot)")
    
    # Application banao
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Command handlers add karo
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("stats", stats_command))
    
    # Join request handler add karo
    application.add_handler(ChatJoinRequestHandler(handle_join_request))
    
    # Database initialize karo
    db = load_db()
    save_db(db)
    
    # Bot start karo
    print("🤖 Bot starting...")
    print(f"📝 Database file: {DB_FILE}")
    print("✅ Bot is running! Press Ctrl+C to stop.")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
