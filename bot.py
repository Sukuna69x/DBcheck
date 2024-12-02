import re
import os
import pymongo
import urllib

from pyrogram import Client, filters
from pyrogram.types import Message

# Get environment variables
api_id = os.getenv("API_ID", "21406615")
api_hash = os.getenv("API_HASH", "d66b1900ea3a7438ee22dd389085949a")
bot_token = os.getenv("BOT_TOKEN", "7849431555:AAHeOZvMvmssK5tTu6TfYdpxWH9kIyE4ebU")

bot = Client(
    session_name=":memory:",
    api_id=int(api_id),
    api_hash=api_hash,
    bot_token=bot_token
)


@bot.on_message(filters.command("start"))
async def _start(_, msg: Message):
    START = """
**Hii {}**, `I am MongoDB Url Checker Bot, Just Send me your MongoDB Url I will tell you if your Url has any issues connecting or not.`

__Made with ❤ by [Krishna](https://t.me/Krishna_Singhal)__.
"""
    await msg.reply(START.format(msg.from_user.mention), disable_web_page_preview=True)


@bot.on_message(filters.private & filters.text & ~filters.command(["start", "check"]))
async def _private_filter(_, msg: Message):
    url = msg.text
    await check_url(msg, url)
    await msg.delete()  # For Security


@bot.on_message(filters.command("check"))
async def _check(_, msg: Message):
    if len(msg.command) > 1:
        url = msg.command[1]
    else:
        return await msg.reply("`URL not Found!`")
    await check_url(msg, url)
    try:
        await msg.delete()  # Will work also in group so Pass chat admin Exception.
    except Exception as e:
        await msg.reply(f"`I can't delete this URL myself, any admin delete this for security.` Error: {str(e)}")


async def check_url(msg: Message, url: str):
    PATTERN = r"^mongodb((?:\+srv))?:\/\/(.*):(.*)@[a-z0-9]+\.(.*)\.mongodb\.net\/(.*)\?retryWrites\=true&w\=majority"
    s_r = re.compile("[@_!#$%^&*()<>?/\|}{~:]")
    match = re.match(PATTERN, url)
    if not match:
        return await msg.reply(f"**Invalid MongoDB Url**: `{url}`")
    try:
        pymongo.MongoClient(url)
    except Exception as e:
        if "Username and password must be escaped" in str(e):
            if bool(match.group(1)):
                raw_url = "mongodb+srv://{}:{}@cluster0.{}.mongodb.net/{}?retryWrites=true&w=majority"
            else:
                raw_url = "mongodb://{}:{}@cluster0.{}.mongodb.net/{}?retryWrites=true&w=majority"
            username, password, key, dbname = match.group(2), match.group(3), match.group(4), match.group(5)
            if s_r.search(username):
                username = urllib.parse.quote_plus(username)
            if s_r.search(password):
                password = urllib.parse.quote_plus(password)
            if '<' in dbname or '>' in dbname:
                dbname = "Userge"
            new_url = raw_url.format(username, password, key, dbname)
            await msg.reply(
                "`Your URL has an invalid username and password.`\n\n"
                "`I quoted your username and password and created a new DB_URI, "
                f"Use this to connect to MongoDB.`\n\n`{new_url}`"
            )
    else:
        if '<' in match.group(5) or '>' in match.group(5):
            dbname = "Userge"
            new_url = url.replace(match.group(5), dbname)
            return await msg.reply(f"`You forgot to remove '<' and '>' signs.`\n\n**Use this URL:** `{new_url}`")
        await msg.reply("`This URL is ERROR Free. You can use this to connect to MongoDB.`")


if __name__ == "__main__":
    bot.run()
            
