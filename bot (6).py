# CREDIT: MISTER STARK.                                -_-
# REPOSITORY TO PUBLIC HAI SO CREDIT MT CHURANA LADLE  -_-
#-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-

import logging
import json
import asyncio
import requests
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ===================== CONFIG =====================
BOT_TOKEN = "YOUR_BOT_TOKEN"

# ---- Existing APIs ----
NUM_API_URL = "YOUR_NUM_API_URL"
NUM_API_KEY = ""

VEHICLE_API_URL = "YOUR_VEHICLE_API_URL"
VEHICLE_API_KEY = ""

FF_API_URL = "FREE_FIRE_API"
FF_API_KEY = ""

# ---- Future APIs ----
AB_API_URL = "YOUR_ADHAR_INFO_API_URL"
AB_API_KEY = ""

BC_API_URL = "https://stark-free-osint-api.vercel.app/info?type=tg&tg_id="
BC_API_KEY = ""

CD_API_URL = "YOUR_RASHAN_CARD_API_URL"
CD_API_KEY = ""

# ---- New APIs ----
PAN_API_URL = "YOUR_PAN_API_URL"
PAN_API_KEY = ""

POK_API_URL = "YOUR_POK_NUMBER_API_URL"
POK_API_KEY = ""

AK_API_URL = "YOUR_AK_API_URL" #FOR FUTURE FEATURES
AK_API_KEY = ""

# ---- Group Restriction ----
ALLOWED_GROUP_ID = -1003562666331
GROUP_LINK = "https://t.me/CarelessxWorld"
OWNER_ID = 8028749711

# ---- Start Message Image ----
START_IMAGE_URL = "https://files.catbox.moe/8lo2n8.jpg"

# ---- Inline Buttons ----
SUPPORT_LINK = "https://t.me/CarelessxWorld"
# ==================================================

# ---- Runtime State ----
auto_delete_enabled = True
auto_delete_seconds = 15
sudo_users = set()
approved_groups = {-1003562666331}  # Default group pre-approved
maintenance_mode = False
rate_limit_seconds = 5
user_last_command = {}

# ---- Branding ----
OWNER_USERNAME = "@carelessxowner"
OWNER_TG_LINK = "https://t.me/carelessxowner"
POWERED_BY = "Mister Stark"

# ---- Stats ----
stats = {
    "num": 0,
    "vehicle": 0,
    "ff": 0,
    "ab": 0,
    "bc": 0,
    "cd": 0,
    "pan": 0,
    "pok": 0,
    "ak": 0,
    "total": 0,
    "start_time": datetime.now().strftime("%d-%m-%Y %H:%M")
}

logging.basicConfig(level=logging.INFO)


# =================== PERMISSION CHECKS ===================

def is_owner(update: Update) -> bool:
    return update.effective_user.id == OWNER_ID

def is_sudo(update: Update) -> bool:
    return update.effective_user.id in sudo_users

def is_owner_or_sudo(update: Update) -> bool:
    return is_owner(update) or is_sudo(update)

def is_allowed(update: Update) -> bool:
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    return chat_id in approved_groups or user_id == OWNER_ID or user_id in sudo_users


# =================== RATE LIMIT ===================

def check_rate_limit(user_id: int) -> int:
    """0 return karo agar allowed, warna remaining seconds"""
    if user_id == OWNER_ID or user_id in sudo_users:
        return 0
    now = datetime.now().timestamp()
    last = user_last_command.get(user_id, 0)
    diff = now - last
    if diff < rate_limit_seconds:
        return int(rate_limit_seconds - diff) + 1
    user_last_command[user_id] = now
    return 0


# =================== HELPERS ===================

async def send_group_warning(update: Update):
    msg = (
        "❌ *ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ᴏᴜʀ ɢʀᴏᴜᴘ!*\n\n"
        "👇 *ᴊᴏɪɴ ᴛʜᴇ ɢʀᴏᴜᴘ ғɪʀsᴛ, ᴛʜᴇɴ ᴜsᴇ ᴄᴏᴍᴍᴀɴᴅs:*\n"
        f"[ᴊᴏɪɴ ᴛʜᴇ ɢʀᴏᴜᴘ]({GROUP_LINK})"
    )
    sent = await update.message.reply_text(msg, parse_mode="Markdown", disable_web_page_preview=True)
    asyncio.create_task(auto_delete_msg(sent, 20))


async def auto_delete_msg(message, delay: int):
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except Exception:
        pass


def call_api(url: str, api_key: str = None) -> dict:
    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        return response.json()
    except requests.exceptions.Timeout:
        return {"error": "Request timeout"}
    except requests.exceptions.ConnectionError:
        return {"error": "API se connect nahi ho paya"}
    except Exception as e:
        return {"error": str(e)}


def remove_branding(data):
    """API ke branding/owner fields hatao"""
    REMOVE_KEYS = {
        "branding", "developer", "processed_by",
        "owner_contact", "api_owner", "credit",
        "credits", "powered_by", "made_by",
        "api_used", "api_name"
    }
    if isinstance(data, dict):
        return {k: remove_branding(v) for k, v in data.items() if k.lower() not in REMOVE_KEYS}
    elif isinstance(data, list):
        return [remove_branding(i) for i in data]
    return data


def format_response(data: dict) -> str:
    if "error" in data:
        return f"❌ Error: {data['error']}"
    clean_data = remove_branding(data)
    pretty = json.dumps(clean_data, indent=2, ensure_ascii=False)
    return f"```\n{pretty}\n```"


def get_start_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("⌯ 𝐎𝐬ɪɴᴛ 𝐆ʀᴏᴜᴘ ⌯", url=GROUP_LINK),
        ],
        [
            InlineKeyboardButton("⌯ 𝐔ᴘᴅᴀᴛᴇ ⌯", url="https://t.me/+92MMlAl05kA5MTE1"),
            InlineKeyboardButton("⌯ 𝐌ʏ 𝐌ᴧsᴛᴇʀ ⌯", url="https://t.me/carelessxowner"),
        ],
        [
            InlineKeyboardButton("⌯ 𝐇єʟᴘ 𝐀ηᴅ 𝐂ᴏᴍᴍᴧηᴅ𝐬 ⌯", url=""),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_help_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("📋 𝐇ᴇʟᴘ 1", callback_data="help1"),
            InlineKeyboardButton("🔐 𝐇ᴇʟᴘ 2", callback_data="help2"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


# =================== START ===================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
    f"""
👋 *ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴏsɪɴᴛ ʙᴏᴛ!*

📋 *ᴜsᴇ /help ᴛᴏ sᴇᴇ ᴧʟʟ ᴄᴏᴍᴍᴧɴᴅs.*
🔍 *ᴛʜɪs ʙᴏᴛ ʜᴇʟᴘs ʏᴏᴜ ғɪɴᴅ ᴠᴧʀɪᴏᴜs ɪɴғᴏʀᴍᴧᴛɪᴏɴ ǫᴜɪᴄᴋʟʏ ᴧɴᴅ ᴇᴧsɪʟʏ.*

📌 *ᴛᴏ ᴜsᴇ ᴧʟʟ ᴄᴏᴍᴍᴧɴᴅs, ʏᴏᴜ ᴍᴜsᴛ ᴊᴏɪɴ ᴏᴜʀ ᴏғғɪᴄɪᴧʟ ɢʀᴏᴜᴘ.*
👇 *ᴄʟɪᴄᴋ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ᴊᴏɪɴ!*
[ᴊᴏɪɴ ᴛʜᴇ ɢʀᴏᴜᴘ]({GROUP_LINK})
⚡ *_ᴘᴏᴡᴇʀᴇᴅ ʙʏ_* [ᴍɪsᴛᴇʀ sᴛᴧʀᴋ](https://t.me/carelessxowner)
"""
    )
    await update.message.reply_photo(
        photo=START_IMAGE_URL,
        caption=msg,
        parse_mode="Markdown",
        reply_markup=get_start_keyboard()
    )


# =================== HELP ===================

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update):
        await send_group_warning(update)
        return

    msg = (
        "📚 *ʜᴇʟᴘ ᴍᴇɴᴜ*\n\n"
        "*❖ ᴄʟɪᴄᴋ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ᴛᴏ ᴠɪᴇᴡ ᴧʟʟ ʜᴇʟᴘ ᴄᴏᴍᴍᴧɴᴅs.*\n\n"
        "➻ ᴧʟʟ *ᴄᴏᴍᴍᴧɴᴅs ᴏғ ʜᴇʟᴘ 1* ᴄᴧɴ ʙᴇ ᴜsᴇᴅ ʙʏ ᴜsᴇʀs ᴧɴᴅ ᴛʜᴇ ᴏᴡɴᴇʀ.\n"
        "➻ ʙᴜᴛ ᴛʜᴇ *ᴄᴏᴍᴍᴧɴᴅs ᴏғ ʜᴇʟᴘ 2* ᴧʀᴇ ᴏɴʟʏ ғᴏʀ ᴛʜᴇ ᴏᴡɴᴇʀ ᴧɴᴅ sᴜᴅᴏᴇʀs."
    )
    await update.message.reply_text(
        msg,
        parse_mode="Markdown",
        reply_markup=get_help_keyboard()
    )


async def help_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "help1":
        msg = (
            "📋 *ᴜsᴇʀ ᴄᴏᴍᴍᴧɴᴅs*\n\n"
            "➻ `/start` — sᴛᴧʀᴛ ᴛʜᴇ ʙᴏᴛ\n"
            "➻ `/help` — ᴠɪᴇᴡ ᴛʜɪs ᴍᴇɴᴜ\n"
            "➻ `/id` — ᴄʜᴇᴄᴋ ʏᴏᴜʀ ᴛᴇʟᴇɢʀᴧᴍ ɪᴅ\n\n"
            "🔍 *ɪɴғᴏ ᴄᴏᴍᴍᴧɴᴅs:*\n"
            "➻ `/num [number]` — ɢᴇᴛ ᴍᴏʙɪʟᴇ ɴᴜᴍʙᴇʀ ɪɴғᴏ\n"
            "➻ `/vehicle [RC]` — ɢᴇᴛ ᴠᴇʜɪᴄʟᴇ / ʀᴄ ᴅᴇᴛᴧɪʟs\n"
            "➻ `/ff [UID]` — ɢᴇᴛ ғʀᴇᴇ ғɪʀᴇ ᴘʟᴧʏᴇʀ ɪɴғᴏ\n"
            "➻ `/a [value]` — ᴄᴏᴍɪɴɢ sᴏᴏɴ\n"
            "➻ `/tg [value]` — ᴄᴏᴍɪɴɢ sᴏᴏɴ\n"
            "➻ `/cd [value]` — ᴄᴏᴍɪɴɢ sᴏᴏɴ"
        )
        
    elif query.data == "help2":
        if not is_owner_or_sudo(update):
            await query.edit_message_text(
                "❌ *Only For Owner & sudoers*",
                parse_mode="Markdown"
            )
            return
        msg = (
            "🔐 *ᴏᴡɴᴇʀ & sᴜᴅᴏ ᴄᴏᴍᴍᴧɴᴅs*\n\n"
            "👑 *ᴏɴʟʏ ᴏᴡɴᴇʀ:*\n"
            "➻ `/ping` — ᴄʜᴇᴄᴋ ɪғ ʙᴏᴛ ɪs ᴏɴʟɪɴᴇ\n"
            "➻ `/addsudo [id]` — ᴧᴅᴅ sᴜᴅᴏ\n"
            "➻ `/rmsudo [id]` — ʀᴇᴍᴏᴠᴇ sᴜᴅᴏ\n"
            "➻ `/addgc [id]` — ᴧᴘᴘʀᴏᴠᴇ ᴧ ɢʀᴏᴜᴘ\n"
            "➻ `/rmgc [id]` — ʀᴇᴍᴏᴠᴇ ɢʀᴏᴜᴘ ᴧᴘᴘʀᴏᴠᴧʟ\n"
            "➻ `/broadcast [msg]` — sᴇɴᴅ ᴧɴ ᴧɴɴᴏᴜɴᴄᴇᴍᴇɴᴛ ɪɴ ɢʀᴏᴜᴘs\n\n"
            "🛡 *ᴏᴡɴᴇʀ + sᴜᴅᴏ:*\n"
            "➻ `/sudolist` — ᴠɪᴇᴡ sᴜᴅᴏ ʟɪsᴛ\n"
            "➻ `/gclist` — ᴠɪᴇᴡ ᴧᴘᴘʀᴏᴠᴇᴅ ɢʀᴏᴜᴘs\n"
            "➻ `/settime on/off/sec` — ᴄᴏɴᴛʀᴏʟ ᴧᴜᴛᴏ ᴅᴇʟᴇᴛᴇ\n"
            "➻ `/maintenance on/off` — ᴍᴧɪɴᴛᴇɴᴧɴᴄᴇ ᴍᴏᴅᴇ\n"
            "➻ `/stats` — ʙᴏᴛ ᴜsᴧɢᴇ sᴛᴧᴛs\n"
            "➻ `/setrl [seconds]` — sᴇᴛ ʀᴧᴛᴇ ʟɪᴍɪᴛ"
        )

    await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=get_help_keyboard())


# =================== PING & ID ===================

async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update):
        await send_group_warning(update)
        return
    start_t = datetime.now().timestamp()
    msg = await update.message.reply_text("🏓 Pong!")
    end_t = datetime.now().timestamp()
    ms = round((end_t - start_t) * 1000)
    await msg.edit_text(f"🏓 *Pong!*\n⚡ `{ms}ms`", parse_mode="Markdown")


async def id_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update):
        await send_group_warning(update)
        return
    user = update.effective_user
    await update.message.reply_text(
        f"👤 *Your Info*\n\n"
        f"• ID: `{user.id}`\n"
        f"• Name: {user.full_name}\n"
        f"• Username: @{user.username or 'N/A'}",
        parse_mode="Markdown"
    )


# =================== SUDO COMMANDS ===================

async def addsudo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update):
        await update.message.reply_text("❌ *Only owner can add sudoers*", parse_mode="Markdown")
        return
    if not context.args:
        await update.message.reply_text("❌ Usage: `/addsudo [user_id]`", parse_mode="Markdown")
        return
    try:
        user_id = int(context.args[0].strip())
    except ValueError:
        await update.message.reply_text("❌ *Invalid user ID!*", parse_mode="Markdown")
        return
    if user_id == OWNER_ID:
        await update.message.reply_text("👑 *He is already owner*", parse_mode="Markdown")
        return
    sudo_users.add(user_id)
    await update.message.reply_text(
        f"✅ *Sudo added!*\nUser ID: `{user_id}`\nTotal sudoers: {len(sudo_users)}",
        parse_mode="Markdown"
    )


async def rmsudo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update):
        await update.message.reply_text("❌ *Only owner can remove sudoers*", parse_mode="Markdown")
        return
    if not context.args:
        await update.message.reply_text("❌ Usage: `/rmsudo [user_id]`", parse_mode="Markdown")
        return
    try:
        user_id = int(context.args[0].strip())
    except ValueError:
        await update.message.reply_text("❌ *Invalid user ID!*", parse_mode="Markdown")
        return
    if user_id not in sudo_users:
        await update.message.reply_text(f"❌ User `{user_id}` is not available in sudolist", parse_mode="Markdown")
        return
    sudo_users.discard(user_id)
    await update.message.reply_text(
        f"✅ *Sudo removed!*\nUser ID: `{user_id}`\nTotal sudoers: {len(sudo_users)}",
        parse_mode="Markdown"
    )


async def sudolist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner_or_sudo(update):
        await update.message.reply_text("❌ *Only owner and sudoers can open this. *", parse_mode="Markdown")
        return
    sudo_list = "\n".join([f"• `{uid}`" for uid in sudo_users]) if sudo_users else "No any sudo users."
    await update.message.reply_text(
        f"👑 *Sudo List*\n\n*Owner:*\n• `{OWNER_ID}`\n\n*Sudo Users:*\n{sudo_list}",
        parse_mode="Markdown"
    )


# =================== SETTIME ===================

async def settime_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global auto_delete_enabled, auto_delete_seconds
    if not is_owner_or_sudo(update):
        await update.message.reply_text("❌ *This command for only owner & sudoers*", parse_mode="Markdown")
        return
    if not context.args:
        status = "✅ ON" if auto_delete_enabled else "❌ OFF"
        await update.message.reply_text(
            f"⏱ *Auto Delete*\nStatus: {status}\nTime: {auto_delete_seconds}s\n\n"
            f"`/settime on` | `/settime off` | `/settime 10`",
            parse_mode="Markdown"
        )
        return
    arg = context.args[0].strip().lower()
    if arg == "on":
        auto_delete_enabled = True
        await update.message.reply_text(f"✅ *Auto delete ON!* ({auto_delete_seconds}s)", parse_mode="Markdown")
    elif arg == "off":
        auto_delete_enabled = False
        await update.message.reply_text("❌ *Auto delete OFF!*", parse_mode="Markdown")
    elif arg.isdigit():
        auto_delete_seconds = int(arg)
        auto_delete_enabled = True
        await update.message.reply_text(f"⏱ *Timer: {auto_delete_seconds}s set!*", parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ Invalid! Use: on / off / number", parse_mode="Markdown")


# =================== MAINTENANCE ===================

async def maintenance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global maintenance_mode
    if not is_owner_or_sudo(update):
        await update.message.reply_text("❌ *Only owner & sudoers can use it. *", parse_mode="Markdown")
        return
    if not context.args:
        status = "✅ ON" if maintenance_mode else "❌ OFF"
        await update.message.reply_text(f"🔧 *Maintenance Mode:* {status}", parse_mode="Markdown")
        return
    arg = context.args[0].strip().lower()
    if arg == "on":
        maintenance_mode = True
        await update.message.reply_text("🔧 *Maintenance mode ON!*\n Only Owner & Sudoers can use this command.", parse_mode="Markdown")
    elif arg == "off":
        maintenance_mode = False
        await update.message.reply_text("✅ *Maintenance mode OFF!*\nBot is working now.", parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ Use: `/maintenance on` / `/maintenance off`", parse_mode="Markdown")


# =================== STATS ===================

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner_or_sudo(update):
        await update.message.reply_text("❌ *Only owner / sudoers can use it!*", parse_mode="Markdown")
        return
    await update.message.reply_text(
        f"📊 *Bot Stats*\n\n"
        f"🕐 Since: {stats['start_time']}\n\n"
        f"• `/num` used: {stats['num']} times\n"
        f"• `/vehicle` used: {stats['vehicle']} times\n"
        f"• `/ff` used: {stats['ff']} times\n"
        f"• `/ab` used: {stats['ab']} times\n"
        f"• `/bc` used: {stats['bc']} times\n"
        f"• `/cd` used: {stats['cd']} times\n\n"
        f"📌 *Total commands:* {stats['total']}",
        parse_mode="Markdown"
    )


# =================== BROADCAST ===================

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update):
        await update.message.reply_text("❌ *Only Owner can do broadcast*", parse_mode="Markdown")
        return
    if not context.args:
        await update.message.reply_text("❌ Usage: `/broadcast [message]`", parse_mode="Markdown")
        return
    msg = " ".join(context.args)
    broadcast_msg = f"📢 *Announcement*\n\n{msg}\n\n— _Bot Owner_"
    await context.bot.send_message(
        chat_id=ALLOWED_GROUP_ID,
        text=broadcast_msg,
        parse_mode="Markdown"
    )
    await update.message.reply_text("✅ *Broadcasting done*", parse_mode="Markdown")


# =================== RATE LIMIT SET ===================

async def setrl_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global rate_limit_seconds
    if not is_owner_or_sudo(update):
        await update.message.reply_text("❌ *Only onwer / sudoers can use it!*", parse_mode="Markdown")
        return
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text(
            f"⚡ *Rate Limit:* {rate_limit_seconds}s\nUsage: `/setrl 5`",
            parse_mode="Markdown"
        )
        return
    rate_limit_seconds = int(context.args[0])
    await update.message.reply_text(f"✅ *Rate limit: {rate_limit_seconds}s set!*", parse_mode="Markdown")


# =================== HANDLE COMMAND HELPER ===================

async def handle_command(update: Update, label: str, emoji: str, api_url: str, api_key: str, value: str, stat_key: str):
    global maintenance_mode

    user_id = update.effective_user.id

    # Maintenance check
    if maintenance_mode and not is_owner_or_sudo(update):
        msg = await update.message.reply_text("🔧 *Bot in maintenance on this time , pls try again letter!*", parse_mode="Markdown")
        asyncio.create_task(auto_delete_msg(msg, 10))
        try:
            await update.message.delete()
        except Exception:
            pass
        return

    # Rate limit check
    wait = check_rate_limit(user_id)
    if wait > 0:
        msg = await update.message.reply_text(
            f"⏳ *Wait! for* `{wait}` seconds. Then try.",
            parse_mode="Markdown"
        )
        asyncio.create_task(auto_delete_msg(msg, wait + 1))
        try:
            await update.message.delete()
        except Exception:
            pass
        return

    # Stats update
    stats[stat_key] += 1
    stats["total"] += 1

    try:
        await update.message.delete()
    except Exception:
        pass

    searching = await update.effective_chat.send_message(
        f"🔍 Searching `{value}`...", parse_mode="Markdown"
    )

    # api_key ko URL mein query param ke roop mein lagao
    if api_key:
        full_url = f"{api_url}{value}&key={api_key}"
    else:
        full_url = f"{api_url}{value}"
    data = call_api(full_url)
    now_time = datetime.now().strftime("%I:%M %p")
    powered = f"\n⚡ _Powered by_ [Mister Stark](https://t.me/carelessxowner)"
    delete_notice = f"\n🗑 _Remove in {auto_delete_seconds}s_ | 🕐 {now_time}" if auto_delete_enabled else f"\n🕐 {now_time}"
    delete_notice += powered
    result_text = f"{emoji} *{label} — {value}*\n\n{format_response(data)}{delete_notice}"

    try:
        await searching.delete()
    except Exception:
        pass

    result_msg = await update.effective_chat.send_message(result_text, parse_mode="Markdown", disable_web_page_preview=True)

    if auto_delete_enabled:
        asyncio.create_task(auto_delete_msg(result_msg, auto_delete_seconds))


# =================== INFO COMMANDS ===================

async def num_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update):
        await send_group_warning(update)
        return
    if not context.args:
        await update.message.reply_text("❌ Usage: `/num [number]`", parse_mode="Markdown")
        return
    await handle_command(update, "Number Info", "📱", NUM_API_URL, NUM_API_KEY, context.args[0].strip(), "num")


async def vehicle_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update):
        await send_group_warning(update)
        return
    if not context.args:
        await update.message.reply_text("❌ Usage: `/vehicle [RC Number]`", parse_mode="Markdown")
        return
    await handle_command(update, "Vehicle Info", "🚗", VEHICLE_API_URL, VEHICLE_API_KEY, context.args[0].strip().upper(), "vehicle")


async def ff_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update):
        await send_group_warning(update)
        return
    if not context.args:
        await update.message.reply_text("❌ Usage: `/ff [UID]`", parse_mode="Markdown")
        return
    await handle_command(update, "Free Fire Player", "🎮", FF_API_URL, FF_API_KEY, context.args[0].strip(), "ff")


async def ab_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update):
        await send_group_warning(update)
        return
    if not context.args:
        await update.message.reply_text("❌ Usage: `/a [value]`", parse_mode="Markdown")
        return
    await handle_command(update, "AB Info", "🔎", AB_API_URL, AB_API_KEY, context.args[0].strip(), "ab")


async def bc_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update):
        await send_group_warning(update)
        return
    if not context.args:
        await update.message.reply_text("❌ Usage: `/tg [value]`", parse_mode="Markdown")
        return
    await handle_command(update, "BC Info", "🔎", BC_API_URL, BC_API_KEY, context.args[0].strip(), "bc")


async def cd_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update):
        await send_group_warning(update)
        return
    if not context.args:
        await update.message.reply_text("❌ Usage: `/rc [value]`", parse_mode="Markdown")
        return
    await handle_command(update, "CD Info", "🔎", CD_API_URL, CD_API_KEY, context.args[0].strip(), "cd")




async def pan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update):
        await send_group_warning(update)
        return
    if not context.args:
        await update.message.reply_text("❌ Usage: `/pan [value]`", parse_mode="Markdown")
        return
    await handle_command(update, "PAN Info", "🔎", PAN_API_URL, PAN_API_KEY, context.args[0].strip(), "pan")


async def pok_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update):
        await send_group_warning(update)
        return
    if not context.args:
        await update.message.reply_text("❌ Usage: `/pok [value]`", parse_mode="Markdown")
        return
    await handle_command(update, "POK Info", "🔎", POK_API_URL, POK_API_KEY, context.args[0].strip(), "pok")


async def ak_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update):
        await send_group_warning(update)
        return
    if not context.args:
        await update.message.reply_text("❌ Usage: `/ak [value]`", parse_mode="Markdown")
        return
    await handle_command(update, "AK Info", "🔎", AK_API_URL, AK_API_KEY, context.args[0].strip(), "ak")


# =================== GROUP APPROVAL (OWNER ONLY) ===================

async def addgc_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update):
        await update.message.reply_text("❌ *Only owner can approve groups!*", parse_mode="Markdown")
        return
    if not context.args:
        await update.message.reply_text("❌ Usage: `/addgc [group_id]`", parse_mode="Markdown")
        return
    try:
        group_id = int(context.args[0].strip())
    except ValueError:
        await update.message.reply_text("❌ *Invalid group ID!*", parse_mode="Markdown")
        return
    approved_groups.add(group_id)
    await update.message.reply_text(
        f"✅ *Group Approved!*\n\nGroup ID: `{group_id}`\nTotal approved: {len(approved_groups)}",
        parse_mode="Markdown"
    )


async def rmgc_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update):
        await update.message.reply_text("❌ *Only owner can remove groups!*", parse_mode="Markdown")
        return
    if not context.args:
        await update.message.reply_text("❌ Usage: `/rmgc [group_id]`", parse_mode="Markdown")
        return
    try:
        group_id = int(context.args[0].strip())
    except ValueError:
        await update.message.reply_text("❌ *Invalid group ID!*", parse_mode="Markdown")
        return
    if group_id not in approved_groups:
        await update.message.reply_text(f"❌ Group `{group_id}` is not in approved list!", parse_mode="Markdown")
        return
    approved_groups.discard(group_id)
    await update.message.reply_text(
        f"✅ *Group Removed!*\n\nGroup ID: `{group_id}`\nTotal approved: {len(approved_groups)}",
        parse_mode="Markdown"
    )


async def gclist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update):
        await update.message.reply_text("❌ *Only owner can view this!*", parse_mode="Markdown")
        return
    if not approved_groups:
        await update.message.reply_text("📋 *No approved groups yet.*", parse_mode="Markdown")
        return
    gc_list = "\n".join([f"• `{gid}`" for gid in approved_groups])
    await update.message.reply_text(
        f"📋 *Approved Groups*\n\n{gc_list}\n\nTotal: {len(approved_groups)}",
        parse_mode="Markdown"
    )


# =================== MAIN ===================

if __name__ == "__main__":
    from telegram.ext import CallbackQueryHandler

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(help_callback, pattern="^help"))
    app.add_handler(CommandHandler("ping", ping_command))
    app.add_handler(CommandHandler("id", id_command))
    app.add_handler(CommandHandler("settime", settime_command))
    app.add_handler(CommandHandler("maintenance", maintenance_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("broadcast", broadcast_command))
    app.add_handler(CommandHandler("setrl", setrl_command))
    app.add_handler(CommandHandler("addgc", addgc_command))
    app.add_handler(CommandHandler("rmgc", rmgc_command))
    app.add_handler(CommandHandler("gclist", gclist_command))
    app.add_handler(CommandHandler("addsudo", addsudo_command))
    app.add_handler(CommandHandler("rmsudo", rmsudo_command))
    app.add_handler(CommandHandler("sudolist", sudolist_command))
    app.add_handler(CommandHandler("num", num_command))
    app.add_handler(CommandHandler("vehicle", vehicle_command))
    app.add_handler(CommandHandler("ff", ff_command))
    app.add_handler(CommandHandler("a", ab_command))
    app.add_handler(CommandHandler("tg", bc_command))
    app.add_handler(CommandHandler("rc", cd_command))
    app.add_handler(CommandHandler("pan", pan_command))
    app.add_handler(CommandHandler("pok", pok_command))
    app.add_handler(CommandHandler("ak", ak_command))

    print("✅ Bot is running...")
    app.run_polling()
