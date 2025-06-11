import requests
import requests.auth
from datetime import datetime, timezone
import csv
import os
import html

def obtener_token():
    with open('password.txt', 'r') as f:
        password = f.read()
    with open('user.txt', 'r') as f:
        user = f.read().strip()
    with open('client_id.txt', 'r') as f:
        client_id = f.read().strip()
    with open('client_secret.txt', 'r') as f:
        client_secret = f.read().strip()

    client_auth = requests.auth.HTTPBasicAuth(client_id, client_secret)
    post_data = {
        'grant_type': 'password',
        'username': user,
        'password': password
    }
    headers = {'User-Agent': 'datosPostsTFM/0.1'}

    response = requests.post(
        'https://www.reddit.com/api/v1/access_token',
        auth=client_auth,
        data=post_data,
        headers=headers
    )
    token = response.json()['access_token']
    return token

def generar_peticion(token, url):
    headers = {
        "Authorization": f"bearer {token}",
        "User-Agent": "datosPostsTFM/0.1"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 401:
        token = obtener_token()
        return generar_peticion(token, url)
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

def obtener_subreddits(token, query):
    url = f"https://oauth.reddit.com/subreddits/search?q={query}&sort=activity&limit=100"
    resultado = generar_peticion(token, url)
    lista_subreddits = resultado['data']['children']
    for subreddit in lista_subreddits:
        nombre_subreddit = subreddit['data']['display_name']
        subscriber_count = subreddit['data']['subscribers']
        created_date = datetime.fromtimestamp(subreddit['data']['created_utc']).strftime('%Y-%m-%d %H:%M:%S')
        print(f"Subreddit: {nombre_subreddit}, Subscribers: {subscriber_count}, Created: {created_date}")
    
def obtener_posts_2025(token, subreddit, points):
    base_url = f"https://oauth.reddit.com/r/{subreddit}/new?limit=100"
    posts_2025 = []
    after = None
    count = 0

    while True:
        url = base_url + (f"&after={after}" if after else "")
        resultado = generar_peticion(token, url)

        if 'data' not in resultado or 'children' not in resultado['data']:
            break 

        posts = resultado['data']['children']

        for post in posts:
            timestamp = post['data']['created_utc']
            año = datetime.fromtimestamp(timestamp, tz=timezone.utc).year
            if año == 2025 and post['data']['score'] >= points:
                posts_2025.append(post)

        after = resultado['data'].get('after')
        if not after:
            break

    return posts_2025

def obtener_posts_2025_texto(token, subreddit, query):
    base_url = f"https://oauth.reddit.com/r/{subreddit}/search?limit=100&sort=new&q={query}"
    posts_2025 = []
    after = None
    count = 0

    while True:
        url = base_url + (f"&after={after}" if after else "")
        resultado = generar_peticion(token, url)

        if 'data' not in resultado or 'children' not in resultado['data']:
            break 

        posts = resultado['data']['children']

        for post in posts:
            timestamp = post['data']['created_utc']
            año = datetime.fromtimestamp(timestamp, tz=timezone.utc).year
            if año == 2025 and post['data']['num_comments'] > 1:
                posts_2025.append(post)

        after = resultado['data'].get('after')
        if not after:
            break

    return posts_2025

def guardar_posts_csv(posts, archivo_csv):
    os.makedirs(os.path.dirname(archivo_csv), exist_ok=True)
    posts.reverse()
    campos = ["score", "created_utc", "title", "selftext"]

    with open(archivo_csv, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=campos, quoting=csv.QUOTE_NONNUMERIC)

        for post in posts:
            data = post["data"]
            fecha = datetime.fromtimestamp(data["created_utc"], tz=timezone.utc).strftime("%Y-%m-%d")

            writer.writerow({
                "score": data.get("score", 0),
                "created_utc": fecha,
                "title": html.unescape(data.get("title", "")),
                "selftext": html.unescape(data.get("selftext", ""))
            })

token = obtener_token()
subreddit = "politics"
#obtener_subreddits(token, query)
#posts = obtener_posts_2025(token,subreddit, 141)
posts = obtener_posts_2025_texto(token,subreddit, "title:\"Elon Musk\" timestamp:1735689600..1738291200")
print(len(posts))
guardar_posts_csv(posts, r"output_files\\posts_politics.csv")

