"""Package the verified single-page site for GitHub Pages."""

from pathlib import Path
from shutil import copyfile


ROOT = Path(__file__).resolve().parent.parent
SITE_URL = 'https://jam-to-steam.onovich.com/'
DIST = ROOT / 'dist'
DIST.mkdir(exist_ok=True)

copyfile(ROOT / 'outputs/game-jam-to-steam-100.html', DIST / 'index.html')
(DIST / 'robots.txt').write_text(
    f'User-agent: *\nAllow: /\nSitemap: {SITE_URL}sitemap.xml\n',
    encoding='utf-8',
)
(DIST / 'sitemap.xml').write_text(
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    f'  <url><loc>{SITE_URL}</loc></url>\n'
    '</urlset>\n',
    encoding='utf-8',
)
print(f'Prepared {DIST}')
