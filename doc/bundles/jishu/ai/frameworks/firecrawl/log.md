---
okf_version: "0.2"
type: Log
title: firecrawl bundle 变更日志
description: 生成、两轮核验、并行会话合并与对抗审查记录
tags: [changelog]
---

# 变更日志（log）

## 2026-09-16 初版生成（含并行会话合并）

- **来源**：微信公众号「开源软件社」《狂揽 17 万 Star！这个开源项目，把整个互联网变成了 AI 的数据库》（原创，2026-09-01 07:50，四川，4303 字，栏目「AI 基础设施 2026·08」）。
- **工作流**：seven-concepts 场景 4（知识沉淀 R→I→E→V→C）+ blog-article-to-okf-wiki 七阶段；信源微信反爬确定，browser_use 直取 `#js_content`。
- **事实采集**：F-001~F-063（博文 34 + 第一轮官方核验 14 + 第二轮独立深核 15），双份登记（spec facts.md ↔ references/article-source.md）编号集合一致、连续无跳号。
- **P0 核验**：两轮 26 个声明簇 **20✅ / 5⚠️ / 2❌**。两处 ❌：① F-008 博文"最近提交 2026-08-24"失实（commits API：08-20~31 共 94 提交、09-01 当天 5+）；② F-007"P95 跨数百万页面"样本限定查无出处（实为 1,000-URL 自建基准 3,387ms）。
- **骨架判定**：操作可复现性两问 ①是 ②否（无作者实测/版本/输出，代码为 README 转述）→ 技术综述骨架，**不设 examples/**。
- **产出文件**：9 个（index/log + concepts×3 + concepts/index + references×2 + references/index）。

### 并行会话碰撞与合并（重要）

- 本任务存在一个早前/并行会话（21:40 完成 R+I，spec 与 F-001~F-048 一轮核验），并在本会话 E 阶段期间向同目录写入了根 index.md/log.md（一轮版：17✅/1❌，Star 179,337，判定博文"默认模型说反"❌）。
- 本会话第二轮独立深核证明其一轮版两处判定需要修正：① F-038 博文"默认 mini"与官方 2026-01-14 发布文（"Spark 1 Mini (Default)"）一致，矛盾在官方两页之间，且 spark-1 全系已弃用路由 spark-2 → ❌ 改判 ⚠️；② F-008 提交日期经 commits API 升级为 ❌ 实证。并补入 F-049~F-063（1,000-URL 基准精确口径、spark-2 现状、SideGuide 主体与 SEC 融资、云端专属能力清单、包版本实测、免费额度等）。
- 处理：以深核版**统一全束**——concepts/references/index 共 7 文件为深核版原写；根 index.md/log.md 由本会话重写取代一轮版；spec facts.md/tasks.md 同步为 F-063 版。
- 并行写入还造成 `jishu/ai/index.md` 第 72 行 toctree 标记与 aitokenbus 表格行拼接异常 + firecrawl 表格行重复（一轮🔥行 + 深核🕷️行），本会话已修复拼接、保留深核行并保留其他并行会话全部条目（aitokenbus/gpt6/inurl×2 等）。

### V 阶段对抗审查与机械门禁结果

- **四视角审查**：
  - 事实溯源（魔鬼代言人）：所有数字/模型名/包名/端点均挂 F 编号；两处 ❌ 在 concepts/00 与根 index 呈现官方正确值；96%/3,387ms/60% 全程标"厂商自述"并带数据集名与测量日期。
  - 结构规范：3 概念 + 2 信源，3 个 index.md 含 toctree；Mermaid 节点文本加引号（flowchart 与 sequenceDiagram 各一）。
  - 读者可用性（新人视角）：bundle 内相对链接逐一核对；跨束仅引 wigolo/browseract/agent-platform-notes/mattpocock-skills 四个已存在束；代码块标注"转自官方 README/非作者实测"与 SDK 版本。
  - 时效边界（未来视角）：Star 双时点（171,711≈8 月底 / 181,040@09-16）、spark-1 弃用现状、厂商基准无复测、SEC 数字 About 页未更新、stale_after 2026-12-31 前复核项已列。
  - 老板视角：AGPL SaaS 网络开源义务、自托管运维栈（PG/Redis/RabbitMQ/Playwright）与自带 LLM 成本、云端专属能力均在 concepts/02 与根 index 提示。
- **机械门禁（直接运行子模块 scripts，2026-09-16）**：
  - `python scripts/check-bundles-index.py`：五面对账通过（结果见下"计数"）
  - `python scripts/check-toctrees.py`：无孤立文档/无断链/toctree 完整
  - `python scripts/check-utf8.py`：全库 UTF-8 strict 通过
  - 双份 F 编号正则：spec facts.md 与 article-source.md 各 63 个（F-001~F-063），集合相等、连续无跳号
  - 相对链接：本束内/跨束链接 0 断链；无绝对 URL 形式本地链接、无家目录绝对路径（机械扫描通过）
  - frontmatter：okf_version/type/title/description/tags/generated/verified/status/stale_after/sources 齐备（博文 + GitHub API + README + 官网 + SEC 多信源）
- **invoke 包装说明**：早前会话记录 `invoke gates.*` 因 invocations 包元数据损坏无法加载；本会话改用 `python scripts/*.py` **直接运行同一套门禁底层脚本**，以上为脚本真实输出（非 invoke gates 结论）。
- **计数**：地面真值（门禁脚本目录树 BFS）在修复后为 total **555** / jishu **422** / ai **203**，firecrawl 已包含其中（束目录在首次跑脚本前已由并行会话创建于磁盘）；本会话补齐缺失的组导航表行，未重复 +1。
- **既有漂移登记（非本会话引入，不扩大范围）**：`jishu/index.md` 域导航页导语"111 个一级束"、ai 行"45 束"及 document/data/comm 等多行计数为历史过期值（门禁真值 422/203），全页失真，建议另起专项对账（与 wigolo 束 log 登记的漂移同源）。
- **并行会话二次漂移修复**：收尾期间并行会话一度把 `bundles/index.md` 改写为 total 549/jishu 416/ai 197（目录树真值 555/422/203，差 6），门禁拦截后已按地面真值修复 frontmatter、计数行、域节标题、mermaid 节点与 ai 组束数列，复跑三门禁全过。

### C（提交）

- 待用户确认后按序提交：① 子模块 awesome-okf-xs（本束 9 文件 + jishu/ai/index.md 修复，显式文件列表）→ ② 主仓库 spec（firecrawl-blog-okf-wiki/：spec.md/facts.md/tasks.md/review.md）→ ③ 主仓库 gitlink；用户未要求不 push。
