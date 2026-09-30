import json
import re
import time
import unicodedata
from pathlib import Path

import requests


NAMES = [
    "100 Keys to Your Heart", "A Little to the Left", "The Baby in Yellow", "Blood Typers",
    "Blueprint Bob", "Boomerang X", "Breezy", "Cappy & Tappy: Temples of Peril",
    "Cleaning the System", "Coasterama", "Deadly Heart Gambit", "Diceomancer",
    "Frogmageddon", "BunnyFly: Season of Summer", "Clean Stack", "Coaster Crash Course",
    "Collapse Relapse", "Control:Override", "Death in your Dice", "Deep Snake",
    "Dicetris", "(Dis)assemble", "Dyestributor", "Faster Bunnies", "Fragment",
    "GIMMIKO", "Gunslinger Express", "IM LOOPY FOR DOOP LOOPS!!!",
    "In Space No One Can Hear You Clean", "Loop my Crank", "The Gardener and the Wild Vines",
    "Globs", "The Good Overlord", "Happenlance", "Hate Me Not", "How Many Dudes?",
    "Imagine Sisyphus Happy", "Koromeke", "KoroNeko", "Mingle", "Molecoole", "Moonbrella",
    "Maces and Dices", "Negative Time", "ODA", "PhotoLoop", "Roku and Rei",
    "Roll it to the End", "Scale Mail", "Side by Size", "Skyblocker", "Sloop",
    "Spaceship for Newbies", "Split Happens", "Trigger of Time", "Wait, Is That Me?",
    "Where Is My Parking Spot", "Willow Guard", "You Are The Code", "Ziggy's Cosmic Adventures",
    "Negative Nancy", "Neon Shift", "Nested", "Omelet You Cook", "PortalSnake",
    "Press Ctrl", "Push The Cat with WASD", "Rollerdrome", "Scale the Depths",
    "Singled Out", "Sisyphus Is a Bug", "Slider", "Draftula", "First Class Rescue",
    "Galactic Diner", "Getting Goopy", "House Always WINS!", "Kickochet", "Laser Guy",
    "Last Round at the End of the World", "Loaded Dice", "Looplash", "Mycelium Mayhem",
    "Robot Reckoning", "Songrunner", "Splatterpus", "Time Travel Shanty", "Sol Cesto",
    "Squarepinski", "Swan Song", "Tape Man", "Tenvader", "TetherGeist", "Threadbound",
    "Tiny Traffic", "Two-Timin' Towers", "UvsU: You vs. You", "Word Factori", "Word Play",
    "Wrangle Ranch",
]


def norm(value):
    value = unicodedata.normalize("NFKD", value).casefold()
    return re.sub(r"[^a-z0-9]+", "", value)


def search(session, name):
    response = session.get(
        "https://store.steampowered.com/api/storesearch/",
        params={"term": name, "l": "english", "cc": "us"},
        timeout=25,
    )
    response.raise_for_status()
    items = response.json().get("items", [])
    exact = [item for item in items if norm(item["name"]) == norm(name)]
    return (exact or items)[:5], bool(exact)


def details(session, appid):
    response = session.get(
        "https://store.steampowered.com/api/appdetails/",
        params={"appids": appid, "l": "english", "cc": "us"},
        timeout=25,
    )
    response.raise_for_status()
    values = response.json().values()
    return next((v.get("data", {}) for v in values if v.get("data", {}).get("steam_appid") == appid), {})


def main():
    assert len(NAMES) == 100 and len(set(NAMES)) == 100
    path = Path("work/steam_raw.json")
    saved = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    session = requests.Session()
    session.headers.update({"User-Agent": "GMTK-100-research/1.0 (personal research; sequential requests)"})
    for i, name in enumerate(NAMES, 1):
        if name in saved:
            continue
        try:
            choices, exact = search(session, name)
            match = choices[0] if choices else None
            info = details(session, match["id"]) if match else {}
            saved[name] = {
                "choices": [{"name": x["name"], "id": x["id"]} for x in choices],
                "exact": exact,
                "chosen": match["id"] if match else None,
                "details": {
                    "name": info.get("name"),
                    "short_description": info.get("short_description"),
                    "header_image": info.get("header_image"),
                    "release_date": info.get("release_date"),
                    "steam_appid": info.get("steam_appid"),
                    "type": info.get("type"),
                    "demos": info.get("demos"),
                },
            }
            path.write_text(json.dumps(saved, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"{i:03d} {'OK' if exact else 'CHECK'} {name} => {match['name'] if match else 'NONE'}", flush=True)
        except Exception as exc:
            print(f"{i:03d} ERROR {name}: {exc}", flush=True)
            if "429" in str(exc) or "403" in str(exc):
                break
        time.sleep(0.55)


if __name__ == "__main__":
    main()
