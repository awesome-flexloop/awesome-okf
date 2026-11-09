---
type: concept
title: PPT 模板系统
description: 解析 9 套模板的三段式文件结构、index.json 注册协议，以及 build_page.py 的组装与四类校验。
tags: [wecom, wecom-unified, templates, ppt]
generated: { by: okf-wiki/0.2, at: 2026-11-09 }
status: stable
verified: { by: "process:seven-concepts-v", at: "2026-11-09" }
stale_after: 2027-11-09
sources:
  - resource: vendor/WecomTeam/wecom-unified/
  - resource: /references/facts.md
---

# PPT 模板系统

`assets/templates/` 是一套「离线设计系统」：它把版式、配色与文案骨架固化成本地文件，让页面装配不依赖模型的即兴排版。53 个文件由 9 套模板、11 个渲染壳、32 个内容页、1 个注册表组成（F-094）。理解这套系统，关键不是记住 9 个名字，而是掌握「注册表选型 → 三段式读取 → 装配与校验」这条固定路径。

## 一、9 套模板与文件构成

| slug | `.jsx` 数 | `.slide` 页数 | 证据 |
|---|---|---|---|
| `broadside` | 1 | 4 | F-095、F-096 |
| `cartesian` | 1 | 3 | F-095、F-096 |
| `cobalt-grid` | 1 | 3 | F-095、F-096 |
| `editorial-forest` | 1 | 4 | F-095、F-096 |
| `emerald-editorial` | 1 | 4 | F-095、F-096 |
| `grove` | 2 | 3 | F-095、F-096 |
| `long-table` | 1 | 4 | F-095、F-096 |
| `sakura-chroma` | 1 | 4 | F-095、F-096 |
| `signal` | 2 | 3 | F-095、F-096 |
| 合计 | 11 | 32 | F-094 |

页数为 3 的 4 套是 `cartesian`、`cobalt-grid`、`grove`、`signal`；页数为 4 的 5 套是 `broadside`、`editorial-forest`、`emerald-editorial`、`long-table`、`sakura-chroma`（F-096）。`grove` 与 `signal` 各有 2 个 `.jsx`，其余 7 套各 1 个，这说明「渲染壳」并非严格一模板一文件——同一套设计可以有多个壳变体（F-095）。

## 二、三段式结构

每套模板目录都由三类文件构成，职责互不重叠（F-095）：

| 文件 | 位置 | 职责 | 使用方式 |
|---|---|---|---|
| `DESIGN.preset.md` | 套装根 | 设计契约：色彩、字体、间距、版式约束 | 选型后**必须整篇读取** |
| `shell/*.jsx` | `shell/` | 渲染壳：页眉、页脚、页码、引导问题的固定骨架 | 复制为工作副本，不直接改 |
| `slides/*.slide` | `slides/` | 内容页实例：各类页型的 body 与 vars 示例 | 作为填值样例参照 |

这套划分把「不可变的结构」与「可变的内容」彻底分开：`shell` 提供占位符与版面定位，`slides` 只示范某个页型如何填。`build_page.py` 的 `build` 正是据此工作——shell 里的 `〔标题〕`、`〔B区内容〕` 被 vars 替换，值按原样插入（F-070）。因此模板的视觉一致性不靠模型的审美，而靠「所有页面共用同一个 shell」这一结构约束。

需要提醒的是，9 套模板是「最小骨架」而非成品演示稿：每套只有 3～4 页，覆盖封面、章节页与少数内容页型，目的是提供可复用的版式约束，而不是直接交付。实际文档应在选定模板后按需扩展页数，并逐页通过 check、contrast、fit 校验；把模板原样当作成品，往往只会得到页数不足、内容空洞的骨架稿。

## 三、index.json 注册协议

`index.json` 是选型的唯一入口，顶层只有 `usage`、`gate`、`sets` 三个键（F-097）。

| 键 | 内容 | 语义 | 证据 |
|---|---|---|---|
| `usage` | `shape`、`select`、`gate`、`naming`、`then` | 使用协议：选择形状、选型、门禁、命名与后续读取 | F-098 |
| `gate` | `id=government`、`name=政务`、`sets=[broadside, long-table]`、`contract=../government-contract.md` | 命中政务条件时限定可选套装 | F-100 |
| `sets` | 每项含 `slug`、`name`、`scenes_zh`、`tags`、`gate`、`best_for_zh`、`avoid_for_zh`、`preset`、`shell`、`slides` | 9 套模板的元数据 | F-101 |

两条使用协议值得单独记住。第一，**`name` 是给用户看的风格名，`slug` 只是目录名**，对用户表述时不出现 slug（F-099）。第二，用户选定风格后，只读取该套的 `DESIGN.preset.md`、`shell/`、`slides/` 三处，路径照抄 `sets` 项中的 `preset`、`shell`、`slides` 字段，不要自行拼接或跨套取材（F-099）。这条约束同时限制了上下文开销与风格串味。

`gate` 的设计是「条件收敛」：当请求主体是党政机关、事业单位、国企央企、街道社区等，或文体属于公文时，可选集合被收窄为 `broadside` 与 `long-table`，并指向 `../government-contract.md`（F-100）。门禁不是推荐，而是**排除其它 7 套**。

## 四、选型流程

1. **过门禁**：先看 `gate.trigger_zh` 是否命中。命中则只在 `sets=[broadside, long-table]` 中选，并读取政务契约。
2. **对场景**：未命中门禁时，按 `scenes_zh`、`tags.formality`、`tags.density`、`tags.tone` 与 `best_for_zh`/`avoid_for_zh` 匹配。
3. **报名字**：向用户呈现 `name`（如首项 `sakura-chroma` 的 `name` 为「活动策划」），不报 slug（F-101、F-099）。
4. **读三处**：只读目标套装的 preset、shell、slides（F-099）。

`sets` 首项是 `slug=sakura-chroma`、`name=活动策划`、`gate=null`，可作为字段完整度的参照样例（F-101）。

## 五、build_page.py 的组装与校验

组装侧有两个入口。`init --set <slug>` 把目标套装的 shells、模板页与 preset 复制到当前工作目录，并按 `--map colors.json` 重新着色；`template <user.pptx>` 则从用户 PPT 反推 shell，文档创建后再用 `template --docid <docid>` 上传模板素材、生成 `tpl_urls.json`（`build_page.py:4-5`、`:52-59`）。

校验侧有四个子命令，各自回答一个不同的问题：

| 子命令 | 回答的问题 | 失败含义 | 证据 |
|---|---|---|---|
| `check` | 每页是否仍是同一个 shell、只填了占位符 | 页面偏离母版或被手工改写 | `build_page.py:20`（源码） |
| `contrast` | 文字与其所在背景的对比度是否足够 | 可读性不足 | `build_page.py:13`（源码） |
| `fit` | 文字是否溢出文本框、是否压到其它文字、画布是否 1280×720 | 版面溢出或尺寸错误 | `build_page.py:14`（源码） |
| `images` | 页面里图片的声明尺寸与真实宽高比是否一致 | 图片会被压扁 | `build_page.py:16`（源码） |

`build` 自身还有一道图片闸门：页面含 `<Image>` 时必须提供 `--manifest images.json`，且真实尺寸校验通过才写文件，否则提示用 `imgfit --slot … --actual … --src …` 生成正确的 Image JSX（`build_page.py:60-63`）。`buildall` 把这些步骤串成一条命令：先构建每个 `NN_body.jsx`，再跑 contrast 与 images（`build_page.py:6`）。

一个交付前的实用顺序是：`init` → 逐页 `build` → `check` → `contrast` → `fit` → `images`，最后 `buildall` 复跑一次作为回归。任一环节失败都应在本地修复后重跑，而不是把未通过校验的页面直接上传——校验的价值就在于把版面问题挡在发布之前。

## 延伸阅读

- [脚本工具链](04-scripts-toolchain.md)：`build_page.py` 的完整子命令与依赖。
- [references 分类学](03-references-taxonomy.md)：pptx 组件文档与模板元素的关系。
- [sheet 转 PPT 示例](../examples/02-sheet-to-ppt-pipeline.md)：从数据到在线 PPT 的完整链路。
- [套件定位与依赖](00-overview.md)：模板资产在 193 个文件中的位置。