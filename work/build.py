import html
import json
from collections import Counter
from pathlib import Path

from collect import NAMES


ROOT = Path(__file__).resolve().parent.parent
RAW = json.loads((ROOT / 'work/steam_raw.json').read_text(encoding='utf-8'))
EDITORIAL = {}
for line in (ROOT / 'work/editorial.txt').read_text(encoding='utf-8').splitlines():
    if not line.strip():
        continue
    name, category, description = line.split('|', 2)
    EDITORIAL[name] = (category, description)
assert len(NAMES) == len(EDITORIAL) == 100
assert set(NAMES) == set(EDITORIAL)

JAM = {
    'Rollerdrome': (2017, "Dual Purpose Design", 'https://itch.io/jam/gmtk-jam'),
    'Singled Out': (2019, "Only One", 'https://itch.io/jam/gmtk-2019'),
    'Press Ctrl': (2020, "Out of Control", 'https://itch.io/jam/gmtk-2020'),
    'Threadbound': (2021, "Joined Together", 'https://itch.io/jam/gmtk-2021'),
    'In Space No One Can Hear You Clean': (2021, "Joined Together", 'https://itch.io/jam/gmtk-2021'),
    'Blueprint Bob': (2024, "Built to Scale", 'https://itch.io/jam/gmtk-2024'),
    'Nested': (2024, "Built to Scale", 'https://itch.io/jam/gmtk-2024'),
    'Scale the Depths': (2024, "Built to Scale", 'https://itch.io/jam/gmtk-2024'),
    'Fragment': (2025, "Loop", 'https://itch.io/jam/gmtk-2025'),
}
NOTES = {
    'KoroNeko': '作者称原型 Qube 错过正式投稿截止。',
    'Sol Cesto': '作者称 2022 年原型未正式投稿 Jam。',
    'Word Play': '来自 GMTK 的 Patreon 社区内部 Jam，非公开主赛。',
}
H = html.escape
SITE_URL = 'https://jam-to-steam.onovich.com/'
PAGE_TITLE = '从 Game Jam 到 Steam｜100 款游戏数据目录'
PAGE_DESCRIPTION = '浏览从 Game Jam 走向 Steam 的 100 款游戏，按玩法类型和发售状态筛选，查看中文玩法概述与 Steam 商店链接。'

cards = []
statuses = Counter()
categories = Counter()
for index, name in enumerate(NAMES, 1):
    category, description = EDITORIAL[name]
    item = RAW[name]
    appid = item['chosen']
    if name == 'Loaded Dice':
        status = 'unknown'
    elif name == 'A Little to the Left':
        status = 'released'
    else:
        release = item['details']['release_date']
        assert release is not None, name
        status = 'upcoming' if release['coming_soon'] else 'released'
    if status != 'unknown':
        assert appid and (name == 'A Little to the Left' or item['details']['steam_appid'] == appid), name
    statuses[status] += 1
    categories[category] += 1
    image = item['details'].get('header_image')
    if name == 'A Little to the Left':
        image = 'https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/1629520/header.jpg'
    image_html = (f'<img src="{H(image)}" alt="《{H(name)}》Steam 商店封面" loading="lazy" decoding="async">'
                  if image else '<div class="image-missing" aria-hidden="true"><span>?</span><small>封面待核实</small></div>')
    year_html = (f'<a class="jam-year" href="{H(JAM[name][2])}" target="_blank" rel="noopener noreferrer" '
                 f'title="查看官方 Jam 年度页">Jam {JAM[name][0]} ↗</a>'
                 if name in JAM else '')
    if status == 'released':
        status_label = '已发售'
    elif status == 'upcoming':
        status_label = '未发售'
    else:
        status_label = '链接待核实'
    steam_link = (f'<a class="steam-link" href="https://store.steampowered.com/app/{appid}/" '
                  f'target="_blank" rel="noopener noreferrer" aria-label="在 Steam 查看 {H(name)}">Steam <span aria-hidden="true">↗</span></a>'
                  if appid else '<span class="no-link">Steam 链接待核实</span>')
    note_html = f'<p class="card-note">{H(NOTES[name])}</p>' if name in NOTES else ''
    search_text = ' '.join([name, category, description, str(JAM[name][0]) if name in JAM else ''])
    cards.append(f'''<article class="game-row" id="game-{index:03d}" data-category="{H(category)}" data-status="{status}" data-search="{H(search_text)}">
      <div class="row-cover">{image_html}</div>
      <div class="row-main">
        <div class="row-heading"><span class="row-number">{index:02d}</span><h3>{H(name)}</h3></div>
        <div class="row-meta"><span class="category">{H(category)}</span><span class="status {status}"><span class="status-dot" aria-hidden="true"></span>{status_label}</span>{year_html}</div>
        <p class="mechanic">{H(description)}</p>
        {note_html}
      </div>
      <div class="row-action">{steam_link}</div>
    </article>''')

assert statuses == {'released': 70, 'upcoming': 29, 'unknown': 1}, statuses
assert sum(categories.values()) == 100
category_buttons = '<button type="button" data-category-filter="" aria-pressed="true">全部游戏 <span>100</span></button>\n' + '\n'.join(
    f'<button type="button" data-category-filter="{H(cat)}" aria-pressed="false">{H(cat)} <span>{count}</span></button>'
    for cat, count in categories.most_common()
)

css = (ROOT / 'work/style.css').read_text(encoding='utf-8')

js = (ROOT / 'work/ui.js').read_text(encoding='utf-8')

page = f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="dark">
  <meta name="robots" content="index,follow,max-image-preview:large">
  <meta name="description" content="{PAGE_DESCRIPTION}">
  <link rel="canonical" href="{SITE_URL}">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="游戏观察">
  <meta property="og:title" content="{PAGE_TITLE}">
  <meta property="og:description" content="{PAGE_DESCRIPTION}">
  <meta property="og:url" content="{SITE_URL}">
  <title>{PAGE_TITLE}</title>
  <script type="application/ld+json">{json.dumps({'@context': 'https://schema.org', '@type': 'WebSite', 'name': '游戏观察', 'url': SITE_URL}, ensure_ascii=False)}</script>
  <style>{css}</style>
</head>
<body>
<a class="skip-link" href="#catalog">跳到游戏目录</a>
<header class="site-header"><div class="shell header-inner">
  <a class="brand" href="#top">游戏观察</a>
  <nav class="header-links" aria-label="页面导航"><a href="#catalog">游戏列表</a><a href="#method">数据说明</a></nav>
  <div class="source-meta"><span>数据来源：</span><a href="https://gmtk.substack.com/p/100-steam-games-that-started-life" target="_blank" rel="noopener noreferrer">Game Maker's Toolkit 原文 ↗</a><span class="source-date">2026-09-26 核查</span></div>
</div></header>
<main id="top">
  <div class="shell">
    <section class="hero" aria-labelledby="page-title">
      <div class="hero-copy">
        <p class="eyebrow">独立游戏数据目录</p>
        <h1 id="page-title">从 Game Jam 到 Steam</h1>
        <p class="hero-subtitle">100 款游戏的 Steam 去向</p>
      </div>
      <div class="hero-stats" aria-label="100款游戏的发售状态：{statuses['released']} 已发售，{statuses['upcoming']} 未发售，{statuses['unknown']} 待核实">
        <div class="stat-items">
          <div class="stat released" aria-label="{statuses['released']} 已发售"><strong>{statuses['released']}</strong><span>已发售</span></div>
          <div class="stat upcoming" aria-label="{statuses['upcoming']} 未发售"><strong>{statuses['upcoming']}</strong><span>未发售</span></div>
          <div class="stat unknown" aria-label="{statuses['unknown']} 待核实"><strong>{statuses['unknown']}</strong><span>待核实</span></div>
        </div>
        <div class="status-meter" aria-hidden="true"><span class="released" style="width:{statuses['released']}%"></span><span class="upcoming" style="width:{statuses['upcoming']}%"></span><span class="unknown" style="width:{statuses['unknown']}%"></span></div>
      </div>
    </section>
  </div>
  <section class="shell catalog" id="catalog" aria-labelledby="catalog-title">
    <aside class="sidebar" aria-label="玩法类型筛选">
      <h2>玩法类型</h2>
      <div class="category-filters" role="group" aria-label="按玩法类型筛选">{category_buttons}</div>
      <p class="sidebar-note">类型是为了浏览而整理的单一主标签。名单与核查口径见页面底部的数据说明。</p>
    </aside>
    <div class="catalog-main">
      <div class="toolbar" role="search">
        <label for="search">搜索游戏或玩法</label><input id="search" type="search" placeholder="搜索游戏或玩法" autocomplete="off">
        <label for="status-filter">发售状态</label><select id="status-filter"><option value="">全部发售状态</option><option value="released">已发售</option><option value="upcoming">未发售</option><option value="unknown">链接待核实</option></select>
        <button class="clear-button" id="clear-filters" type="button">清除筛选</button>
      </div>
      <div class="list-heading"><h2 id="catalog-title">游戏目录</h2><p>按来源清单顺序</p><span class="result-count" id="result-count" role="status" aria-live="polite">显示 100 / 100 款</span></div>
      <div class="game-list" id="game-list">{''.join(cards)}</div>
      <p class="empty-state" id="empty-state" hidden>没有符合条件的游戏。试试更短的关键词，或清除筛选。</p>
    </div>
  </section>
  <section class="shell method" id="method" aria-label="数据说明">
    <details><summary>数据来源与统计口径</summary><div class="method-content">
      <p>这 100 款名称取自 <a href="https://gmtk.substack.com/p/100-steam-games-that-started-life" target="_blank" rel="noopener noreferrer">Game Maker's Toolkit 作者文字版</a>，包括文中的快速点名。本站是独立整理，与原作者没有隶属关系；这份清单不是所有 Jam 作品的成功率统计。</p>
      <p>Steam 链接与发售状态核查于 2026-09-26：99 款有明确对应的商店页；《Loaded Dice》存在不同开发者的同名作品，暂不附链接。状态会随时间变化。类型是编辑性主标签，不代表 Steam 官方分类；Jam 年份仅在有可靠来源时显示。</p>
      <p>每款玩法概述依据原文与 Steam 官方介绍整理。Steam 封面由官方图片地址载入，网络不可用时仍可阅读文字。</p>
    </div></details>
  </section>
</main>
<footer class="site-footer"><div class="shell"><span>独立中文整理 · 数据核查：2026-09-26</span><span>游戏名称与封面归各开发者及发行方所有</span></div></footer>
<script>{js}</script>
</body></html>'''

out = ROOT / 'outputs/game-jam-to-steam-100.html'
out.parent.mkdir(exist_ok=True)
out.write_text(page, encoding='utf-8')
print(out)
print('statuses', dict(statuses), 'categories', dict(categories), 'bytes', out.stat().st_size)
