# 28 位 Coding 角色图库

统一职场 / Coding 主题，每位从对应官方原始形象独立生成，透明背景。默认 `hana` 是本批新版羽那。

## 选择方式

在 `config.json` 中设置，例如：

```json
"character": "madoka"
```

也支持日文姓名和清单中的中文别名。删除已有的 `illustration` 字段即可使用内置角色；该字段若存在，会继续覆盖角色选择。

- **随机模式**：`"character": "random"`，每次已有定时或手动构建时从 28 位中随机选一位，允许重复。配置保持 `random`；访客刷新 GitHub 主页不会重新抽取，不增加触发器。
- **GitHub 操作**：Actions → Shiny Refresh → Run workflow → character，选择角色名或 `random`。工作流会保存配置；`from-config` 保留当前设置。
- **本地试用**：`python build.py --demo --character madoka` 或 `--character random`，仅覆盖本次构建，不修改配置。
- **本地交互图库**：启动 `python -m http.server 4180 --bind 127.0.0.1`，打开 `http://127.0.0.1:4180/docs/gallery.html`，可预览、筛选和复制配置。
- **旧版羽那**：添加 `"illustration": "assets/illustrations/hana-coding.webp"`。新版文件为 `hana-coding-v2.webp`，旧图保留。

以下预览均为 AI 同人立绘，非官方服装或原图。[素材来源](../assets/illustrations/SOURCES.md) · [完整提示词](character-prompts.json)


## illumination STARS

| 櫻木真乃 | 風野灯織 | 八宮めぐる |
| --- | --- | --- |
| <img src="../assets/illustrations/mano-coding.webp" width="220" alt="櫻木真乃 Coding 立绘"> | <img src="../assets/illustrations/hiori-coding.webp" width="220" alt="風野灯織 Coding 立绘"> | <img src="../assets/illustrations/meguru-coding.webp" width="220" alt="八宮めぐる Coding 立绘"> |
| `mano` | `hiori` | `meguru` |


## L’Antica

| 月岡恋鐘 | 幽谷霧子 | 三峰結華 |
| --- | --- | --- |
| <img src="../assets/illustrations/kogane-coding.webp" width="220" alt="月岡恋鐘 Coding 立绘"> | <img src="../assets/illustrations/kiriko-coding.webp" width="220" alt="幽谷霧子 Coding 立绘"> | <img src="../assets/illustrations/yuika-coding.webp" width="220" alt="三峰結華 Coding 立绘"> |
| `kogane` | `kiriko` | `yuika` |

| 田中摩美々 | 白瀬咲耶 |
| --- | --- |
| <img src="../assets/illustrations/mamimi-coding.webp" width="220" alt="田中摩美々 Coding 立绘"> | <img src="../assets/illustrations/sakuya-coding.webp" width="220" alt="白瀬咲耶 Coding 立绘"> |
| `mamimi` | `sakuya` |


## 放課後クライマックスガールズ

| 小宮果穂 | 園田智代子 | 西城樹里 |
| --- | --- | --- |
| <img src="../assets/illustrations/kaho-coding.webp" width="220" alt="小宮果穂 Coding 立绘"> | <img src="../assets/illustrations/chiyoko-coding.webp" width="220" alt="園田智代子 Coding 立绘"> | <img src="../assets/illustrations/juri-coding.webp" width="220" alt="西城樹里 Coding 立绘"> |
| `kaho` | `chiyoko` | `juri` |

| 杜野凛世 | 有栖川夏葉 |
| --- | --- |
| <img src="../assets/illustrations/rinze-coding.webp" width="220" alt="杜野凛世 Coding 立绘"> | <img src="../assets/illustrations/natsuha-coding.webp" width="220" alt="有栖川夏葉 Coding 立绘"> |
| `rinze` | `natsuha` |


## ALSTROEMERIA

| 桑山千雪 | 大崎甘奈 | 大崎甜花 |
| --- | --- | --- |
| <img src="../assets/illustrations/chiyuki-coding.webp" width="220" alt="桑山千雪 Coding 立绘"> | <img src="../assets/illustrations/amana-coding.webp" width="220" alt="大崎甘奈 Coding 立绘"> | <img src="../assets/illustrations/tenka-coding.webp" width="220" alt="大崎甜花 Coding 立绘"> |
| `chiyuki` | `amana` | `tenka` |


## Straylight

| 芹沢あさひ | 黛冬優子 | 和泉愛依 |
| --- | --- | --- |
| <img src="../assets/illustrations/asahi-coding.webp" width="220" alt="芹沢あさひ Coding 立绘"> | <img src="../assets/illustrations/fuyuko-coding.webp" width="220" alt="黛冬優子 Coding 立绘"> | <img src="../assets/illustrations/mei-coding.webp" width="220" alt="和泉愛依 Coding 立绘"> |
| `asahi` | `fuyuko` | `mei` |


## noctchill

| 浅倉透 | 樋口円香 | 福丸小糸 |
| --- | --- | --- |
| <img src="../assets/illustrations/toru-coding.webp" width="220" alt="浅倉透 Coding 立绘"> | <img src="../assets/illustrations/madoka-coding.webp" width="220" alt="樋口円香 Coding 立绘"> | <img src="../assets/illustrations/koito-coding.webp" width="220" alt="福丸小糸 Coding 立绘"> |
| `toru` | `madoka` | `koito` |

| 市川雛菜 |
| --- |
| <img src="../assets/illustrations/hinana-coding.webp" width="220" alt="市川雛菜 Coding 立绘"> |
| `hinana` |


## SHHis

| 七草にちか | 緋田美琴 |
| --- | --- |
| <img src="../assets/illustrations/nichika-coding.webp" width="220" alt="七草にちか Coding 立绘"> | <img src="../assets/illustrations/mikoto-coding.webp" width="220" alt="緋田美琴 Coding 立绘"> |
| `nichika` | `mikoto` |


## CoMETIK

| 斑鳩ルカ | 鈴木羽那 | 郁田はるき |
| --- | --- | --- |
| <img src="../assets/illustrations/luca-coding.webp" width="220" alt="斑鳩ルカ Coding 立绘"> | <img src="../assets/illustrations/hana-coding-v2.webp" width="220" alt="鈴木羽那 Coding 立绘"> | <img src="../assets/illustrations/haruki-coding.webp" width="220" alt="郁田はるき Coding 立绘"> |
| `luca` | `hana` | `haruki` |

