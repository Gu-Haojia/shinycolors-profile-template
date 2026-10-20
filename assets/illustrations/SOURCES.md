# 立绘来源

28 位 Coding / 职场服装同人立绘：2026-10-20 通过 OpenAI 内置 imagegen 逐位生成，每位以其在[官方角色网站](https://shinycolors.idolmaster-official.jp/)的原始形象为参考，没有以其他角色或先前的 AI 生成图作为参考叠加生成。保留各角色的发型、瞳色和标志配饰，统一使用现代职场穿搭与笔记本电脑构图。

- 文件、姓名与官方参考 URL：[角色清单](../../data/characters.json)。
- 每张完整提示词与生成方式：[生成记录](../../docs/character-prompts.json)。
- 规格：1024×1536，透明 RGBA PNG 无损导出为 WebP，保留 alpha；没有额外后期重绘。
- `hana-coding-v2.webp` 是本批重新生成的羽那，`character: "hana"` 使用此版本。
- `hana-coding.webp` 保留此前经过头发清理的旧版羽那；添加 `"illustration": "assets/illustrations/hana-coding.webp"` 可继续使用。

原始角色相关权利归原权利人所有。本素材不在生成器代码的 MIT 授权范围内；详见 [第三方声明](../../THIRD_PARTY_NOTICES.md)。

在 `config.json` 中通过 `character` 选择角色或 `random`；添加 `illustration` 可优先使用自己的透明 PNG/WebP，也可设为 `null` 隐藏人物。官方原始参考图片、生成中间 PNG、个人头像与个人统计不包含在模板仓库中。
