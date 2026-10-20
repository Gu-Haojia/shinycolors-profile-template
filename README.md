<div align="center">

# ✦ Shiny Colors Profile

**把 GitHub 主页变成你的制作人档案。**

闪耀色彩页游风格 · 一张连续滚动的动画 SVG · GitHub Actions 自动更新

[使用模板](https://github.com/Gu-Haojia/shinycolors-profile-template/generate) · [部署指南](docs/DEPLOYMENT.md) · [角色图库](docs/CHARACTERS.md) · [配置说明](docs/CONFIGURATION.md) · [English](docs/README.en.md)

</div>

沿用《偶像大师 闪耀色彩》enza 页游的界面风格，把项目、语言、贡献和个人介绍放进主页、培育、制作人详情和任务画面。字体与图像内嵌，背景缓移、立绘浮动、气泡和图表动画直接在 SVG 中播放。适用于 GitHub Profile README，无需 GitHub Pages 或服务器。

## 三步开始

1. 点击 **[Use this template](https://github.com/Gu-Haojia/shinycolors-profile-template/generate)**，创建一个**公开仓库**，名字与自己的 GitHub 用户名完全一致。例如 `alice/alice`。已有同名仓库时，按[迁移指南](docs/DEPLOYMENT.md#已有个人主页仓库)操作。
2. 打开新仓库的 **Actions → Shiny Refresh → Run workflow**。如显示启用 Actions 的提示，先启用。等待运行成功。
3. 打开自己的 GitHub 个人页。默认自动识别账号、显示名、头像和项目；需要个性化时只改 [`config.json`](config.json) 与 [`projects.json`](projects.json)。

**不需要自己创建 Token。** 工作流使用 GitHub 自动提供的 `GITHUB_TOKEN`。默认每日北京时间 **00:17** 更新，也会在修改配置和源码后更新；其他项目的新提交在下一次更新时展示。

## 示例预览

以下是**虚构演示数据**，使用模板后会替换成你的 GitHub 数据。模板仓库的说明文档会保留；同名个人主页仓库会自动生成纯主页 README。

<details>
<summary>展开完整动态预览</summary>

<!-- SHINY:START -->
<!-- ✦ 本文件由 build.py 生成：配置 config.json / projects.json；python3 build.py 或 --offline --watch ✦ -->
<p align="center"><img src="assets/shinycolors.svg?v=3a79be216508" width="100%" alt="Your Name 的闪耀色彩风格主页 · Lv.35 · 连续贡献 4 天"/></p>
<!-- SHINY:END -->

</details>

## 28 位 Coding 伙伴

固定角色或设为 `random`。完整大图、角色 ID 和选择说明见[角色图库](docs/CHARACTERS.md)。

<!-- CHARACTERS:START -->
<table>
  <tr>
    <td align="center" width="14%"><a href="docs/CHARACTERS.md"><img src="assets/illustrations/mano-coding.webp?v=da5d737690b1" width="100" alt="櫻木真乃"><br><sub>櫻木真乃</sub></a><br><code>mano</code></td>
    <td align="center" width="14%"><a href="docs/CHARACTERS.md"><img src="assets/illustrations/hiori-coding.webp?v=48722258226a" width="100" alt="風野灯織"><br><sub>風野灯織</sub></a><br><code>hiori</code></td>
    <td align="center" width="14%"><a href="docs/CHARACTERS.md"><img src="assets/illustrations/meguru-coding.webp?v=0828ad926689" width="100" alt="八宮めぐる"><br><sub>八宮めぐる</sub></a><br><code>meguru</code></td>
    <td align="center" width="14%"><a href="docs/CHARACTERS.md"><img src="assets/illustrations/kogane-coding.webp?v=196982c4f5e2" width="100" alt="月岡恋鐘"><br><sub>月岡恋鐘</sub></a><br><code>kogane</code></td>
    <td align="center" width="14%"><a href="docs/CHARACTERS.md"><img src="assets/illustrations/kiriko-coding.webp?v=6eabfacb5ddb" width="100" alt="幽谷霧子"><br><sub>幽谷霧子</sub></a><br><code>kiriko</code></td>
    <td align="center" width="14%"><a href="docs/CHARACTERS.md"><img src="assets/illustrations/yuika-coding.webp?v=714a3d770f68" width="100" alt="三峰結華"><br><sub>三峰結華</sub></a><br><code>yuika</code></td>
    <td align="center" width="14%"><a href="docs/CHARACTERS.md"><img src="assets/illustrations/mamimi-coding.webp?v=4622dc8c65d9" width="100" alt="田中摩美々"><br><sub>田中摩美々</sub></a><br><code>mamimi</code></td>
  </tr>
  <tr>
    <td align="center" width="14%"><a href="docs/CHARACTERS.md"><img src="assets/illustrations/sakuya-coding.webp?v=3b45c5112552" width="100" alt="白瀬咲耶"><br><sub>白瀬咲耶</sub></a><br><code>sakuya</code></td>
    <td align="center" width="14%"><a href="docs/CHARACTERS.md"><img src="assets/illustrations/kaho-coding.webp?v=dceff91ff934" width="100" alt="小宮果穂"><br><sub>小宮果穂</sub></a><br><code>kaho</code></td>
    <td align="center" width="14%"><a href="docs/CHARACTERS.md"><img src="assets/illustrations/chiyoko-coding.webp?v=e40e1ee7dfcd" width="100" alt="園田智代子"><br><sub>園田智代子</sub></a><br><code>chiyoko</code></td>
    <td align="center" width="14%"><a href="docs/CHARACTERS.md"><img src="assets/illustrations/juri-coding.webp?v=b1ff5988cf52" width="100" alt="西城樹里"><br><sub>西城樹里</sub></a><br><code>juri</code></td>
    <td align="center" width="14%"><a href="docs/CHARACTERS.md"><img src="assets/illustrations/rinze-coding.webp?v=3081b878511d" width="100" alt="杜野凛世"><br><sub>杜野凛世</sub></a><br><code>rinze</code></td>
    <td align="center" width="14%"><a href="docs/CHARACTERS.md"><img src="assets/illustrations/natsuha-coding.webp?v=ae8a11afe5fc" width="100" alt="有栖川夏葉"><br><sub>有栖川夏葉</sub></a><br><code>natsuha</code></td>
    <td align="center" width="14%"><a href="docs/CHARACTERS.md"><img src="assets/illustrations/chiyuki-coding.webp?v=3ede5dc5e806" width="100" alt="桑山千雪"><br><sub>桑山千雪</sub></a><br><code>chiyuki</code></td>
  </tr>
  <tr>
    <td align="center" width="14%"><a href="docs/CHARACTERS.md"><img src="assets/illustrations/amana-coding.webp?v=85293fb7e241" width="100" alt="大崎甘奈"><br><sub>大崎甘奈</sub></a><br><code>amana</code></td>
    <td align="center" width="14%"><a href="docs/CHARACTERS.md"><img src="assets/illustrations/tenka-coding.webp?v=a283c01f5e9a" width="100" alt="大崎甜花"><br><sub>大崎甜花</sub></a><br><code>tenka</code></td>
    <td align="center" width="14%"><a href="docs/CHARACTERS.md"><img src="assets/illustrations/asahi-coding.webp?v=b4c43f5227e9" width="100" alt="芹沢あさひ"><br><sub>芹沢あさひ</sub></a><br><code>asahi</code></td>
    <td align="center" width="14%"><a href="docs/CHARACTERS.md"><img src="assets/illustrations/fuyuko-coding.webp?v=a3660206202f" width="100" alt="黛冬優子"><br><sub>黛冬優子</sub></a><br><code>fuyuko</code></td>
    <td align="center" width="14%"><a href="docs/CHARACTERS.md"><img src="assets/illustrations/mei-coding.webp?v=5c764e997d10" width="100" alt="和泉愛依"><br><sub>和泉愛依</sub></a><br><code>mei</code></td>
    <td align="center" width="14%"><a href="docs/CHARACTERS.md"><img src="assets/illustrations/toru-coding.webp?v=e4b5af331348" width="100" alt="浅倉透"><br><sub>浅倉透</sub></a><br><code>toru</code></td>
    <td align="center" width="14%"><a href="docs/CHARACTERS.md"><img src="assets/illustrations/madoka-coding.webp?v=f5e7b7029b87" width="100" alt="樋口円香"><br><sub>樋口円香</sub></a><br><code>madoka</code></td>
  </tr>
  <tr>
    <td align="center" width="14%"><a href="docs/CHARACTERS.md"><img src="assets/illustrations/koito-coding.webp?v=fb05f54bec84" width="100" alt="福丸小糸"><br><sub>福丸小糸</sub></a><br><code>koito</code></td>
    <td align="center" width="14%"><a href="docs/CHARACTERS.md"><img src="assets/illustrations/hinana-coding.webp?v=1a0fac2c1b8c" width="100" alt="市川雛菜"><br><sub>市川雛菜</sub></a><br><code>hinana</code></td>
    <td align="center" width="14%"><a href="docs/CHARACTERS.md"><img src="assets/illustrations/nichika-coding.webp?v=3dc0f0ec067d" width="100" alt="七草にちか"><br><sub>七草にちか</sub></a><br><code>nichika</code></td>
    <td align="center" width="14%"><a href="docs/CHARACTERS.md"><img src="assets/illustrations/mikoto-coding.webp?v=0a30c45b8a6e" width="100" alt="緋田美琴"><br><sub>緋田美琴</sub></a><br><code>mikoto</code></td>
    <td align="center" width="14%"><a href="docs/CHARACTERS.md"><img src="assets/illustrations/luca-coding.webp?v=8dcc9eb37772" width="100" alt="斑鳩ルカ"><br><sub>斑鳩ルカ</sub></a><br><code>luca</code></td>
    <td align="center" width="14%"><a href="docs/CHARACTERS.md"><img src="assets/illustrations/hana-coding.webp?v=0bc03c847511" width="100" alt="鈴木羽那"><br><sub>鈴木羽那</sub></a><br><code>hana</code></td>
    <td align="center" width="14%"><a href="docs/CHARACTERS.md"><img src="assets/illustrations/haruki-coding.webp?v=5c3127d8cde6" width="100" alt="郁田はるき"><br><sub>郁田はるき</sub></a><br><code>haruki</code></td>
  </tr>
</table>
<!-- CHARACTERS:END -->

## 你可以改什么

| 内容 | 配置位置 | 默认行为 |
| --- | --- | --- |
| 用户名、显示名、介绍、技能 | `config.json` | 账号和显示名自动识别；其他内容为通用示例 |
| 项目页列表 | `projects.json` | 选择最近推送的 4 个公开原创仓库；支持手动排序和文案 |
| 首页最新项目 | 自动获取 | 按默认分支最新 commit 排序；独立于项目列表，排除主页和当前构建仓库 |
| 人物立绘 | `config.json` → `character` | [28 位角色](docs/CHARACTERS.md)，默认羽那；`random` 每次构建随机选择 |
| 自定义立绘 | `config.json` → `illustration` | 可选透明 PNG/WebP 路径或 `null` 隐藏；优先于 `character` |
| 背景与统计时区 | `config.json` | 内置场景；UTC+8 |
| 自动更新频率 | `.github/workflows/shiny-refresh.yml` | 每日 16:17 UTC |

代码和内容都在自己的仓库里，不依赖作者的服务。生成结果带内容哈希，用于减少 GitHub 图片缓存未刷新的情况。

人物统一为职场 / Coding 主题，分别参考各角色官方原始形象生成。修改 `"character": "madoka"` 可固定圆香，修改为 `"character": "random"` 可在每次现有定时或手动构建时随机选择。也可直接在 **Run workflow → character** 下拉菜单选择，工作流会保存设置。GitHub 主页上的图片不会在访客刷新时重新抽取。

## 本地试用

需要 Python **3.12+**，macOS / Linux / Windows 均可。

```sh
git clone https://github.com/Gu-Haojia/shinycolors-profile-template.git
cd shinycolors-profile-template
python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows PowerShell：.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python build.py --demo
python -m http.server 4180 --bind 127.0.0.1
```

打开 `http://127.0.0.1:4180/preview.html`。`--demo` 完全离线，不需要 Token。用 `python build.py --demo --watch` 在修改配置后自动生成；浏览器刷新即可查看。真实数据、本地 Token 设置和缓存说明见[部署指南](docs/DEPLOYMENT.md)。

## 统计说明

- 首页「年提交」：GitHub API 返回的**滚动近一年 commit 贡献数**。
- 标注年份的贡献：该自然年的所有贡献，不只是 commit。
- 「本周」：配置时区下本周一至今天的日历贡献合计。
- 钻石与等级：历年可见贡献总数；等级是其平方根取整（最低 1）。属于展示用游戏化数值。
- Stars：公开非 fork 仓库之和；粉丝：Followers。更多字段和可见范围见[配置说明](docs/CONFIGURATION.md#数据口径)。

## 开发与素材许可

```sh
python -m unittest discover -s tests -v
```

生成器代码、测试和文档采用 [MIT](LICENSE)。**游戏图像、角色形象及其衍生立绘不在 MIT 授权范围内**，不代表它们可自由商用或再授权。字体与图标保留各自许可。使用默认视觉素材前请阅读 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)；也可替换为自己有权使用的素材。

本项目是非官方同人项目，与 Bandai Namco Entertainment 无隶属或背书关系。
