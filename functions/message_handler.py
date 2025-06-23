import os
import discord

from dotenv import load_dotenv


load_dotenv()


STICKER_NAME = 'для мемов геры'


async def handle_message(client: discord.Client, message: discord.Message):
    if message.author.id == int(os.getenv('TARGET_USER_ID')):
        if any(attachment.content_type.startswith(('image/', 'video/'))
               for attachment in message.attachments):
            sticker = discord.utils.get(
                message.guild.stickers, name=STICKER_NAME)
            if sticker:
                await message.channel.send(stickers=[sticker])
            else:
                print(
                    f'Стикер с именем "{STICKER_NAME}" не найден на сервере!')
