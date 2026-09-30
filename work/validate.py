"""Validate content, locale metadata, and the exact public Pages artifact."""

from collections import Counter
from html import unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import struct
from xml.etree import ElementTree as ET

from collect import NAMES
from i18n import SITE_URL, TEXT


ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / 'dist'
ALTERNATES = {
    'zh-CN': f'{SITE_URL}zh/',
    'en': f'{SITE_URL}en/',
    'x-default': SITE_URL,
}


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


titles = set()
descriptions = set()
for filename, locale, canonical, is_landing in (
    ('outputs/index.html', 'en', SITE_URL, True),
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
    assert 'C:\\Users\\' not in data and 'noindex' not in data, filename
    assert 'onovich1110' not in data and 'gamemakerstoolkit@' not in data, filename
    assert '<meta name="robots" content="index,follow,max-image-preview:large">' in data, filename
    assert f'<link rel="canonical" href="{canonical}">' in data, filename
    for language, url in ALTERNATES.items():
        assert f'<link rel="alternate" hreflang="{language}" href="{url}">' in data, filename
    assert f'<link rel="icon" type="image/svg+xml" href="{SITE_URL}favicon.svg">' in data, filename
    assert '<meta property="og:site_name" content="游戏观察">' in data, filename
    assert f'<meta property="og:url" content="{canonical}">' in data, filename
    assert f'<meta property="og:image" content="{SITE_URL}social-preview.png">' in data, filename
    assert '<meta name="twitter:card" content="summary_large_image">' in data, filename
    assert 'href="https://gmtk.substack.com/' in data, filename
    title = re.search(r'<title>([^<]+)</title>', data).group(1)
    description = re.search(r'<meta name="description" content="([^"]+)">', data).group(1)
    assert title not in titles and description not in descriptions, filename
    titles.add(title)
    descriptions.add(description)
    schema = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', data).group(1))
    assert schema['url'] == canonical, filename

    if is_landing:
        assert audit.headings == {'h1': 1}, filename
        assert not audit.cards and not audit.steam_links, filename
        assert 'location.replace(' in data, filename
        assert 'href="./zh/"' in data and 'href="./en/"' in data, filename
        assert schema['@type'] == 'WebSite' and schema['name'] == '游戏观察', filename
        assert schema['alternateName'] == 'Game Observatory', filename
    else:
        assert audit.cards == [f'game-{i:03d}' for i in range(1, 101)], filename
        assert len(audit.images) == 99 and all(x.startswith('https://') for x in audit.images), filename
        assert data.count('loading="eager"') == 2 and data.count('loading="lazy"') == 97, filename
        assert data.count('fetchpriority="high"') == 1, filename
        assert len(audit.steam_links) == len(set(audit.steam_links)) == 99, filename
        assert audit.headings == {'h1': 1, 'h2': 2, 'h3': 100}, filename
        assert data.count('class="game-row"') == 100, filename
        assert all(name in unescape(data) for name in NAMES), filename
        assert 'location.replace(' not in data, filename
        assert schema['@type'] == 'CollectionPage' and schema['inLanguage'] == locale, filename
        assert schema['isPartOf']['@id'] == f'{SITE_URL}#website', filename
        assert f'<a class="brand" href="#top">{TEXT[locale]["brand"]}</a>' in data, filename
        assert 'data-category-filter="" aria-pressed="true"' in data, filename
        assert 'data-lang="zh-CN"' in data and 'data-lang="en"' in data, filename
        for key, number in (('released', 70), ('upcoming', 29), ('unknown', 1)):
            assert f'<strong>{number}</strong><span>{TEXT[locale][key]}</span>' in data, filename
    print(f'PASS {filename}: {locale}, canonical, alternate languages, metadata, schema')

assert (ROOT / 'outputs/game-jam-to-steam-100.html').read_bytes() == (ROOT / 'outputs/index.html').read_bytes()

expected_files = {
    'index.html', 'zh/index.html', 'en/index.html',
    'robots.txt', 'sitemap.xml', 'favicon.svg', 'social-preview.png',
}
actual_files = {path.relative_to(DIST).as_posix() for path in DIST.rglob('*') if path.is_file()}
assert actual_files == expected_files, actual_files ^ expected_files
for output, published in (
    ('outputs/index.html', 'index.html'),
    ('outputs/zh/index.html', 'zh/index.html'),
    ('outputs/en/index.html', 'en/index.html'),
):
    assert (ROOT / output).read_bytes() == (DIST / published).read_bytes()

png = (DIST / 'social-preview.png').read_bytes()
assert png.startswith(b'\x89PNG\r\n\x1a\n')
assert struct.unpack('>II', png[16:24]) == (1200, 630)
assert b'<svg' in (DIST / 'favicon.svg').read_bytes()
assert f'Sitemap: {SITE_URL}sitemap.xml' in (DIST / 'robots.txt').read_text(encoding='utf-8')

namespace = {
    's': 'http://www.sitemaps.org/schemas/sitemap/0.9',
    'x': 'http://www.w3.org/1999/xhtml',
}
root = ET.parse(DIST / 'sitemap.xml').getroot()
entries = root.findall('s:url', namespace)
assert len(entries) == 3
assert {entry.find('s:loc', namespace).text for entry in entries} == set(ALTERNATES.values())
for entry in entries:
    links = {
        element.attrib['hreflang']: element.attrib['href']
        for element in entry.findall('x:link', namespace)
    }
    assert links == ALTERNATES, links
print('PASS public artifact: exact allowlist, 1200×630 image, reciprocal sitemap alternates')
