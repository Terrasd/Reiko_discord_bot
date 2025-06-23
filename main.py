import os
import datetime

import discord
from discord import app_commands
from discord.ext import tasks, commands
from dotenv import load_dotenv

from functions.get_memes_reddit import get_random_meme_url
from functions.words import bad_words
from functions.message_handler import handle_message
# from functions.nickname_animation import NicknameAnimator


load_dotenv()


intents = discord.Intents.all()
client = commands.Bot(command_prefix='/', intents=intents)

# nicknames = ['( *｀з´)', '(●´^｀●)', "(ฅ'ω'ฅ)", '(≧◡≦)']
# nickname_animator = NicknameAnimator(
#     client,
#     int(os.getenv('GUILD_ID')),
#     int(os.getenv('MY_USER_ID')),
#     base_nickname='SourceCream',
#     animation_type='sequence',
#     nicknames=nicknames
# )


@client.event
async def on_ready():
    print(f'Бот {client.user} готов к работе!')
    send_random_meme.start()
    # nickname_animator.start()
    await client.tree.sync()


@client.event
async def on_message(message: discord.Message):
    '''Обработка любых сообщений.'''
    try:
        await handle_message(client, message)
    except Exception as e:
        print(f'Произошла ошибка при обработке сообщения: {e}')

    if message.author == client.user:
        return

    if client.user in message.mentions and any(
            word in message.content.lower() for word in bad_words):
        await message.reply('接辺掲玄転述込併士売載投後科前後南', mention_author=False)

    if (isinstance(message.channel, discord.DMChannel) and message.author.id ==
            int(os.getenv('TARGET_USER_ID'))):
        target_channel = client.get_channel(int(os.getenv('CHANNEL_ID')))
        if target_channel:
            await target_channel.send(message.content)
        else:
            print(f'Не могу найти канал с ID {int(os.getenv('CHANNEL_ID'))}')

    await client.process_commands(message)


@client.tree.command(name='meme', description='Отправить пост из сабреддита')
@app_commands.describe(subreddit='Введите сабреддит')
async def meme(interaction: discord.Interaction, subreddit: str):
    '''Команда для отправки случайного поста по указанному сабреддиту.'''
    meme_title, meme_url, subred_name = await get_random_meme_url(subreddit)

    if meme_url:
        embed = discord.Embed(
            title=meme_title,
            url=meme_url,
            color=discord.Color.blue()
        )
        embed.set_image(url=meme_url)
        embed.description = f'*From {subred_name}*'

        await interaction.response.send_message(embed=embed)
        print(
            f'Пост по команде "/meme" из <{subreddit}> отправлен: {meme_url}')
    else:
        await interaction.response.send_message(
            f'Не удалось получить пост из {subreddit},'
            f' прошу прощения ･ﾟ･(｡>ω<｡)･ﾟ･')
        print(f'Ошибка при получении поста из {subreddit}.')


@tasks.loop(seconds=30)
async def send_random_meme():
    '''Задача для отправки случайного поста из случайного сабреддита.'''
    nowtime = str(datetime.datetime.now().time().strftime('%H.%M.%S'))
    if nowtime == '00.00.00':
        channel = client.get_channel(int(os.getenv('CHANNEL_ID')))
        meme_title, meme_url, subred_name = await get_random_meme_url()

        if channel and meme_url:
            embed = discord.Embed(
                title=meme_title,
                url=meme_url,
                color=discord.Color.green()
            )
            embed.set_image(url=meme_url)
            embed.description = f'*From {subred_name}*'

            await channel.send(embed=embed)
            print(f'Случайный пост отправлен: {meme_url}')
        else:
            print('Не удалось отправить случайный пост')


if __name__ == '__main__':
    client.run(os.getenv('TOKEN'))
