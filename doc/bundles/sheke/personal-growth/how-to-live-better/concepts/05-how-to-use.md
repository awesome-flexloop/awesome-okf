---
type: Concept
title: 如何使用：检索页、离线版与 AI skill
description: 四种使用姿势实操——在线检索页的关键词/章节/证据级/三成本/口径组合筛选与条目互引、三种离线电子版（HTML/PDF/EPUB）固定下载链接、life-decision-guide 在 Claude Code 与 Codex 的安装与能力边界、git clone 自托管的三个注意事项，以及四个信源站点如何选择
tags: [使用指南, 检索页, 筛选, 离线HTML, PDF, EPUB, Kindle, Claude-Code, Codex, AI-skill, 自托管, 镜像选择]
generated: { by: "blog-article-to-okf-bundle", at: "2026-09-28T21:30:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-09-28T21:30:00+08:00" }
status: stable
stale_after: 2027-03-31
sources:
  - id: live
    resource: https://eternity4719.github.io/HowToLiveBetter/
    title: 官方在线检索页
  - id: repo
    resource: https://github.com/eternity4719/HowToLiveBetter
    title: 原仓 README"怎么读/自己跑一份"节与 Release 产物
  - id: skill-readme
    resource: https://raw.githubusercontent.com/eternity4719/HowToLiveBetter/main/skills/life-decision-guide/README.md
    title: life-decision-guide skill 官方安装说明
  - id: mirror-dlgrv
    resource: https://dlgrv.github.io/HowToLiveBetter/zh/?sec=1
    title: dlgrv 翻译快照
  - id: mirror-cdy
    resource: https://cdyforever.github.io/how-to-live-better/
    title: cdyforever 镜像
---

# 如何使用：检索页、离线版与 AI skill

> 本篇是**使用层**。这本书的正确用法不是通读，而是"**带着具体处境来查**"；本篇给出四种取用姿势和选站建议。所有功能描述以原仓 README 为准（F-008、F-013、F-014）。

## 1. 在线检索页：五个筛选维度怎么叠

打开 <https://eternity4719.github.io/HowToLiveBetter/>，数据与仓库 book/ 实时同步。可用条件（可任意叠加）：

| 维度 | 取值 | 典型用法 |
|---|---|---|
| 关键词 | 任意词 | 搜"低钠盐""工伤""ICP""96110" |
| 章节 | 33 章任选 | 只看第 13 章急救、第 19 章职场 |
| 证据等级 | A / B / C | 只看 415 条数字最硬的（勾 A） |
| 三项成本 | 花不花钱、花多少时间、要不要毅力 | 勾出"不花钱+不花时间+不要毅力" |
| 换回什么 | 寿命 / 钱 / 时间精力 / 人身自由 | 先定口径再同口径内比较（见 [02 模型](02-cost-benefit-model.md)） |

**三个推荐组合**：

1. **零成本救命清单**：勾证据 A + 性价比"极高" → 现行 104 条中收益落在寿命口径、三项成本全零的条目（F-042）；
2. **遇事速查**：关键词 + 对应章节（如"胸痛"→第 13 章），先看"说人话"行，再看备注禁忌；
3. **同口径比价**：选定"换回钱"，再按成本维度组合，比较第 5、7、15 章的省钱动作。

两个阅读辅助：

- **术语悬浮**：带虚线的统计术语（HR、RR、荟萃分析、定金/订金等 41 个）鼠标悬停（手机点按）弹释义，不必跳查（F-039）；
- **条目互引**："见第 8 节第 17 条"这类引用带虚线，点击**就地显示**被引条的标题与"说人话"，再按"跳过去"才跳转；若目标条被当前筛选条件藏住，页面会自动清掉筛选（F-038）。

## 2. 离线三件套：固定链接、随正文自动重生成

| 格式 | 下载链接（固定，正文更新后产物自动重建） | 适用 |
|---|---|---|
| 单文件 HTML | `https://github.com/eternity4719/HowToLiveBetter/releases/download/epub-latest/HowToLiveBetter.html` | 双击即开、无需服务器和联网，**可直接在微信里转发** |
| PDF | 同目录 `HowToLiveBetter.pdf` | A4 排版、两百多页、目录页码书签、每节另起一页；打印或手机翻读 |
| EPUB | 同目录 `HowToLiveBetter.epub` | Kindle 用 Send to Kindle 推送，其他阅读器通用 |

关键认知（F-013）：**转发出去的副本不会跟着原文更新，一切以在线版为准**。需要打印某章给家人时再用 PDF，日常查用在线版最不容易用过时数字。

## 3. AI skill：让 Claude Code / Codex "照这本书回答"

仓库自带 `life-decision-guide` skill，设计得非常克制（F-014）：

- **只做一件事**：先从正文里把相关条目查出来，再照书里的算账方式排序回答，每条注明出自第几节第几条；
- **查不到就说查不到，不凭记忆编数字**；
- 规则单文件（SKILL.md），Claude Code 与 Codex 共用；节清单与档位算法不写死（运行时读 README 与 index.html），所以正文增改不会让 skill 过期。

安装方式（官方说明原文）：

```bash
# Claude Code：装到个人 skill 目录
mkdir -p ~/.claude/skills/life-decision-guide && curl -fsSL \
  -o ~/.claude/skills/life-decision-guide/SKILL.md \
  "https://raw.githubusercontent.com/eternity4719/HowToLiveBetter/main/skills/life-decision-guide/SKILL.md"

# Codex：装到自定义提示词目录，用 /life-decision-guide 调用
mkdir -p ~/.codex/prompts && curl -fsSL \
  -o ~/.codex/prompts/life-decision-guide.md \
  "https://raw.githubusercontent.com/eternity4719/HowToLiveBetter/main/skills/life-decision-guide/SKILL.md"
```

在仓库目录内打开 Claude Code 或 Codex 则**无需安装**（`.claude/skills/` 与根 `AGENTS.md` 已指向它）。Codex 想全局自动生效，可把官方给的那一行 AGENTS.md 提示加入 `~/.codex/AGENTS.md`。问法示例："每天通勤两小时值不值""朋友让我替他担保，签不签""替公司写爬虫会不会坐牢"。

## 4. 自托管：三行命令与三个坑

```bash
git clone https://github.com/eternity4719/HowToLiveBetter.git
cd HowToLiveBetter
python -m http.server 8000   # 然后浏览器开 http://localhost:8000/
```

注意（F-011）：

1. 检索页是**纯静态**的，README.md + book/ 就是数据，无后端、无数据库、无需装依赖；丢给 Nginx/GitHub Pages/对象存储效果一样；
2. **index.html 必须经 http 打开**——直接双击本地文件会空白（浏览器不允许网页读本地文件），这种场景请改用离线单文件 HTML；
3. 想自己生成 EPUB/HTML/PDF 才需要 Node 工具链与 pandoc ≥3.1、typst ≥0.13，普通读者不需要（Release 里已是自动产物）。

## 5. 四个站点怎么选

| 站点 | 用途建议 |
|---|---|
| **eternity4719.github.io**（官方） | **默认唯一选择**：查条目、看最新数字 |
| **github.com/eternity4719**（原仓） | 查 Markdown 原文、看 `引用对照.md` 与 `核实记录/`、读 docs 长文、提 Issue、装 skill |
| cdyforever.github.io | 官方页打不开时的结构级备用（33 章渲染同构），但不保证同步时效 |
| dlgrv.github.io | **仅作翻译研究/版本考古**：站点自述为非官方翻译快照（608 条口径）、原文仍在更新，数字可能滞后，**不要据此做决策** |

---

下一篇 [06-boundaries-and-method.md](06-boundaries-and-method.md) 讲清楚这本书的边界，以及如何把它的框架迁移到评估任何一条生活建议。
