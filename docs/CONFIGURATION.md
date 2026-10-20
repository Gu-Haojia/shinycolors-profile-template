# 配置说明

所有文件是 UTF-8 JSON，不支持注释或末尾多余的逗号。修改后提交到 `main`，工作流会重新生成；不要手改 `assets/shinycolors.svg` 或生成的 `PROFILE.md`。

## 个人配置

`config.json`：

| 字段 | 说明 |
| --- | --- |
| `github` | `"auto"` 使用 Actions 仓库所有者；也可填写个人 GitHub 用户名 |
| `nickname` | `"auto"` / `null` 使用 GitHub 显示名，可直接填写自己的名字 |
| `card_title` | 制作人档案小标题 |
| `tags` | 简短标签数组，建议 2～3 项 |
| `greeting` | 首页对话，最多 2 行 |
| `tagline` | 右侧大标语，最多 3 行 |
| `produce_label` | Produce 按钮上方短标题 |
| `timezone_offset` | 显示时区相对 UTC 的小时偏移，-12～14，可用 5.5 等小数；不自动适应夏令时 |
| `backgrounds.home` / `.produce` | 内置背景编号 `"001"`、`"003"` 或 `"035"` |
| `character` | [28 位内置角色](CHARACTERS.md)的 ID / 姓名，默认 `hana`；`random` 每次构建随机选择 |
| `illustration` | 可选，相对仓库根目录的 PNG/WebP 路径；`null` 隐藏人物。存在时优先于 `character` |
| `skills` | 最多 4 组技能，每组 `name`、`param`、`icons`，可选 `tags` |
| `about_title` / `about` | 关于页标题和说明；方括号 `[文字]` 表示强调文字 |
| `speaks` | 关于页底部语言文字，可留空 |
| `projects_file` | 项目配置文件，相对 `config.json`，默认 `projects.json` |
| `languages.exclude` | 不计入语言排名的语言名数组 |
| `languages.size_weight` / `.count_weight` | 语言评分指数，默认各 0.5；评分为代码字节数的 size_weight 次方 × 仓库数的 count_weight 次方 |

技能的 `param` 是 `Vo`、`Da`、`Vi`、`Me` 之一，决定徽章与颜色。图标使用内置名称，运行 `python build.py --list-icons` 查看。`skills.icons` 只接受技术图标；`about.icon` 也接受统计图标。

默认个人介绍与技能是可替换示例，**并非从 GitHub 自动推断**。界面当前以简体中文为主，文案可用中文、日文或拉丁字母；未包含字形的语言可能需要换字体。

## 项目列表

自动模式，按公开非 fork 仓库最近推送时间选取前 4 个：

```json
{
  "items": null,
  "limit": 4
}
```

`limit` 为 1～20。自动排除与账号同名的主页仓库，以及 Actions 当前构建仓库。

手动模式，按数组顺序展示：

```json
{
  "items": [
    {
      "repo": "your-repository",
      "title": "我的项目",
      "description": null,
      "language": null,
      "color": "blue",
      "show_on_projects": true
    }
  ]
}
```

可以复制 [`examples/projects.manual.json`](../examples/projects.manual.json)。

- `repo`：当前账号下的仓库名，不填写完整 URL 或 `owner/repo`。
- `title`：展示名称；省略 / `null` 时使用仓库名。
- `description`、`language`：省略 / `null` 自动取 GitHub；填文字则覆盖。简介填 `""` 表示空白。
- `color`：`blue`、`yellow`、`orange`、`pink`，省略则轮换。
- `show_on_projects`：默认 `true`，`false` 隐藏该条。
- `items: []`：明确隐藏全部项目卡；不会自动补回。
- 手动列表可超过 4 项，布局自动增加行数。未公开或不存在的仓库不能获取统计，Stars 显示 `—`。

**首页最新项目独立于 items**：读取公开原创仓库默认分支最新 commit，按实际提交时间选最新一项，显示时间与 NEW 角标；不展示 commit 摘要、短 SHA 或语言标记。没有有效提交时不造假项目卡。

## 替换视觉素材

选择内置角色只需设置 `"character": "hana"`、`"character": "樋口円香"` 等；完整 ID 和预览见[角色图库](CHARACTERS.md)。`"character": "random"` 在每次构建时从 28 位角色中等概率抽取一位，允许连续两次相同。随机结果内嵌到 SVG，配置保持 `random`，访问或刷新 GitHub 主页不会重新抽取，也不增加更新触发器。

Actions → Shiny Refresh → Run workflow 的 `character` 菜单可保存固定角色或 `random`，选 `from-config` 保留原设置。明确选择时会移除旧的 `illustration` 覆盖项。

自定义立绘建议使用透明背景、2:3 画布，放进 `assets/illustrations/`，添加 `illustration` 指向新文件。构建会等比缩放、底部对齐到 1024×1536 的透明画布；当前场景构图针对桌前角色设计，其他姿势可能需要调整 `character_artwork()` 中的位置。使用内置角色或随机模式前，删除已有的 `illustration` 字段；旧字段仍优先，便于已有配置继续使用。

`illustration: null` 仅隐藏人物，场景和游戏图标仍然存在。背景与道具可替换 `assets/game/` 同名文件，尺寸变化时同步修改 `index.json`。`bg_001` 和 `bg_003` 的渲染优先使用对应 `_hd` 文件。字体文件与图标路径分别在 `assets/fonts/` 和 `data/icons.json`。

包含原生游戏素材的默认主题不等于免费素材包。素材的来源和授权边界见 [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md)。

## 数据口径

| 页面数值 | 实际含义 |
| --- | --- |
| 金币 / Stars | 公开非 fork 仓库 Stars 总数 |
| 钻石 | 各自然年可见日历贡献之和，包含提交、PR、Issue 等 GitHub 计入的活动 |
| 粉丝 | Followers |
| Lv. | 历年贡献平方根取整，最低 1；下一级阈值为 `(Lv + 1)²` |
| 首页年提交 | GitHub 默认 contributionsCollection 的滚动近一年 commit 贡献数 |
| 首页 PR / Issue | GitHub 查询返回的已创建 PR / Issue 总数，不限于近一年 |
| 仓库 | 账号公开仓库数，包含 fork |
| `YYYY 年贡献` | 配置时区下当年 1 月 1 日至抓取时刻的日历贡献总数 |
| 本周 | 配置时区下本周一至今天的日历贡献合计 |
| 近 30 天 / 日历 / 连续贡献 | GitHub 返回的逐日贡献数据；今天尚未贡献不立即视为断签 |
| 确认流行 / Vo・Da・Vi・Me | 按配置权重计算的语言排名与占比，并非 GitHub 官方统计指标 |
| 正在培育 | 最近公开推送事件对应的原创仓库，事件不可用时用最近推送时间 |

工作流默认读取公开仓库和 GitHub API 当前可见的贡献；不承诺覆盖私有活动或未关联到账号的 commit。日历的逐日归属由 GitHub 提供，显示时区不会重新计算每条提交属于哪天。Stars、语言统计与贡献来源范围不同；贡献总数也不等于 `git log` 中所有 commit 的总数。

## 构建命令与输出

```sh
python build.py --demo                     # 离线虚构示例
python build.py --username alice           # 真实数据；需环境变量 GITHUB_TOKEN
python build.py --username alice --offline # 使用 alice 的缓存
python build.py --demo --watch             # 监听配置和立绘修改
python build.py --list-characters          # 查看 28 位角色与 random
python build.py --demo --character madoka  # 单次试用；不修改 config.json
python build.py --demo --character random  # 单次随机；watch 时只在文件变化后重新抽取
python build.py --strict-refresh           # 抓取失败即退出，Actions 使用
python build.py --readme-mode preserve     # 保留 README，仅更新 SHINY 标记区域
python build.py --readme-mode profile      # 将 README 完整替换为生成的主页
```

默认 `--readme-mode auto` 在 Actions 的同名个人仓库中使用 `profile`，普通仓库和本地已有文档中使用 `preserve`。本地已生成的主页 README 会继续更新。

输出 `assets/shinycolors.svg`、`PROFILE.md`、`README.md` 与本地 `preview.html`。真实抓取另外写 `data/stats.json`，缓存绑定用户名；演示不会写入缓存。README 图片 URL 带内容哈希；本地预览文件不提交。
