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
<p align="center"><img src="assets/shinycolors.svg?v=7a8330515176" width="100%" alt="Your Name 的闪耀色彩风格主页 · Lv.35 · 连续贡献 4 天"/></p>
<!-- SHINY:END -->

</details>

## 你可以改什么

| 内容 | 配置位置 | 默认行为 |
| --- | --- | --- |
| 用户名、显示名、介绍、技能 | `config.json` | 账号和显示名自动识别；其他内容为通用示例 |
| 项目页列表 | `projects.json` | 选择最近推送的 4 个公开原创仓库；支持手动排序和文案 |
| 首页最新项目 | 自动获取 | 按默认分支最新 commit 排序；独立于项目列表，排除主页和当前构建仓库 |
| 人物立绘 | `config.json` → `character` | [28 位角色](docs/CHARACTERS.md)，默认新版羽那；`random` 每次构建随机选择 |
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
