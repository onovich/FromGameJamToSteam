from collections import Counter
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
import re

from collect import NAMES


class Audit(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.cards = []
        self.images = []
        self.steam_links = []
        self.headings = Counter()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.append(attrs['id'])
            if re.fullmatch(r'game-\d{3}', attrs['id']):
                self.cards.append(attrs['id'])
        if tag == 'img':
            self.images.append(attrs.get('src', ''))
        if tag == 'a' and attrs.get('href', '').startswith('https://store.steampowered.com/app/'):
            self.steam_links.append(attrs['href'])
        if tag in ('h1', 'h2', 'h3'):
            self.headings[tag] += 1


path = Path('outputs/game-jam-to-steam-100.html')
data = path.read_text(encoding='utf-8')
audit = Audit()
audit.feed(data)
assert not path.read_bytes().startswith(b'\xef\xbb\xbf')
assert len(audit.ids) == len(set(audit.ids))
assert audit.cards == [f'game-{i:03d}' for i in range(1, 101)]
assert len(audit.images) == 99 and all(x.startswith('https://') for x in audit.images)
assert len(audit.steam_links) == len(set(audit.steam_links)) == 99
assert audit.headings == {'h1': 1, 'h2': 2, 'h3': 100}
assert data.count('class="game-row"') == 100
assert '<a class="brand" href="#top">游戏观察</a>' in data
assert '数据来源：</span><a href="https://gmtk.substack.com/' in data
assert 'data-category-filter="" aria-pressed="true"' in data
assert 'onovich1110' not in data and 'gamemakerstoolkit@' not in data
assert 'C:\\Users\\' not in data
assert all(name in unescape(data) for name in NAMES)
assert '70 已发售' in data and '29 未发售' in data and '1 待核实' in data
assert '<meta name="robots" content="index,follow,max-image-preview:large">' in data
assert '<link rel="canonical" href="https://jam-to-steam.onovich.com/">' in data
assert 'noindex' not in data
print('PASS: 100 cards, 99 unique Steam links and covers, headings, IDs, UTF-8, privacy')
