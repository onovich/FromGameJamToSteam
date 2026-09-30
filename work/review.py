import json

d = list(json.load(open('work/steam_raw.json', encoding='utf-8')).items())
for i, (name, value) in enumerate(d, 1):
    description = value['details'].get('short_description') or '?'
    print(f'{i:03d} {name}: {description[:210]}')
