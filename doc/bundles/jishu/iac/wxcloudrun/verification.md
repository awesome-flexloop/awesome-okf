---
type: Reference
title: "微信云托管 OKF Wiki 独立验证记录"
description: "记录微信云托管教程在 F 编号一致性、勘误落实、frontmatter、链接、导航、计数与项目质量门上的独立核验结果。"
tags: [微信云托管, wxcloudrun, verification, quality, OKF]
generated: { by: "agent:blog-article-to-okf-wiki", at: "2026-10-22T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-10-22T00:00:00Z" }
status: draft
stale_after: 2027-04-22
sources:
  - id: docs
    resource: https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/basic/intro.html
    title: 微信开放文档 · 云托管（2026-10-22 采集）
  - id: fact-table
    resource: /references/doc-source.md
    title: 微信云托管官方文档事实登记表（F-001~F-190）
---

# 微信云托管 OKF Wiki 独立验证记录

本页记录微信云托管教程束（145 页官方文档 → 190 条编号事实）的独立验证证据。**本页只报告核验结果，不声称做过真实环境部署**。

## 已完成检查

| 检查项 | 结果 | 证据与口径 |
|---|---|---|
| 事实编号连续性 | PASS | 脚本提取 `^\|\s*F-(\d{3})\s*\|` 表行：F-001~F-190 共 190 条，连续无跳号、无重复。 |
| 双份 F 编号一致性 | PASS | spec 侧 `facts.md` 与 bundle 侧 `references/doc-source.md` 的编号集合逐元素相等，均为 190 条；后者由脚本从前者派生，不存在人工誊写漂移。 |
| 正文 F 编号越界 | PASS | 脚本扫描 bundle 全部 Markdown 中出现的 `F-\d{3}`，逐一比对事实登记表集合，**越界编号 0 个**；概念文档覆盖 175 个不重复编号，示例文档覆盖 91 个不重复编号，两者并集 181 个，剩余 9 个（F-032、F-033、F-036、F-037、F-041、F-042、F-046、F-050、F-051）仅出现在事实登记表与覆盖度矩阵的边界登记中，不作为内容引用。 |
| 勘误落实 | PASS | E-001~E-009 共 9 条官方文档内部口径不一致已在正文按采信结论呈现，并统一注明「官方文档不同页面口径不一致，本处采信 X」；未出现照搬错误值的表述。E-009 的源文档算术不一致（正文 702 与同页算式 `720 − 12 = 708`）已在两处引用点同时给出两个数值并标注「源文档算术存疑」，采信源文档正文原值 702。 |
| 厂商自述标注 | PASS | 可用性 99.99%（F-017）、DDoS 防护免费（F-094）等厂商宣称项在正文与根索引均有显式提示块。 |
| Frontmatter 完整 | PASS | 根 `index.md` 含 `okf_version: "0.2"` 与 `type: bundle`；7 篇 concepts 为 `type: Concept`，4 篇 examples 为 `type: Example`，references 两篇为 `type: Reference`。内容文档（13 篇）九字段齐备；根 `index.md` 未设 `tags`（按 bundle 规范可省）；`log.md` 与 `concepts\|examples\|references/index.md` 四个导航文件按 OKF 规范不设 frontmatter。 |
| 三级 toctree 完整 | PASS | `python scripts/check-toctrees.py` 通过；bundle 根 `index.md` 收录 `concepts/index`、`examples/index`、`references/index`、`log`、`verification`，各子目录 `index.md` 收录本目录全部内容文件。 |
| 相对链接可达 | PASS | bundle 内全部 Markdown 相对链接逐一 Test-Path 通过；**本包内**零 `file:///` 绝对路径、零本机绝对路径、零 `.temp/` 引用（注：`file:///` 在本子模块的其它 bundle 中存在既有存量，不在本包范围，也未在本任务中修改）。 |
| UTF-8 严格解码 | PASS | 新增/修改的全部 `.md` 以 UTF-8 strict 解码无异常、无 BOM、无乱码。 |
| 三级计数同步 | PASS | `python scripts/check-bundles-index.py` 通过：9 域 / 63 组 / **661 束**；`jishu` 域 491 束 / 19 组，`iac` 组 2 束。frontmatter、计数行、域节标题、分组表束数列、末尾 toctree 五面一致。 |
| 敏感信息 | PASS | 全文零真实 AppID / Secret / 商户号 / 密钥，示例一律使用占位符。 |
| 非官方代码标注 | PASS | `examples/` 中 6 个代码块全部在紧邻上一行标注「以下为非官方示例代码，基于官方文档描述自行编写。」；`concepts/02-call-and-identity.md` 中 1 个代码块为官方文档调用示例原文（F-073），已显式标注「官方文档给出的调用示例原文（逐字引用 F-073），非本知识包改写」。全包其余代码块均为 mermaid 图或 toctree 指令块。 |
| 部署边界声明 | PASS | 4 篇 examples 与根 `index.md` 均明确声明「未在任何真实云托管环境部署验证」。 |
| 术语自解释 | PASS | 「结单」「webshell」两处在首次出现的概念文档中已补一句释义；「预发」仅出现在逐字引用 F-091 的表格单元中，保留原文口径。 |
| 计数口径一致性 | PASS | F-163 的 7 项「暂不支持的场景」在 `concepts/05`、`concepts/06`、`examples/04` 三处均按 7 条对齐：表格已把原文的「仅支持 HTTP」与「不支持 tcp/udp/mqtt」拆为两行，使表行数与 F-163 条目数一一对应，正文不再出现「表 6 行却称 7 条」的矛盾。 |
| 表格列数与渲染 | PASS | 脚本扫描本包全部 Markdown：按「忽略 `\\|` 转义」规则切分单元格，逐表比对表头列数与数据行列数，**不一致 0 处**。代码 span 内的 `|` 会切分单元格（MyST/markdown-it 严格按表头列数渲染，超出列被静默丢弃），已全部转义为 `\|`（F-068 的 `--releaseType=FULL\|GRAY`、本文件导航路径记法等）。 |
| 事实陈述归属 | PASS | 全部表格的「依据/事实」列均指向登记表中真实存在的 F 编号：脚本提取全包 F 引用集合并与 F-001~F-190 求差，**越界 0 个**；前置条件表中「被调服务需有线上版本」一条已改挂 F-060（版本分线上/线下两种状态），不再借用 F-053（发布单三子流程）充当依据。 |
| 计数口径（覆盖矩阵） | PASS | 脚本统计：`concepts/` 覆盖 175 个不重复 F 编号、`examples/` 覆盖 91 个、并集 181 个、全包 190 个；coverage-matrix 第三节列出的 9 条（F-032、F-033、F-036、F-037、F-041、F-042、F-046、F-050、F-051）经复核在 concepts/ 与 examples/ 中**确实均未出现**，与矩阵陈述一致。 |

## 质量门结果

| 检查项 | 状态 | 验收方式 |
|---|---|---|
| Bundle 与父级 toctree | PASS | `python scripts/check-toctrees.py` 退出码 0。 |
| 全库 bundle/group/domain 计数 | PASS | `python scripts/check-bundles-index.py` 退出码 0，输出「9 域 / 63 组 / 661 束，五面一致」。 |
| UTF-8 与全部项目质量门 | PASS | `python scripts/check-utf8.py` 退出码 0，输出「UTF-8 检查通过: 12066 个文件均为有效 UTF-8」；`check-toctrees.py` 与 `check-bundles-index.py` 均退出码 0（见上表）。 |
| 完整文档构建 | 未执行 | 本次任务未运行 `invoke build`（Sphinx 完整构建），因此**不主张**构建通过；Sphinx 侧的 toctree 可达性已由 `check-toctrees.py` 的可达性检查覆盖。 |
| 复核方式 | — | 复核本记录可执行 `python scripts/check-utf8.py`、`python scripts/check-toctrees.py`、`python scripts/check-bundles-index.py`（工作目录为本子模块根），三者输出即为本页所述结论的复现方式。 |

## 范围与限制

- 本教程覆盖官方文档站云托管分区 145 页主题域的事实内容，**不覆盖**控制台界面逐屏操作、各语言运行时库完整 API、计费规则变更历史、与腾讯云其他产品的联动矩阵（详见[覆盖度矩阵](references/coverage-matrix.md)）。
- 价格为**刊例价时点值**（采集日 2026-10-22），不代表任何折扣后的实际成交价；文档自述预估基于刊例价即可理解为理论最高价（F-156）。
- 性能、可用性、成本对比类表述为**厂商自述**，本教程按原样引用并标注，未做独立验证。
- 官方文档内部 9 处口径不一致（E-001~E-009）已按采信结论处理，其中 E-009 为源文档自身的算术不一致，引用处已标注「源文档算术存疑」。
- **未在真实云托管环境部署验证**，示例代码为按官方文档描述自行编写的非官方示例。
