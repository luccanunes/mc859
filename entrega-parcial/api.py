import requests
import random
import time

def get_random_game_sample(qty=10, seed=42):
    """
    Retorna uma amostra aleatória de jogos da Steam no formato (appid, name)
    Usa uma seed fixa para permitir replicabilidade.
    """
    url = 'https://api.steampowered.com/ISteamApps/GetAppList/v2/'
    resp = requests.get(url)
    apps = resp.json()['applist']['apps']
    games = [app for app in apps if app['name']]
    rng = random.Random(seed)
    return rng.sample([(g['appid'], g['name']) for g in games], qty)

def get_game_by_id(game_id):
    url = f'https://store.steampowered.com/api/appdetails?appids={game_id}'
    resp = requests.get(url)
    data = resp.json().get(str(game_id), {})
    if 'data' in data:
        return data['data']
    else:
        return None

def get_game_reviews(game_id, num_pages=2, per_page=100):
    cursor = '*'
    reviews = {}
    for _ in range(num_pages):
        url = (
            f"https://store.steampowered.com/appreviews/{game_id}"
            f"?json=1&num_per_page={per_page}&cursor={cursor}&purchase_type=all&language=all"
        )
        resp = requests.get(url)
        if resp.status_code != 200:
            break
        data = resp.json()
        for rev in data.get('reviews', []):
            voted_up = rev['voted_up']
            steamid = rev['author']['steamid']
            weighted_vote_score = rev.get('weighted_vote_score', 0)
            reviews[steamid] = (voted_up, weighted_vote_score)
        cursor = data.get('cursor')
        if not data.get('reviews'):
            break
        time.sleep(.5)
    return reviews