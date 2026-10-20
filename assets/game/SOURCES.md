# 素材来源

- `bg_*.webp` 和培育画面的桌面道具（台历、马克杯、资料、平板）、气泡、Produce / 任务按钮、标题条、等级条、叶月等：《偶像大师 闪耀色彩》页游原生素材，© Bandai Namco Entertainment Inc.
- 其中带中文字样的部件来自汉化项目 [ShinyGroup/SCTranslationData](https://github.com/ShinyGroup/SCTranslationData) 的汉化图集。
- `coin.webp`、`jewel.webp`：从游戏商店的金币 / 羽石图标（148px）里抠掉了道具框。
- `row_yellow.webp` 在原图基础上抹掉了一条虚线。
- 页签、圆形菜单按钮、粉丝 / 奖杯 / 连续图标、Vo/Da/Vi/Me 徽章、技能分类条、项目卡、NEW 角标不在这里：它们由 `build.py` 照游戏样式用矢量重绘。
- 这些素材只用于个人主页的同人展示，版权归原权利人所有。

字体 `assets/fonts/ResourceHanRoundedCN-VF.woff2`：源样圆体（Resource Han Rounded），SIL Open Font License 1.1，见同目录 `OFL.txt`。

## 2026-10-19 清晰度与 UI 修正

- `bg_001_hd.webp`（1671×941）、`bg_003_hd.webp`（1672×941）：以上原生背景经内置 image_gen 编辑生成的清晰度增强版，再编码为 WebP。保留原始背景。增强版不是官方高清原图，微小纹理与标识可能有重建差异。
- `papers_plain.webp`：从 [原生汉化培育图集](https://github.com/ShinyGroup/SCTranslationData/blob/master/data/image/produce_top_parts.png) 的 `(783,543)-(1080,636)` 无损提取的 297×93 资料图；“回顾”标题由 SVG 单独绘制。
- `build.py` 现在用矢量绘制气泡、底部操作标题、平板与排行、首页 Produce/任务按钮、等级条、页标题框、黄色统计行；原有对应位图留存，但不再内嵌进输出。
- 构图、背景放大与移动参数保持原样。渲染配置见 [配置说明](../../docs/CONFIGURATION.md)，素材授权范围见 [第三方声明](../../THIRD_PARTY_NOTICES.md)。
