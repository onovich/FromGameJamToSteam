"""Package both localized pages and crawl files for GitHub Pages."""

from pathlib import Path
from shutil import copyfile

from i18n import SITE_URL


ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / 'dist'
DIST.mkdir(exist_ok=True)

for language in ('zh', 'en'):
    target = DIST / language
    target.mkdir(exist_ok=True)
    copyfile(ROOT / 'outputs' / language / 'index.html', target / 'index.html')
copyfile(ROOT / 'outputs/index.html', DIST / 'index.html')
(DIST / 'robots.txt').write_text(
    f'User-agent: *\nAllow: /\nSitemap: {SITE_URL}sitemap.xml\n',
    encoding='utf-8',
)
(DIST / 'sitemap.xml').write_text(
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    f'  <url><loc>{SITE_URL}zh/</loc></url>\n'
    f'  <url><loc>{SITE_URL}en/</loc></url>\n'
    '</urlset>\n',
    encoding='utf-8',
)
print(f'Prepared {DIST}')
