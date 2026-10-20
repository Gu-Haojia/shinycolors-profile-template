# 部署指南

## 新建个人主页

1. 在上游仓库点击 **Use this template → Create a new repository**，Owner 选择自己的个人账号。
2. 仓库名填写自己的 GitHub 用户名，选择 **Public**，保留默认分支 `main`。
3. 进入 **Actions → Shiny Refresh → Run workflow**，选择 `main`，运行一次。
4. 成功后会看到机器人提交，包含 `README.md`、`PROFILE.md`、`assets/shinycolors.svg` 与 `data/stats.json`。同名仓库的 README 会显示在个人页。

默认 `github: "auto"` 从 `GITHUB_REPOSITORY_OWNER` 读取账号，`nickname: "auto"` 使用 GitHub 显示名（为空时用用户名）。所有者是组织时，应在 `config.json` 的 `github` 填入一个个人账号；当前统计查询面向 GitHub 用户。

工作流声明了 `contents: write`，通常无需额外设置。若报 `403` 或 `Permission denied to github-actions[bot]`，检查 **Settings → Actions → General → Workflow permissions**，以及组织策略和分支保护是否允许工作流向默认分支写入。该流程不需要额外 PAT；不要把 Token 写进配置或提交到仓库。

模板仓库首次创建时是否立即运行取决于 GitHub 事件，手动执行一次最稳妥。

## 已有个人主页仓库

先保存现有 README 和工作流。在现有同名仓库中添加本模板的 `build.py`、`requirements.txt`、`config.json`、`projects.json`、`assets/`、`data/icons.json`、`tests/`、`docs/`、`examples/`、许可说明及 `.github/workflows/shiny-refresh.yml`，再运行工作流。不要把别人的 `data/stats.json` 当作自己的统计缓存。

**默认会把同名仓库的 README 改为生成的主页。** 想保留自己的文字，在工作流构建命令后加 `--readme-mode preserve`，并在 README 需要插入主页的地方放：

```html
<!-- SHINY:START -->
<!-- SHINY:END -->
```

构建只更新标记之间的内容。没有标记时在文末追加；标记不完整则报错并保留原文件。

## 使用普通仓库

也可以创建 `alice/my-profile` 之类的普通公开仓库。它仍自动抓取 `alice` 的数据，但会保留模板 README 的文档，只更新预览区域；可在仓库中查看 `PROFILE.md`。

如需在另一个仓库的 README 引用生成图，将 `PROFILE.md` 中图片的相对路径改为你的仓库 raw URL，例如：

```html
<img src="https://raw.githubusercontent.com/OWNER/REPOSITORY/main/assets/shinycolors.svg" width="100%" alt="我的主页">
```

跨仓库手写链接不会自动带上新哈希，可能受到 GitHub 图片缓存影响。直接在同名个人仓库中生成是最省事的方式。

## 本地读取真实数据

安装 Python 3.12+ 与依赖。将 `GITHUB_TOKEN` 作为当前进程的环境变量提供；如果已登录 GitHub CLI，可使用：

```sh
# macOS / Linux；Token 只通过环境变量传入，不写入配置文件
GITHUB_TOKEN="$(gh auth token)" python build.py --username YOUR_USERNAME --strict-refresh
```

Windows PowerShell：

```powershell
$env:GITHUB_TOKEN = gh auth token
python build.py --username YOUR_USERNAME --strict-refresh
Remove-Item Env:GITHUB_TOKEN
```

多账号用户先确认 `gh` 当前登录的是期望的账号。只需要读取公开数据，不必给本地 Token 增加私有仓库访问权限。生成后：

```sh
python build.py --username YOUR_USERNAME --offline
python build.py --username YOUR_USERNAME --offline --watch
```

缓存与账号绑定；换账号需要重新联网抓取。本地克隆默认 `auto` 无法从 Actions 环境获得账号，必须传 `--username` 或填写配置。离线演示用 `--demo`，不会读写真实缓存，也不会联网。

## 自动更新

工作流现有三种入口：每日定时、手动运行、配置/源码推送。默认 `17 16 * * *` 是 UTC 16:17，也就是北京时间次日 00:17；`timezone_offset` 只控制显示与统计分组，不改变 cron。

上游 `Gu-Haojia/shinycolors-profile-template` 的定时事件会跳过整个构建任务，不运行测试、抓取或提交，也不占用 runner；Actions 中可能仍显示已跳过的记录。上游的手动运行和配置/源码推送正常执行。从模板创建的其他仓库仍每日更新，无需修改条件。`--demo` 演示图底部的更新时间留空，不显示“数据每天自动更新”；真实个人主页继续显示实际更新日期。

其他仓库的提交不会额外触发更新，会在下一次运行时读取默认分支最新提交。修改 `projects.json` 会触发构建；如果改了 `projects_file` 文件名或把自定义立绘放在 `assets/illustrations/` 之外，也要把新路径加进工作流 `push.paths`，或手动运行。

Actions 定时运行可能延迟。GitHub 可能在公开仓库长期无活动时停用定时工作流，届时进入 Actions 重新启用。详情见 [GitHub schedule 文档](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)。

## 常见问题

- **仍显示 Your Name / 演示项目**：确认在自己的新仓库里运行了 Shiny Refresh，检查最新运行和机器人提交。上游模板刻意保留虚构演示。
- **刷新失败**：查看 Actions 中 Build profile 的实际错误。严格模式会让运行失败，保留已发布页面，不会用零值伪装成功。
- **本地没 Token**：用 `--demo`；真实贡献日历需要 GitHub GraphQL 认证，生成器会明确报错。
- **提交了配置但没更新**：检查默认分支、工作流路径过滤、最新 Actions 是否成功；不要手改生成的 SVG。
- **GitHub 缓存**：README 的图片 URL 自动包含 SVG 内容哈希。确认机器人提交中的 URL 已变化，再强制刷新。离线预览刷新 `preview.html` 即可；该页面无 Service Worker。
- **动画/按钮**：输出是一张 SVG 图片，动态效果由 SVG SMIL 播放。图内按钮是视觉元素，不提供网页跳转或交互。具体动画支持由浏览器和 GitHub 图片展示方式决定。
- **贡献与 GitHub 页面不完全一致**：参见[数据口径](CONFIGURATION.md#数据口径)，尤其是提交贡献与所有贡献、自然年与近一年、Token 可见范围。

参考：[GitHub 个人主页 README](https://docs.github.com/en/account-and-profile/how-tos/profile-customization/managing-your-profile-readme)、[从模板创建仓库](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-repository-from-a-template)、[GITHUB_TOKEN](https://docs.github.com/en/actions/tutorials/authenticate-with-github_token)。
