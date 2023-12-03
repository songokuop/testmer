# (c) @AbirHasan2005

from config import Config
from helpers.database.database import db
from pyrogram import Client
from pyrogram.types import Message


async def AddUserToDatabase(c: Client, cmd: Message):
    if not await db.isuser_exist(cmd.from_user.id):
        await db.addUser(cmd.from_user.id)
        if Config.LOG_CHANNEL is not None:
            await c.send_message(
                int(Config.LOG_CHANNEL),
                f"#NEW_USER: \n\nNew User [{cmd.from_user.first_name}](tg://user?id={cmd.from_user.id}) started @{(await c.get_me()).username} !!"
            )
