---
okf_version: "0.2"
type: Reference
title: "huashu-art-motion 文章事实清单（信源登记）"
description: "微信公众号「开源星探」推介文的 F 编号事实登记与 GitHub 一手信源交叉核验状态（F-001~F-054）"
tags: [huashu-art-motion, article-source, fact-registry, blog-article, art-animation]
generated:
  by: "wechat-public-okf:R"
  at: "2026-10-10T12:30:00+08:00"
status: stable
stale_after: 2027-01-31
sources:
  - id: wechat
    url: https://mp.weixin.qq.com/s/BbsIpq82oAq7RPusw_jHXA
  - id: github-repo
    url: https://github.com/alchaincyf/huashu-art-motion
  - id: github-readme
    url: https://raw.githubusercontent.com/alchaincyf/huashu-art-motion/main/README.md
---

# 文章事实清单（article-source）

> 本文件是 F 编号事实的信源登记（source-manifest + facts 合体）。事实采集时间 2026-10-10。
> 类型：O=客观事实，V=作者/执行者观点，S=厂商/作者自述。核验：✅ 一手一致 ｜ ⚠️ 口径/时效差异 ｜ ➖ 无需外部核验 ｜ ❌ 失实。
> 信源：微信公众号「开源星探」推介文（次要信源，转述花叔项目）叠加 GitHub 官方 README（一手信源）。F-001~F-031 出自文章，F-032~F-054 为 GitHub 官方核验补充。
> **关键勘误已在 F-007/F-008 登记**：文章标题"1.3K Star 一天收获"与 GitHub 实测 **41 stars** 严重不符；"8 种解说语法"与官方 **9 种** 不一致。

## A. 文章与项目元信息（F-001 ~ F-004）

| F编号 | 类型 | 事实 | 核验 |
|-------|------|------|------|
| F-001 | O | 文章标题《开源一天就收获 1.3K Star！花叔用 35 种艺术风格做了一支会动的动画 Skill！》 | ➖ |
| F-002 | O | 公众号「开源星探」/原创，2026-10-07 23:03 发布（页脚 ¥ 例标注"791篇原创内容"，公众号简介"专注分享GitHub上优质开源项目"） | ➖ |
| F-003 | O | 推介项目 huashu-art-motion，作者花叔（Huashu），GitHub 账号 alchaincyf | ✅ F-032/F-053 |
| F-004 | O | 文章项目地址 https://github.com/alchaincyf/huashu-art-motion | ✅ F-032 |

## B. 项目背景与定位（F-005 ~ F-012）

| F编号 | 类型 | 事实 | 核验 |
|-------|------|------|------|
| F-005 | O | 花叔是独立开发者、GitHub 万星项目创作者；此前有更出名的项目 huashu-design（在 Claude Code/Cursor 等 coding agent 里一句话生成 App 原型、PPT、时间轴动画） | ⚠️ "万星"待核（F-046） |
| F-006 | O | huashu-art-motion 聚焦「用代码让艺术风格动起来」：非 AI 生图，而是纯代码绘制——星星位置用数学公式算、笔触粗细与颜色用参数控制、画面用代码一层层叠出 | ✅ F-036/F-049 |
| F-007 | ⚠️ | 文章标题声称「开源一天就收获 1.3K Star」 | ❌ F-034：GitHub 实测仅 **41 stars**，与 1.3K 严重不符（动态数，见核验） |
| F-008 | O | 项目含 35 种艺术风格配方卡（岩洞壁画、埃及壁画、莫奈、梵高、克林姆特、包豪斯、Kirby 漫画、8-bit、蒸汽波、新海诚等），每种配可运行 Canvas 场景+渲染器+签名转场 | ✅ F-039/F-042 |
| F-009 | O | 配方卡是「可执行的工程文档」：写明参数(颜色/笔触/画布比例)、母题动作、签名转场、当前短板 | ✅ F-040 |
| F-010 | O | 场景代码在 `scripts/engine/scenes/`，直接改就能跑 | ✅ F-040/F-043 |
| F-011 | V | 文章评价：skill 里记的不只是代码，还有哪些做法被证明有效、每种风格的坑和短板、签名转场该怎么写 | ✅ F-047 |
| F-012 | O | 花叔派 4 组只读该 skill 的 agent 去做它没见过的 20 种新风格，把各自造的轮子收成统一库 | ✅ F-041 |

## C. 解说动画语法与参数化片段（F-013 ~ F-021）

| F编号 | 类型 | 事实 | 核验 |
|-------|------|------|------|
| F-013 | ⚠️ | 文章正文提"8 种 YouTube 解说动画语法 / 8 种参数化片段"（衔接处） | ⚠️ F-037：官方口径为 **9 种解说语法**（8 种附示范片+第9种讲解员式）+ **8 种参数化片段**；文章衔接处把语法数写成 8 有误，正文宜按 9 表述 |
| F-014 | O | 已实现 9 种解说语法：Kurzgesagt / Vox / 白板动画 / 3Blue1Brown / Storytime / 动态文字 / 发布会UI / 财经图表 / 讲解员式财经科普 | ✅ F-037 |
| F-015 | O | Kurzgesagt：扁平无描边、尺度穿行（地球缩到星系、DNA 放大到细胞） | ✅ F-037 |
| F-016 | O | Vox：剪报、红线、荧光笔——新闻截图/数据图表/手绘红线拼贴的信息密度感 | ✅ F-037 |
| F-017 | O | 白板动画：笔尖揭开线稿，跟着口播一步步把图画出来 | ✅ F-037 |
| F-018 | O | 3Blue1Brown：对象形变成下一个，用几何变换做视觉隐喻 | ✅ F-037 |
| F-019 | O | 前 8 种都有示范片和参数化片段：给 JSON spec 就能导出一段时长精确到帧的动画（横屏、竖屏、透明底） | ✅ F-037/F-050 |
| F-020 | O | 9 种参数化片段中的财经图表：先坐标轴、后数据、只标一件事 | ✅ F-037 |
| F-021 | O | 8 种可参数化动画片段可作「动画积木」；最有意思的是「长卷穿越片骨架」 | ✅ F-038 |

## D. 长卷穿越片与《花叔穿越名画》（F-022 ~ F-027）

| F编号 | 类型 | 事实 | 核验 |
|-------|------|------|------|
| F-022 | O | 长卷穿越片骨架：每个画风世界是单独段文件；主角一路往右走；跨边界时画风自动切换；镜头只进不退，保持向前节奏 | ✅ F-038/F-050 |
| F-023 | O | 骨架自带 3 段示范：埃及壁画 → 莫奈《日本桥》→ 8-bit 像素 | ✅ F-051 |
| F-024 | O | 花叔的作品《花叔穿越名画》：23 种画风、2分08秒，卡通形象从洞穴一路走到 2026 | ✅ F-041/F-051 |
| F-025 | V | 文章称「这套东西已经不只是一个 skill，更像是一个动画工程的脚手架」 | ➖（观点） |
| F-026 | O | 累计产出：4 组 agent 的 20 种新风格 + 8 种解说语法 + 最后接入花叔自己口播视频管线 | ⚠️ 8→9 见 F-013/F-037 |
| F-027 | O | 项目「5 Parts + Conclusion」篇章结构（PART 01 把艺术风格写成会动的画 / 02 核心亮点 / 03 功能特性 / 04 快速上手 / 写在最后） | ➖ |

## E. 工程实践特性（F-028 ~ F-036）

| F编号 | 类型 | 事实 | 核验 |
|-------|------|------|------|
| F-028 | O | 拆解脚本 `breakdown.py`：把参考动画输出为转场标记、节拍网格(24/30fps、每几秒一拍)、运动热图 | ✅ F-044/F-052 |
| F-029 | O | QA 脚本 `qa.py`：五维度数字验收——稳定性(同一 spec 渲两次帧差异)、效率(每帧渲染时间+CPU)、动感、流畅度、文字框景 | ✅ F-044/F-052 |
| F-030 | O | 数字验收后派一个「没参与制作」的 agent 只看成片挑问题（类代码 review 但对象是动画） | ✅ F-044 |
| F-031 | O | 画面不完全是纯 Canvas：场景/转场/运动用代码完成；人交给生图模型出帧，代码负责帧间过渡、换帧节奏、材质合成 | ✅ F-049/F-052 |
| F-032 | O | 配乐纯代码合成：`scripts/audio/` 模板支持 BPM 网格对齐、动机换乐器、结尾音效序列（水墨「唰」声、像素「boop」声） | ✅ F-050 |
| F-033 | O | 安装三依赖：uv（Python 包管理器）、ffmpeg、Playwright Chromium | ✅ F-050 |
| F-034 | O | 安装命令 `npx skills add alchaincyf/huashu-art-motion` | ✅ F-050 |
| F-035 | ⚠️ | 文章提醒陷阱：skill 不只 SKILL.md 单文件，references/assets/scripts/demos 四子目录有 99 处被引用配方/脚本/素材；skills CLI ≤1.5.15 只同步 SKILL.md 单文件导致缺依赖 | ⚠️ F-050/F-053：目录确为 references/assets/scripts，`demos/` 是否独立顶层目录存疑（README 树显示 scripts/engine/demos/）；"99处"为文章口径，未在官方独立核实 |
| F-036 | O | 试渲梵高《星月夜》静止帧命令：`uv run --with playwright python scripts/engine/render.py --solo 09_postimp --stills 0.3 --out 试渲` | ✅ F-050 |

## F. GitHub 官方核验补充（F-037 ~ F-054，2026-10-10 采集 GitHub README/仓库页）

| F编号 | 类型 | 事实 | 核验 |
|-------|------|------|------|
| F-037 | O | 官方 README 副标题：`35种艺术风格 · 9种解说语法 · 8种参数化片段 · 口播整片参考代码` | ✅ |
| F-038 | O | 9 种语法附 8 种示范片与参数化片段；第 9 种「讲解员式财经科普」提供语法卡+需自备角色的整片代码快照 | ✅ |
| F-039 | O | 35 张风格配方卡位于 `references/风格配方/`；35 个场景代码位于 `scripts/engine/scenes/` | ✅ |
| F-040 | O | 配方卡结构（官方"里面有什么"表）：参数、母题动作、签名转场、当前短板 | ✅ |
| F-041 | O | 背景故事（官方）：2026-10 初在 X 看到 Tak（@cherry_mx_reds）的 15 秒《Art History Speedrun》，让 Claude 复刻并积累经验；后派 4 组只读 agent 做 20 种新风格，收成统一库；接 8 种 YouTube 解说语法进口播管线；最后做《花叔穿越名画》23 种画风、2分08秒 | ✅ |
| F-042 | O | 仓库结构：SKILL.md（先判断任务再按表读对应文档）+ references/（01–12 方法文档、35 风格卡、9 语法卡、正面经验）+ assets/ + scripts/engine/（可整个复制走的动画工程）+ scripts/analyze/breakdown.py + scripts/qa.py + scripts/audio/ + font_subset.py 等 | ✅ |
| F-043 | O | 方法文档 12 篇：拆解/机制/一帧先行/纯代码绘制/节奏配乐/角色/长卷等（references/01–12）| ✅ |
| F-044 | O | 绘画与动画库 17 个（references/… lib/ 笔刷/渲染器/后期/骨架/镜头/图表/排版） | ✅ |
| F-045 | O | 转场：艺术风格签名转场与解说转场，含淡入、硬切和纸面转场 | ✅ |
| F-046 | ⚠️ | "万星项目创作者"声明：文章称花叔 huashu-design 是万星项目，本仓库页未直接证实 huashu-design 的 Star 量级（不在本仓库可核范围） | ⚠️ 无法独立证实 |
| F-047 | O | 正面经验文档存在：`references/07-正面经验.md`（哪些做法被证明有效） | ✅ |
| F-048 | O | 「动漫风格」开头示例构图沿用 Tak 原片思路；仓库不含原片帧/截图/音频；配乐脚本是原创示例乐谱（官方致谢段） | ✅ 版权边界清晰 |
| F-049 | O | 版权：代码与文档 MIT；人物交给生图模型出帧+代码合成（"画面里要有人"QA 卡）；角色帧库 `scripts/engine/demos/_shared/hero/` | ✅ |
| F-050 | O | 官方"能做什么"矩阵：复刻/拆解→量转场节拍热图；做梵高莫奈→先设计一帧再动；用口播做→镜头表→定风格→世界画布加镜头→画面轨；做人穿名画→长卷骨架；解说动画段→按口播选语法喂 JSON 出精确到帧片段；配乐卡节奏→BPM/动机/结尾音效 | ✅ |
| F-051 | O | 依赖：uv、ffmpeg、Playwright Chromium；试渲命令与文章一致；JavaScript 96.1% + Python 3.8% | ✅ |
| F-052 | O | 拆解 `breakdown.py` 与 QA `qa.py` 均确认存在于仓库 scripts/ 下 | ✅ |
| F-053 | O | 许可证与角色素材例外：`scripts/engine/demos/_shared/hero/`、`scripts/engine/demos/long_scroll/frames/`、`assets/角色/` 的花叔卡通形象与角色帧只用于本 skill 示范，不随 MIT 授权其他用途 | ✅ |
| F-054 | O | 旁系：作者另在开发 nuwa-skill（造 Skill）、darwin-skill（让 Skill 进化）；官网 bookai.top/huasheng.ai | ✅ |

## 双份一致性核对

- 本文件 F 编号集合 = {F-001 … F-054}，连续无跳号
- 事实来源分层：F-001~F-036 出自微信推介文（次要信源），F-037~F-054 出自 GitHub 官方 README/仓库页（一手信源），凡一手可核声明已在核验栏回引对应 F 编号
- 保留的 ⚠️/❌ 项：F-007（Star 数失实）、F-013（8 vs 9 语法数）、F-035（skills CLI 版本坑）、F-046（万星项目待证）