"""Package both localized pages and crawl files for GitHub Pages."""

from pathlib import Path
from shutil import copyfile, rmtree

from i18n import SITE_URL


ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / 'dist'
if DIST.exists():
    assert DIST.resolve() == ROOT.resolve() / 'dist', 'Refusing to clear an unexpected path'
    rmtree(DIST)
DIST.mkdir()

for language in ('zh', 'en'):
    target = DIST / language
    target.mkdir(exist_ok=True)
    copyfile(ROOT / 'outputs' / language / 'index.html', target / 'index.html')
copyfile(ROOT / 'outputs/index.html', DIST / 'index.html')
copyfile(ROOT / 'assets/favicon.svg', DIST / 'favicon.svg')
copyfile(ROOT / 'assets/social-preview.png', DIST / 'social-preview.png')
(DIST / 'robots.txt').write_text(
    f'User-agent: *\nAllow: /\nSitemap: {SITE_URL}sitemap.xml\n',
    encoding='utf-8',
)
alternates = (
    ('zh-CN', f'{SITE_URL}zh/'),
    ('en', f'{SITE_URL}en/'),
    ('x-default', SITE_URL),
)
sitemap = [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
    'xmlns:xhtml="http://www.w3.org/1999/xhtml">',
]
for url in (SITE_URL, f'{SITE_URL}zh/', f'{SITE_URL}en/'):
    sitemap.append(f'  <url><loc>{url}</loc>')
    for language, alternate_url in alternates:
        sitemap.append(
            f'    <xhtml:link rel="alternate" hreflang="{language}" href="{alternate_url}" />'
        )
    sitemap.append('  </url>')
sitemap.append('</urlset>')
(DIST / 'sitemap.xml').write_text('\n'.join(sitemap) + '\n', encoding='utf-8')
print(f'Prepared {DIST}')
