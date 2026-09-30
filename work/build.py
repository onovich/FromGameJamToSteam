"""Build complete Chinese and English static pages from one data snapshot."""

import html
import json
from collections import Counter
from pathlib import Path

from collect import NAMES
from i18n import CATEGORY_CODES, CATEGORY_LABELS, NOTES, SITE_URL, TEXT


ROOT = Path(__file__).resolve().parent.parent
RAW = json.loads((ROOT / 'work/steam_raw.json').read_text(encoding='utf-8'))
SOURCE_URL = 'https://gmtk.substack.com/p/100-steam-games-that-started-life'
SITE_NAME = '游戏观察'
SOCIAL_IMAGE_URL = f'{SITE_URL}social-preview.png'

EDITORIAL_ZH = {}
for line in (ROOT / 'work/editorial.txt').read_text(encoding='utf-8').splitlines():
    if line.strip():
        name, category, description = line.split('|', 2)
        EDITORIAL_ZH[name] = (category, description)

EDITORIAL_EN = {}
for line in (ROOT / 'work/editorial_en.txt').read_text(encoding='utf-8').splitlines():
    if line.strip():
        name, description = line.split('|', 1)
        EDITORIAL_EN[name] = description

assert len(NAMES) == len(EDITORIAL_ZH) == len(EDITORIAL_EN) == 100
assert set(NAMES) == set(EDITORIAL_ZH) == set(EDITORIAL_EN) == set(RAW)
assert all(category in CATEGORY_CODES for category, _ in EDITORIAL_ZH.values())

JAM = {
    'Rollerdrome': (2017, 'https://itch.io/jam/gmtk-jam'),
    'Singled Out': (2019, 'https://itch.io/jam/gmtk-2019'),
    'Press Ctrl': (2020, 'https://itch.io/jam/gmtk-2020'),
    'Threadbound': (2021, 'https://itch.io/jam/gmtk-2021'),
    'In Space No One Can Hear You Clean': (2021, 'https://itch.io/jam/gmtk-2021'),
    'Blueprint Bob': (2024, 'https://itch.io/jam/gmtk-2024'),
    'Nested': (2024, 'https://itch.io/jam/gmtk-2024'),
    'Scale the Depths': (2024, 'https://itch.io/jam/gmtk-2024'),
    'Fragment': (2025, 'https://itch.io/jam/gmtk-2025'),
}

H = html.escape
CSS = (ROOT / 'work/style.css').read_text(encoding='utf-8')
JS = (ROOT / 'work/ui.js').read_text(encoding='utf-8')


def status_for(name, item):
    if name == 'Loaded Dice':
        return 'unknown'
    if name == 'A Little to the Left':
        return 'released'
    release = item['details']['release_date']
    assert release is not None, name
    return 'upcoming' if release['coming_soon'] else 'released'


STATUSES = Counter(status_for(name, RAW[name]) for name in NAMES)
CATEGORIES = Counter(EDITORIAL_ZH[name][0] for name in NAMES)
assert STATUSES == {'released': 70, 'upcoming': 29, 'unknown': 1}, STATUSES
assert sum(CATEGORIES.values()) == 100


def render_cards(locale):
    t = TEXT[locale]
    cards = []
    for index, name in enumerate(NAMES, 1):
        category_zh, description_zh = EDITORIAL_ZH[name]
        category = CATEGORY_CODES[category_zh]
        category_label = CATEGORY_LABELS[locale][category_zh]
        description = description_zh if locale == 'zh-CN' else EDITORIAL_EN[name]
        item = RAW[name]
        appid = item['chosen']
        status = status_for(name, item)
        if status != 'unknown':
            assert appid and (name == 'A Little to the Left' or item['details']['steam_appid'] == appid), name

        image = item['details'].get('header_image')
        if name == 'A Little to the Left':
            image = 'https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/1629520/header.jpg'
        loading = 'eager' if index <= 2 else 'lazy'
        priority = ' fetchpriority="high"' if index == 1 else ''
        image_html = (
            f'<img src="{H(image)}" alt="{H(t["image_alt"].format(name=name))}" '
            f'width="460" height="215" loading="{loading}"{priority} decoding="async">'
            if image else
            f'<div class="image-missing" aria-hidden="true"><span>?</span><small>{H(t["image_missing"])}</small></div>'
        )
        year_html = (
            f'<a class="jam-year" href="{H(JAM[name][1])}" target="_blank" rel="noopener noreferrer" '
            f'title="{H(t["jam_year_title"])}">Jam {JAM[name][0]} ↗</a>'
            if name in JAM else ''
        )
        status_label = t['link_unverified'] if status == 'unknown' else t[status]
        steam_link = (
            f'<a class="steam-link" href="https://store.steampowered.com/app/{appid}/" '
            f'target="_blank" rel="noopener noreferrer" aria-label="{H(t["steam_aria"].format(name=name))}">'
            'Steam <span aria-hidden="true">↗</span></a>'
            if appid else f'<span class="no-link">{H(t["no_link"])}</span>'
        )
        note_html = f'\n        <p class="card-note">{H(NOTES[locale][name])}</p>' if name in NOTES[locale] else ''
        search_text = ' '.join(
            [name, category_zh, category_label, description_zh, EDITORIAL_EN[name],
             str(JAM[name][0]) if name in JAM else '']
        )
        cards.append(f'''<article class="game-row" id="game-{index:03d}" data-category="{category}" data-status="{status}" data-search="{H(search_text)}">
      <div class="row-cover">{image_html}</div>
      <div class="row-main">
        <div class="row-heading"><span class="row-number">{index:02d}</span><h3>{H(name)}</h3></div>
        <div class="row-meta"><span class="category">{H(category_label)}</span><span class="status {status}"><span class="status-dot" aria-hidden="true"></span>{H(status_label)}</span>{year_html}</div>
        <p class="mechanic">{H(description)}</p>{note_html}
      </div>
      <div class="row-action">{steam_link}</div>
    </article>''')
    return ''.join(cards)


def render_filters(locale):
    t = TEXT[locale]
    buttons = [
        f'<button type="button" data-category-filter="" aria-pressed="true">{H(t["all_games"])} <span>100</span></button>'
    ]
    for category_zh, count in CATEGORIES.most_common():
        label = CATEGORY_LABELS[locale][category_zh]
        buttons.append(
            f'<button type="button" data-category-filter="{CATEGORY_CODES[category_zh]}" '
            f'aria-pressed="false">{H(label)} <span>{count}</span></button>'
        )
    return '\n'.join(buttons)


REDIRECT_SCRIPT = '''<script>
(() => {
  let stored = '';
  try { stored = localStorage.getItem('jam-to-steam-language') || ''; } catch {}
  const browser = (navigator.languages && navigator.languages[0]) || navigator.language || '';
  const language = ['zh-CN', 'en'].includes(stored) ? stored : /^zh(?:-|$)/i.test(browser) ? 'zh-CN' : 'en';
  const path = language === 'zh-CN' ? 'zh/' : 'en/';
  location.replace(new URL(path + location.hash, new URL('.', location.href)));
})();
</script>'''


def render_page(locale, canonical_url, nav_base):
    t = TEXT[locale]
    stats_aria = t['stats_aria'].format(**STATUSES)
    count_text = t['count'].format(visible=100, total=100)
    category_buttons = render_filters(locale)
    cards = render_cards(locale)
    current_zh = ' aria-current="page"' if locale == 'zh-CN' else ''
    current_en = ' aria-current="page"' if locale == 'en' else ''
    schema = json.dumps({
        '@context': 'https://schema.org',
        '@type': 'CollectionPage',
        'name': t['title'],
        'description': t['description'],
        'url': canonical_url,
        'inLanguage': locale,
        'isPartOf': {'@id': f'{SITE_URL}#website'},
        'isBasedOn': SOURCE_URL,
    }, ensure_ascii=False)
    og_locale = 'zh_CN' if locale == 'zh-CN' else 'en_US'
    og_other_locale = 'en_US' if locale == 'zh-CN' else 'zh_CN'
    return f'''<!doctype html>
<html lang="{locale}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="dark">
  <meta name="theme-color" content="#081b2d">
  <meta name="robots" content="index,follow,max-image-preview:large">
  <meta name="description" content="{H(t['description'])}">
  <link rel="canonical" href="{canonical_url}">
  <link rel="icon" type="image/svg+xml" href="{SITE_URL}favicon.svg">
  <link rel="alternate" hreflang="zh-CN" href="{SITE_URL}zh/">
  <link rel="alternate" hreflang="en" href="{SITE_URL}en/">
  <link rel="alternate" hreflang="x-default" href="{SITE_URL}">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="{SITE_NAME}">
  <meta property="og:locale" content="{og_locale}">
  <meta property="og:locale:alternate" content="{og_other_locale}">
  <meta property="og:title" content="{H(t['title'])}">
  <meta property="og:description" content="{H(t['description'])}">
  <meta property="og:url" content="{canonical_url}">
  <meta property="og:image" content="{SOCIAL_IMAGE_URL}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="{H(t['social_alt'])}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{H(t['title'])}">
  <meta name="twitter:description" content="{H(t['description'])}">
  <meta name="twitter:image" content="{SOCIAL_IMAGE_URL}">
  <title>{H(t['title'])}</title>
  <script type="application/ld+json">{schema}</script>
  <style>{CSS}</style>
</head>
<body>
<a class="skip-link" href="#catalog">{H(t['skip'])}</a>
<header class="site-header"><div class="shell header-inner">
  <a class="brand" href="#top">{H(t['brand'])}</a>
  <nav class="header-links" aria-label="{H(t['nav_games'])}"><a href="#catalog">{H(t['nav_games'])}</a><a href="#method">{H(t['nav_method'])}</a></nav>
  <div class="source-meta"><span>{H(t['source_prefix'])}</span><a href="{SOURCE_URL}" target="_blank" rel="noopener noreferrer">{H(t['source_article'])}</a><span class="source-date">{H(t['verified_date'])}</span></div>
  <nav class="language-switch" aria-label="{H(t['language_label'])}"><a href="{nav_base}zh/" data-lang="zh-CN" lang="zh-CN"{current_zh}>中</a><a href="{nav_base}en/" data-lang="en" lang="en"{current_en}>EN</a></nav>
</div></header>
<main id="top">
  <div class="shell">
    <section class="hero" aria-labelledby="page-title">
      <div class="hero-copy">
        <p class="eyebrow">{H(t['eyebrow'])}</p>
        <h1 id="page-title">{H(t['hero_title'])}</h1>
        <p class="hero-subtitle">{H(t['hero_subtitle'])}</p>
      </div>
      <div class="hero-stats" aria-label="{H(stats_aria)}">
        <div class="stat-items">
          <div class="stat released" aria-label="{STATUSES['released']} {H(t['released'])}"><strong>{STATUSES['released']}</strong><span>{H(t['released'])}</span></div>
          <div class="stat upcoming" aria-label="{STATUSES['upcoming']} {H(t['upcoming'])}"><strong>{STATUSES['upcoming']}</strong><span>{H(t['upcoming'])}</span></div>
          <div class="stat unknown" aria-label="{STATUSES['unknown']} {H(t['unknown'])}"><strong>{STATUSES['unknown']}</strong><span>{H(t['unknown'])}</span></div>
        </div>
        <div class="status-meter" aria-hidden="true"><span class="released" style="width:{STATUSES['released']}%"></span><span class="upcoming" style="width:{STATUSES['upcoming']}%"></span><span class="unknown" style="width:{STATUSES['unknown']}%"></span></div>
      </div>
    </section>
  </div>
  <section class="shell catalog" id="catalog" aria-labelledby="catalog-title">
    <aside class="sidebar" aria-label="{H(t['category_aria'])}">
      <h2>{H(t['category_heading'])}</h2>
      <div class="category-filters" role="group" aria-label="{H(t['category_aria'])}">{category_buttons}</div>
      <p class="sidebar-note">{H(t['sidebar_note'])}</p>
    </aside>
    <div class="catalog-main">
      <div class="toolbar" role="search">
        <label for="search">{H(t['search_label'])}</label><input id="search" type="search" placeholder="{H(t['search_label'])}" autocomplete="off">
        <label for="status-filter">{H(t['status_filter_label'])}</label><select id="status-filter"><option value="">{H(t['all_statuses'])}</option><option value="released">{H(t['released'])}</option><option value="upcoming">{H(t['upcoming'])}</option><option value="unknown">{H(t['link_unverified'])}</option></select>
        <button class="clear-button" id="clear-filters" type="button">{H(t['clear'])}</button>
      </div>
      <div class="list-heading"><h2 id="catalog-title">{H(t['catalog'])}</h2><p>{H(t['source_order'])}</p><span class="result-count" id="result-count" role="status" aria-live="polite" data-template="{H(t['count'])}">{H(count_text)}</span></div>
      <div class="game-list" id="game-list">{cards}</div>
      <p class="empty-state" id="empty-state" hidden>{H(t['empty'])}</p>
    </div>
  </section>
  <section class="shell method" id="method" aria-label="{H(t['nav_method'])}">
    <details><summary>{H(t['method_heading'])}</summary><div class="method-content">
      <p>{H(t['method_intro_before'])}<a href="{SOURCE_URL}" target="_blank" rel="noopener noreferrer">{H(t['method_source_name'])}</a>{H(t['method_intro_after'])}</p>
      <p>{H(t['method_status'])}</p>
      <p>{H(t['method_covers'])}</p>
    </div></details>
  </section>
</main>
<footer class="site-footer"><div class="shell"><span>{H(t['footer_snapshot'])}</span><span>{H(t['footer_right'])}</span></div></footer>
<script>{JS}</script>
</body></html>'''


def render_landing():
    """Keep the root a distinct, crawlable language selector when JS is unavailable."""
    title = 'From Game Jam to Steam | 中文与 English'
    description = 'Explore 100 games from Game Jam to Steam in English or Chinese. 浏览 100 款从 Game Jam 走向 Steam 的游戏。'
    schema = json.dumps({
        '@context': 'https://schema.org',
        '@type': 'WebSite',
        '@id': f'{SITE_URL}#website',
        'url': SITE_URL,
        'name': SITE_NAME,
        'alternateName': 'Game Observatory',
        'inLanguage': ['zh-CN', 'en'],
    }, ensure_ascii=False)
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="dark">
  <meta name="theme-color" content="#081b2d">
  <meta name="robots" content="index,follow,max-image-preview:large">
  <meta name="description" content="{H(description)}">
  <link rel="canonical" href="{SITE_URL}">
  <link rel="icon" type="image/svg+xml" href="{SITE_URL}favicon.svg">
  <link rel="alternate" hreflang="zh-CN" href="{SITE_URL}zh/">
  <link rel="alternate" hreflang="en" href="{SITE_URL}en/">
  <link rel="alternate" hreflang="x-default" href="{SITE_URL}">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="{SITE_NAME}">
  <meta property="og:title" content="{H(title)}">
  <meta property="og:description" content="{H(description)}">
  <meta property="og:url" content="{SITE_URL}">
  <meta property="og:image" content="{SOCIAL_IMAGE_URL}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="100 games shown as a grid of release status markers">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{H(title)}">
  <meta name="twitter:description" content="{H(description)}">
  <meta name="twitter:image" content="{SOCIAL_IMAGE_URL}">
  <title>{H(title)}</title>
  <script type="application/ld+json">{schema}</script>
{REDIRECT_SCRIPT}
  <style>{CSS}
  .language-landing {{ max-width: 760px; padding: clamp(70px, 12vw, 150px) 0; }}
  .language-landing h1 {{ margin-bottom: 16px; }}
  .language-landing p {{ color: var(--muted); }}
  .language-choices {{ display: flex; flex-wrap: wrap; gap: 12px; margin-top: 35px; }}
  .language-choices a {{ min-width: 200px; padding: 20px 24px; border: 1px solid var(--line); border-radius: 9px; background: var(--surface); color: var(--text); text-decoration: none; font-weight: 700; }}
  .language-choices a:hover {{ border-color: var(--cyan); color: var(--cyan); }}
  </style>
</head>
<body>
<header class="site-header"><div class="shell header-inner"><span class="brand">{SITE_NAME} / Game Observatory</span></div></header>
<main class="shell language-landing">
  <p class="eyebrow">INDEPENDENT GAME DATA DIRECTORY</p>
  <h1>From Game Jam to Steam</h1>
  <p>Explore the Steam journey of 100 games. <span lang="zh-CN">查看 100 款游戏的 Steam 去向。</span></p>
  <nav class="language-choices" aria-label="Choose language / 选择语言"><a href="./zh/" lang="zh-CN">中文版 ↗</a><a href="./en/" lang="en">English version ↗</a></nav>
  <p>Source: <a href="{SOURCE_URL}" target="_blank" rel="noopener noreferrer">Game Maker's Toolkit article</a>. Independent compilation.</p>
</main>
</body></html>'''


OUTPUTS = {
    ROOT / 'outputs/index.html': render_landing(),
    ROOT / 'outputs/zh/index.html': render_page('zh-CN', f'{SITE_URL}zh/', '../'),
    ROOT / 'outputs/en/index.html': render_page('en', f'{SITE_URL}en/', '../'),
}
for path, page in OUTPUTS.items():
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(page, encoding='utf-8')
    print(path, 'bytes', path.stat().st_size)

# Keep the old local preview address usable while the published root routes by language.
(ROOT / 'outputs/game-jam-to-steam-100.html').write_text(
    OUTPUTS[ROOT / 'outputs/index.html'], encoding='utf-8'
)
print('statuses', dict(STATUSES), 'categories', dict(CATEGORIES))
