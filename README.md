# 从 Game Jam 到 Steam：100 款游戏目录

这是一个中英双语静态目录，收录 GMTK 作者文字版《100 Steam Games That Started Life in the GMTK Game Jam》中点名的 100 款游戏。页面按原文顺序排列，提供双语玩法概述、类型筛选，以及核实过的 Steam 商店链接。

## 文件

| 路径 | 用途 |
| --- | --- |
| `outputs/index.html` | 语言入口：根据浏览器语言进入中文或英文页面；手动选过语言时优先使用已保存的偏好。脚本不可用时显示双语选择页。 |
| `outputs/zh/index.html`、`outputs/en/index.html` | 可直接访问的完整静态页面；HTML、CSS、JavaScript 均内嵌，封面图片从 Steam 远程载入。 |
| `outputs/game-jam-to-steam-100.html` | 兼容旧本地预览地址的语言入口副本，不单独发布。 |
| `work/build.py` | 根据名单、编辑文案和 Steam 数据生成页面。 |
| `work/style.css`、`work/ui.js` | 页面样式和筛选交互的源文件；构建时内嵌进 HTML。 |
| `outputs/design-concepts/` | 视觉探索稿与设计说明，正式页面不依赖这些图片。 |
| `work/collect.py` | 作者原文的 100 款名单，以及初次收集 Steam API 数据的脚本。 |
| `work/editorial.txt` | 每款游戏的编辑性类型和中文玩法概述；每行格式为 `英文名称\|类型\|概述`。 |
| `work/editorial_en.txt` | 与中文名单逐项对应的英文玩法概述；每行格式为 `英文名称\|概述`。 |
| `work/i18n.py` | 中英文界面文案、类型译名和注释的统一来源。 |
| `work/steam_raw.json` | Steam 搜索与商店详情的原始记录、人工核实后的 `chosen` app ID。 |
| `work/evidence.md` | 来源、核查依据、例外和未解决的歧义。 |
| `work/fix_details.py`、`work/review.py` | 初次研究时使用的修复与检查脚本；保留作为材料，非日常构建步骤。 |
| `work/validate.py` | 对生成页面进行结构和内容校验。 |
| `work/prepare_pages.py` | 把双语成品打包成 GitHub Pages 页面、`robots.txt` 与含语言对应关系的站点地图。 |
| `assets/favicon.svg`、`assets/social-preview.png` | 站点图标和社交分享预览图；发布时复制到站点根目录。 |
| `.github/workflows/deploy.yml` | 推送到 `main` 后自动构建、校验并发布。 |

## 构建与查看

在本目录的 PowerShell 终端中运行：

```powershell
python -m pip install -r requirements.txt
python work/build.py
python work/prepare_pages.py
python work/validate.py
python -m http.server 8765 --directory dist
```

然后访问 `http://localhost:8765/`，或直接打开 `http://localhost:8765/zh/` 与 `http://localhost:8765/en/`。首页按浏览器首选语言进入对应页面：`zh` 开头的语言进入简体中文，其他语言进入英文。页眉可用「中 / EN」切换，选择保存在浏览器本地存储中，之后从首页访问会优先采用此偏好。日常构建只读取本地数据，不会请求 Steam；`requests` 依赖来自 `collect.py` 的导入。

## 发布域名

正式入口为 `https://jam-to-steam.onovich.com/`；中文与英文的独立地址分别为 `/zh/` 和 `/en/`。该子域名在 Cloudflare DNS 中用 CNAME 指向 `onovich.github.io`；GitHub Pages 由仓库的 Actions 工作流发布。首页是 `x-default` 双语选择页，浏览器正常运行脚本时按语言进入对应目录；三个地址分别设置 canonical，互相标注 hreflang，并写入 `sitemap.xml`。站点只发布构建后的七个文件。之后修改数据并推送 `main` 即可重新部署，无需手工上传 HTML。

## 维护数据

1. 修改 `work/editorial.txt` 中的中文概述或类型、`work/editorial_en.txt` 中相应的英文概述，或修改 `work/steam_raw.json` 中已核实的 Steam 记录。界面文案与类型译名统一修改 `work/i18n.py`。
2. 若更改名单或核实结论，同步检查 `work/build.py` 中的特例、Jam 年份、状态计数、核查日期与页面说明；`work/validate.py` 中的计数断言也反映当前快照。
3. 重新运行构建、打包和校验，并在浏览器中检查中文、英文页面及语言切换。若状态计数改变，同步更新 `assets/social-preview.png`。

`work/collect.py` 只收集 JSON 中尚不存在的名称，不能用于刷新已有游戏的发售状态。`work/fix_details.py` 会重新应用早期的人工选择，更新数据前应先查看脚本内容。Steam 详情会变化，当前页面和证据笔记记录的是 **2026-09-26** 的核查快照；不应仅因重新构建就改写这个日期。

## 资料边界

名单仅来自 [GMTK 作者文字版](https://gmtk.substack.com/p/100-steam-games-that-started-life)，原视频和 Backloggd 索引的角色与范围见 `work/evidence.md`。目前 99 款对应明确的 Steam 商店页；《Loaded Dice》存在不同开发者的同名游戏，暂未附商店链接。类型是为浏览而作的编辑性归类，不代表 Steam 官方标签；此目录也不推断销量或商业成功率。
