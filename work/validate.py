"""Validate the bilingual snapshot before publishing."""

from collections import Counter
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
import re

from collect import NAMES
from i18n import SITE_URL, TEXT


ROOT = Path(__file__).resolve().parent.parent


class Audit(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.cards = []
        self.images = []
        self.steam_links = []
        self.headings = Counter()
        self.html_lang = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'html':
            self.html_lang = attrs.get('lang')
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


for filename, locale, canonical, landing in (
    ('outputs/index.html', 'zh-CN', f'{SITE_URL}zh/', True),
    ('outputs/game-jam-to-steam-100.html', 'zh-CN', f'{SITE_URL}zh/', True),
    ('outputs/zh/index.html', 'zh-CN', f'{SITE_URL}zh/', False),
    ('outputs/en/index.html', 'en', f'{SITE_URL}en/', False),
):
    path = ROOT / filename
    data = path.read_text(encoding='utf-8')
    audit = Audit()
    audit.feed(data)
    assert not path.read_bytes().startswith(b'\xef\xbb\xbf'), filename
    assert audit.html_lang == locale, filename
    assert len(audit.ids) == len(set(audit.ids)), filename
    assert audit.cards == [f'game-{i:03d}' for i in range(1, 101)], filename
    assert len(audit.images) == 99 and all(x.startswith('https://') for x in audit.images), filename
    assert len(audit.steam_links) == len(set(audit.steam_links)) == 99, filename
    assert audit.headings == {'h1': 1, 'h2': 2, 'h3': 100}, filename
    assert data.count('class="game-row"') == 100, filename
    assert all(name in unescape(data) for name in NAMES), filename
    assert 'onovich1110' not in data and 'gamemakerstoolkit@' not in data, filename
    assert 'C:\\Users\\' not in data and 'noindex' not in data, filename
    assert '<meta name="robots" content="index,follow,max-image-preview:large">' in data, filename
    assert f'<link rel="canonical" href="{canonical}">' in data, filename
    for language, url in (('zh-CN', f'{SITE_URL}zh/'), ('en', f'{SITE_URL}en/'), ('x-default', SITE_URL)):
        assert f'<link rel="alternate" hreflang="{language}" href="{url}">' in data, filename
    assert ('location.replace(' in data) == landing, filename
    assert f'<a class="brand" href="#top">{TEXT[locale]["brand"]}</a>' in data, filename
    assert TEXT[locale]['hero_title'] in data, filename
    assert TEXT[locale]['catalog'] in data, filename
    assert 'href="https://gmtk.substack.com/' in data, filename
    assert 'data-category-filter="" aria-pressed="true"' in data, filename
    assert 'data-lang="zh-CN"' in data and 'data-lang="en"' in data, filename
    for key, number in (('released', 70), ('upcoming', 29), ('unknown', 1)):
        assert f'<strong>{number}</strong><span>{TEXT[locale][key]}</span>' in data, filename
    print(f'PASS {filename}: 100 rows, 99 Steam links, locale {locale}, SEO links')
