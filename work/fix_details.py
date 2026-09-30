import json
import time
from pathlib import Path

import requests
from collect import details

path = Path("work/steam_raw.json")
saved = json.loads(path.read_text(encoding="utf-8"))
saved["Fragment"]["chosen"] = 4023710
saved["Split Happens"]["chosen"] = 4650730
saved["Loaded Dice"]["chosen"] = None
saved["Loaded Dice"]["details"] = {}
session = requests.Session()
session.headers.update({"User-Agent": "GMTK-100-research/1.0 (personal research; sequential requests)"})
for name, item in saved.items():
    if item.get("chosen") and (not item["details"].get("name") or item["details"].get("steam_appid") != item["chosen"]):
        try:
            d = details(session, item["chosen"])
            item["details"] = {
                "name": d.get("name"), "short_description": d.get("short_description"),
                "header_image": d.get("header_image"), "release_date": d.get("release_date"),
                "steam_appid": d.get("steam_appid"), "type": d.get("type"), "demos": d.get("demos"),
            }
            path.write_text(json.dumps(saved, ensure_ascii=False, indent=2), encoding="utf-8")
            print(name, item["details"]["name"], flush=True)
        except Exception as exc:
            print("ERROR", name, exc, flush=True)
            if "429" in str(exc) or "403" in str(exc):
                break
        time.sleep(0.6)
