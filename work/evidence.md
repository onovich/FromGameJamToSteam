# GMTK「100 Steam Games」中文目录：证据与边界

核查日期：2026-09-26（北京时间）。目的：把作者于 2026-07-06 发布的百款清单做成便于浏览的中文目录；不把 Steam 商店页误写成已发售，不推断销量或盈利。

## 名单与范围

- 唯一的百款边界是 [GMTK 作者文字版](https://gmtk.substack.com/p/100-steam-games-that-started-life)。正文依次列出恰好 100 个名称，包括三段快速点名；`work/collect.py` 按该顺序保存名单。
- [原视频](https://youtu.be/usF4cpcxbZc) 是相同主题的作者材料。[Backloggd alumni 索引](https://backloggd.com/u/GameMakersTK/list/gmtk-game-jam-games/) 是持续增长的更大名单，不作为这 100 款的补名来源。
- 作者原文含已发售、未发售但有试玩、仅有商店页的游戏。目录的「已发售 / 未发售」取 2026-09-26 核查时 Steam 官方商店信息，而不是照搬 2026-07 的分组。
- 特例：Sol Cesto 的 2022 原型未正式投稿；Word Play 来自 Patreon 社区内部 Jam；KoroNeko 的原型 Qube 错过正式投稿截止。三者仍在作者的 100 款中，目录保留并标明。

## Steam 核查

- Steam 官方 `storesearch` API 将作者名称映射到 app ID；`appdetails` 的 `release_date.coming_soon` 和官方封面用于目录。访问是顺序、低频的；源记录见 `work/steam_raw.json`。Steam 页面随时间变化，目录状态是核查日快照。
- 已匹配 99 个明确对应的 Steam 商店 app；其中 70 个显示已发售，29 个显示未发售。A Little to the Left 的 API 详情未返回，使用其[官方 Steam 页面](https://store.steampowered.com/app/1629520/A_Little_to_the_Left/)确认已发售。
- `Fragment` 的普通 Steam 搜索优先给出同名近似结果；依据作者的「循环恐怖」描述及[官方 Steam 页面](https://store.steampowered.com/app/4023710/Fragment/)核为 app 4023710。开发者的[访谈](https://bossrush.net/2025/11/15/so-then-i-just-backed-it-a-series-on-my-kickstarter-adventures-part-17-fragment-interview-with-david-fuery/)亦说明 2025 GMTK 原型的来历。
- `Split Happens` 的官方游戏是估算等分物件的 [Split Happens!](https://store.steampowered.com/app/4650730/Split_Happens/)；同名的核电站合作游戏不是作者所述作品。
- `Loaded Dice` 有两款不同的未发售 Steam 游戏：[Yvantis 的骰子构筑](https://store.steampowered.com/app/4637880/)和[Café Ducha Siesta 的多人赌局](https://store.steampowered.com/app/4118100/)。作者仅点名，未写玩法/开发者；目前没找到足够证据确定其指向。目录保留名称，但不附错误链接或编造玩法，故 100 款名称、99 个核实 Steam 链接。

## Jam 年份与主题

仅在作者明言年份或有开发者直接说明，并能与官方 Jam 年度页的主题配对时展示。其余标「未核实」。

| 游戏 | 年份 / 主题 | 年份依据 | 主题依据 |
|---|---|---|---|
| Rollerdrome | 2017 / Dual Purpose Design | GMTK 作者文字版说第一届 | [2017 官方 Jam](https://itch.io/jam/gmtk-jam) |
| Singled Out | 2019 / Only One | GMTK 作者文字版 | [2019 官方 Jam](https://itch.io/jam/gmtk-2019) |
| Press Ctrl | 2020 / Out of Control | GMTK 作者文字版 | [2020 官方 Jam](https://itch.io/jam/gmtk-2020) |
| Threadbound | 2021 / Joined Together | GMTK 作者文字版 | [2021 官方 Jam](https://itch.io/jam/gmtk-2021) |
| In Space No One Can Hear You Clean | 2021 / Joined Together | [Steam 官方页](https://store.steampowered.com/app/1677630/In_Space_No_One_Can_Hear_You_Clean/)说明为 2021 GMTK Jam 制作 | [2021 官方 Jam](https://itch.io/jam/gmtk-2021) |
| Blueprint Bob、Nested、Scale the Depths | 2024 / Built to Scale | GMTK 作者文字版 | [2024 官方 Jam](https://itch.io/jam/gmtk-2024) |
| Fragment | 2025 / Loop | 上述开发者访谈 | [2025 官方 Jam](https://itch.io/jam/gmtk-2025) |

Sol Cesto 的 2022 关联来自作者文字版，但它没有正式投稿，页面单独说明，不把它计作参赛作品。

## 编辑原则

- 每款中文「核心玩法」是作者文字版描述与 Steam 官方短介绍的概述，并非逐字翻译。
- 类型是便于检索的编辑性单一主标签，不代表 Steam 官方类型，也不是对所有玩法的完整分类。
- 三条「从原型到成品」启发是具名案例的观察，不是对 100 款的普遍规律；没有计算成功率、商业成绩或项目盈利。
- 图片为 Steam 官方远程封面。网络不可用时页面文字仍完整可读。
