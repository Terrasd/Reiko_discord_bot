import json
import random
from pathlib import Path

STATS_FILE = Path('subreddit_stats.json')

SUBREDDITS = ['memes', 'Seaofthieves', 'Warframe', 'forhonor',
              'DeepRockGalactic', 'Eldenring', 'shittydarksouls']


def load_stats():
    '''Загрузка статистики из файла.'''
    if STATS_FILE.exists():
        with open(STATS_FILE, 'r') as file:
            return json.load(file)
    return {sub: 0 for sub in SUBREDDITS}


def save_stats(stats):
    '''Сохранение в файл статистики использования.'''
    with open(STATS_FILE, 'w') as file:
        json.dump(stats, file, indent=4)


def choose_subreddit():
    '''Выбор сабреддита на основе использования.'''
    stats = load_stats()

    max_usage = max(stats.values())
    weights = [max_usage - stats[sub] + 1 for sub in SUBREDDITS]

    chosen_subreddit = random.choices(SUBREDDITS, weights=weights, k=1)[0]

    stats[chosen_subreddit] += 1
    save_stats(stats)

    return chosen_subreddit
