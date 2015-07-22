from datetime import datetime
from bs4 import BeautifulSoup
import requests

TIERS_UPDATED = None
TIERS = {}


def get_hots_tier_list(bot):
    global TIERS, TIERS_UPDATED
    now = datetime.now()

    if TIERS and TIERS_UPDATED and \
            (now - TIERS_UPDATED).total_seconds() < 3600:
        print('using cached list')
        return TIERS
    url = 'https://www.hotslogs.com/Sitewide/HeroAndMapStatistics'

    response = requests.get(url)
    if not response.status_code == 200:
        bot.send_message(
            'Unable to get info from hotslogs: response '
            'code {}'.format(response.status_code))
        return None
    soup = BeautifulSoup(response.text, 'html5lib')
    tags = soup.find(
        'div', id='RadGridCharacterStatistics').find_all('tr')
    headers = [x.text.lower().replace(' ', '-') 
               for x in tags[0].find_all('th')][1:]
    tier_1 = []
    tier_2 = []
    tier_3 = []
    tier_4 = []
    tier_5 = []
    tier_none = []
    for tag in tags:
        columns = [x.text.strip() for x in tag.find_all('td')][1:]
        zipped = {h: v for h, v in zip(headers, columns)}
        if not zipped:
            continue
        zipped['games-played'] = int(zipped.get('games-played', '0'))
        zipped['win-percent'] = float(
            zipped.get('win-percent', '0').strip('%'))
        zipped['popularity'] = float(
            zipped.get('popularity', '0').strip('%'))

        win_pct = zipped.get('win-percent')
        if zipped.get('games-played', 0) < 3000:
            tier_none.append(zipped)
            print(tier_none)
        elif win_pct >= 52:
            tier_1.append(zipped)
        elif win_pct >= 50 and win_pct < 52:
            tier_2.append(zipped)
        elif win_pct >= 45 and win_pct < 50:
            tier_3.append(zipped)
        elif win_pct >= 40 and win_pct < 45:
            tier_4.append(zipped)
        elif win_pct <= 40:
            tier_5.append(zipped)
    tiers = {
        1: tier_1,
        2: tier_2,
        3: tier_3,
        4: tier_4,
        5: tier_5,
        None: tier_none,
    }

    TIERS = tiers
    TIERS_UPDATED = now
    return tiers
