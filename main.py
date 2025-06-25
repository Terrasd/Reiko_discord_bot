import os
import datetime

import discord
from discord import app_commands
from discord.ext import tasks, commands
from dotenv import load_dotenv

from functions.get_memes_reddit import get_random_meme_url
# from functions.nickname_animation import NicknameAnimator
from functions.subreddits import LIST_SUBREDDITS


load_dotenv()

has_sent_today = False

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
    if message.author == client.user:
        return

    await client.process_commands(message)


@client.tree.command(name='post', description='Отправить пост из сабреддита')
@app_commands.describe(subreddit='Выберите сабреддит')
async def post(interaction: discord.Interaction, subreddit: str):
    '''Команда для отправки случайного поста по указанному сабреддиту.'''
    meme_title, meme_url, subred_name, post_link = (
        await get_random_meme_url(subreddit))

    if meme_url:
        embed = discord.Embed(
            title=meme_title,
            color=discord.Color.blue()
        )
        embed.set_image(url=meme_url)
        embed.description = f'[Open on Reddit]({post_link})'
        embed.set_footer(text=f'From r/{subred_name}')

        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message(
            f'Не удалось получить пост из {subreddit},'
            f' прошу прощения ･ﾟ･(｡>ω<｡)･ﾟ･')


@post.autocomplete('subreddit')
async def subred_autocomplete(interaction: discord.Interaction, current: str):
    matches = [s for s in LIST_SUBREDDITS if current.lower() in s.lower()]
    return [
        app_commands.Choice(name=s, value=s)
        for s in matches[:25]
    ]


@tasks.loop(seconds=30)
async def send_random_meme():
    '''Задача для отправки случайного поста из случайного сабреддита.'''
    global has_sent_today
    nowtime = str(datetime.datetime.now().time().strftime('%H.%M'))
    if nowtime == '00.00' and not has_sent_today:
        channel = client.get_channel(int(os.getenv('CHANNEL_ID')))
        meme_title, meme_url, subred_name, post_link = (
            await get_random_meme_url()
        )

        if channel and meme_url:
            embed = discord.Embed(
                title=meme_title,
                color=discord.Color.green()
            )
            embed.description = f'[Open on Reddit]({post_link})'
            embed.set_footer(text=f'From r/{subred_name}')

            await channel.send(embed=embed)
        else:
            print('Не удалось отправить случайный пост')

        has_sent_today = True

    elif nowtime != '00.00' and has_sent_today:
        has_sent_today = False


if __name__ == '__main__':
    client.run(os.getenv('TOKEN'))
