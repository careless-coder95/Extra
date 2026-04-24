from pyrogram import Client, filters
import aiohttp

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#           ᴄᴏɴꜰɪɢᴜʀᴀᴛɪᴏɴ
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

API_ID = 0               # APELEYE.ORG SE LO
API_HASH = ""            # APELEYE.ORG SE LO
STRING_SESSION = ""      # NEECHE WALA SCRIPT CHALA KE LO

NUM_API_URL = ""         # PHONE NUMBER API URL (no key needed)
TG_API_URL = "https://stark-free-osint-api.vercel.app/info?type=tg&tg_id="
TG_API_KEY = ""          # TG API KEY

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

app = Client("userbot", session_string=STRING_SESSION, api_id=API_ID, api_hash=API_HASH)

REMOVE_KEYS = {
    "branding", "developer", "processed_by",
    "owner_contact", "api_owner", "credit",
    "credits", "powered_by", "made_by",
    "api_used", "api_name"
}

𝗙𝗢𝗡𝗧_𝗕𝗢𝗟𝗗 = str.maketrans(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",
    "𝗔𝗕𝗖𝗗𝗘𝗙𝗚𝗛𝗜𝗝𝗞𝗟𝗠𝗡𝗢𝗣𝗤𝗥𝗦𝗧𝗨𝗩𝗪𝗫𝗬𝗭𝗮𝗯𝗰𝗱𝗲𝗳𝗴𝗵𝗶𝗷𝗸𝗹𝗺𝗻𝗼𝗽𝗾𝗿𝘀𝘁𝘂𝘃𝘄𝘅𝘆𝘇𝟬𝟭𝟮𝟯𝟰𝟱𝟲𝟳𝟴𝟵"
)

def stylish(text):
    return text.translate(𝗙𝗢𝗡𝗧_𝗕𝗢𝗟𝗗)


def remove_branding(data):
    if isinstance(data, dict):
        return {k: remove_branding(v) for k, v in data.items() if k.lower() not in REMOVE_KEYS}
    elif isinstance(data, list):
        return [remove_branding(i) for i in data]
    return data


def format_response(data, indent=0):
    lines = []
    prefix = "  " * indent
    if isinstance(data, dict):
        for k, v in data.items():
            key_styled = stylish(str(k).upper())
            if isinstance(v, (dict, list)):
                lines.append(f"{prefix}❐ {key_styled}")
                lines.append(format_response(v, indent + 1))
            else:
                lines.append(f"{prefix}• {key_styled} : {v}")
    elif isinstance(data, list):
        for item in data:
            lines.append(format_response(item, indent))
    else:
        lines.append(f"{prefix}{data}")
    return "\n".join(lines)


async def call_api(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    return None
    except Exception:
        return None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#           .ɴᴜᴍ ᴄᴏᴍᴍᴀɴᴅ
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.on_message(filters.me & filters.command("num", prefixes="."))
async def num_command(client, message):
    args = message.text.split(None, 1)

    if len(args) < 2 or not args[1].strip():
        await message.edit("**ᴜꜱᴀɢᴇ:** `.num {number}`")
        return

    number = args[1].strip()
    await message.edit(f"🔎 **ꜱᴇᴀʀᴄʜɪɴɢ...** `{number}`")

    url = f"{NUM_API_URL}{number}"
    data = await call_api(url)

    if not data:
        await message.edit("❌ **ɴᴏ ʀᴇꜱᴜʟᴛ ꜰᴏᴜɴᴅ**")
        return

    clean = remove_branding(data)
    result = format_response(clean)

    text = (
        f"📱 **ɴᴜᴍʙᴇʀ ɪɴꜰᴏ**\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"{result}\n"
        f"━━━━━━━━━━━━━━━━━"
    )
    await message.edit(text)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#           .ᴛɢ ᴄᴏᴍᴍᴀɴᴅ
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.on_message(filters.me & filters.command("tg", prefixes="."))
async def tg_command(client, message):
    user_id = None

    # Reply se auto detect
    if message.reply_to_message:
        replied = message.reply_to_message
        if replied.from_user:
            user_id = replied.from_user.id
        elif replied.sender_chat:
            user_id = replied.sender_chat.id

    # Without reply — .tg {userid}
    else:
        args = message.text.split(None, 1)
        if len(args) < 2 or not args[1].strip():
            await message.edit("**ᴜꜱᴀɢᴇ:** `.tg {userid}` ʏᴀ ᴋɪꜱɪ ᴍᴇꜱꜱᴀɢᴇ ᴋᴏ ʀᴇᴘʟʏ ᴋᴀʀᴋᴇ `.tg`")
            return
        user_id = args[1].strip()

    await message.edit(f"🔎 **ꜱᴇᴀʀᴄʜɪɴɢ...** `{user_id}`")

    url = f"{TG_API_URL}{user_id}&key={TG_API_KEY}"
    data = await call_api(url)

    if not data:
        await message.edit("❌ **ɴᴏ ʀᴇꜱᴜʟᴛ ꜰᴏᴜɴᴅ**")
        return

    clean = remove_branding(data)
    result = format_response(clean)

    text = (
        f"👤 **ᴛᴇʟᴇɢʀᴀᴍ ɪɴꜰᴏ**\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"{result}\n"
        f"━━━━━━━━━━━━━━━━━"
    )
    await message.edit(text)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

print("ᴜꜱᴇʀʙᴏᴛ ꜱᴛᴀʀᴛɪɴɢ...")
app.run()
