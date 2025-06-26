import os
import random

import asyncpraw
import aiohttp
from pathlib import Path
from dotenv import load_dotenv

from .random_subreddits import choose_subreddit


load_dotenv()


MEME_DIR = Path('memes')
MEME_DIR.mkdir(exist_ok=True)


def read_from_file(subreddit_name):
    file_path = MEME_DIR / f'{subreddit_name}.txt'
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return [line.strip() for line in file.readlines()]
    return []


def save_to_file(sent_meme, subreddit_name, max_lines=30):
    file_path = MEME_DIR / f'{subreddit_name}.txt'

    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            lines = file.readlines()
    else:
        lines = []

    if len(lines) >= max_lines:
        lines.pop(0)

    lines.append(sent_meme + '\n')

    with open(file_path, 'w') as file:
        file.writelines(lines)


def get_reddit_instance(session):
    return asyncpraw.Reddit(
        client_id=os.getenv('REDDIT_CLIENT_ID'),
        client_secret=os.getenv('REDDIT_SECRET'),
        user_agent=os.getenv('REDDIT_USER_AGENT'),
        requestor_kwargs={'session': session}
    )


async def get_random_meme_url(subreddit=None):
    if not subreddit:
        subreddit = choose_subreddit()

    sent_memes = read_from_file(subreddit)

    async with aiohttp.ClientSession() as session:
        reddit = get_reddit_instance(session)
        subreddit_obj = await reddit.subreddit(subreddit)

        top_posts = []
        async for post in subreddit_obj.hot(limit=30):
            if post.url.endswith(('jpg', 'jpeg', 'png', 'gif', 'mp4', 'webm')):
                top_posts.append(post)

        available_posts = [
            post for post in top_posts if post.permalink not in sent_memes]

        if available_posts:
            post = random.choice(available_posts)
            save_to_file(post.permalink, subreddit)
            return (
                post.title,
                post.url,
                subreddit_obj.display_name,
                f'https://reddit.com{post.permalink}'
            )
        else:
            return None, None
