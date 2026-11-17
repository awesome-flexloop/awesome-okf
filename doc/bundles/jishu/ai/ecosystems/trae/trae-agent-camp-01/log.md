# 更新日志

## 2026-11-18

- **复读课程文档**：revision_id 仍为 1236，与 2026-11-15 首次采集一致，正文未发现新增或删除章节（F-095）。
- **补充事实**：新增 F-092（文档内鸿蒙表述双口径：开头「鸿蒙 5 以下」、收获段「鸿蒙 4.x 及以下」）、F-093（评论区鸿蒙 4.2.0 闪退、雷电模拟器可用）、F-094（评论区 401/404、`package info is null`、网盘镜像、OpenRouter 替代）。事实总数 91 → 95。
- **正文回归**：00 篇补设备口径差异与社区反馈；03 篇补评论区排查线索；核验报告增第七节。
- **结论**：P0 维持 7 ✅ / 3 ⚠️ / 0 ❌，`status: stable` 不变；社区反馈只作未核验线索，不写成标准步骤。
- **门禁**：本轮结束复跑 toctree、总索引、UTF-8 与链接检查。

### 源码复读（2026-11-18）

- **仓库前进**：本地 main 由 580fdf7（PhonePal）前进到 08cd059（小满），包名统一为 `dev.xiaoman.app`；远端新增 `camp/02-skill-builder`；main 0.1.0、02 分支 0.2.0。
- **事实更新**：S-001~S-007、S-035、S-038 改为当前状态；新增 S-052~S-059（MCP、网页版、iOS、11 个示例技能、SKILL_SAVE、docs 目录）。
- **新增页面**：`concepts/08-source-map.md`（十一个模块、改动落点、读源码路径）。
- **结论**：P0 维持 7 ✅ / 3 ⚠️ / 0 ❌；`status: stable` 不变；新增模块标为课后扩展，不改变课程主线。

### ReAct 调研补充（2026-11-18）

- **信源**：ReAct 原论文 arXiv:2210.03629（ICLR 2023）与项目页 react-lm.github.io。
- **正文**：`concepts/02-agent-anatomy-react.md` 增「论文里的 ReAct 与手机上的 ReAct」对照表，区分文本协议与 JSON 动作、截图/节点观察、步数上限与 Sentinel。
- **交叉链接**：指向 Hello-Agents 的 ReAct 教程（论文实验、失败模式、工程化）。
- **结论**：课程口径与论文机制一致；差异在工程编码与安全约束，不改变 P0 结论。

### 门禁记录（2026-11-18）

| 门禁 | 结果 |
|------|------|
| toctree 完整性 | 通过 |
| 总索引计数对账 | 通过：9 域 / 65 组 / 741 束 |
| UTF-8 编码 | 通过：13389 个文件 |
| Markdown 链接 | 通过：本束全部相对链接有效 |

## 2026-11-17

- **源码核验轮**：只读核验本地 `xiaoman` 仓库（`main` 580fdf7 与 `origin/camp/xiaoman`），新增 [源码核验事实登记](references/source-code.md)（S-001~S-051）。
- **关键确认**：课程分支包名为 `dev.xiaoman.app`、CLI 入口 `cli/xiaoman.py`、版本 0.1.0；记忆为 Basic Memory Markdown，路径 `<external files>/memory/`；提醒使用 `AlarmManager.setAndAllowWhileIdle`（非精确、重启清空）；Sentinel 内置 17 个确认词、授权分 ONCE/TASK；许可证 MIT。
- **P0 复核**：10 项 → **7 ✅ / 3 ⚠️ / 0 ❌**；G-03、G-05、G-06、G-07 关闭，G-01 部分关闭；G-02、G-04、G-08 仍开放。
- **状态调整**：`status` 由 `draft` 升为 `stable`——核心机制已有源码或官方文档双重确认。
- **正文改动**：第 2、3、4、7 篇追加源码小节；index 与 references/index 同步；示例与任务设计未改。
- **门禁**：本轮结束复跑 toctree、总索引、UTF-8、链接与 Sphinx dummy 构建。

### 门禁记录（2026-11-17）

| 门禁 | 结果 |
|------|------|
| toctree 完整性 | 通过 |
| 总索引计数对账 | 通过：9 域 / 65 组 / 741 束 |
| UTF-8 编码 | 通过：13389 个文件 |
| Markdown 链接 | 通过：本束全部相对链接有效 |
| 库规模基线 | 通过：总索引 741；行尾归一残差 +43430 属未提交工作区变更 |
| Sphinx dummy 构建 | 通过：构建成功，364 条既有警告，本束 0 告警 |

## 2026-11-16

- **模式独立入库**：将 [五个可迁移模式](patterns.md) 逐条去重后登记入 SpecWeave 主仓方法论模式库，新增 5 个 L1-draft 条目——`base-first-minimal-customization`（governance-strategy）、`explain-only-reconnaissance`、`four-element-task-brief`、`screenshot-step-cost-trimming`（ai-collaboration）、`split-chain-triage`（tools-automation）。
- **去重与重裁**：每条模式比对 4~6 个既有近邻条目，按「作用对象／核心动作／所处层级」三维裁定不重复，并为每条「不重复」裁定写出可证伪区分判据。库内成熟度维持 **L1-draft**：单案例 + 沉淀侧自审，且五者共享同一证据基座、互不构成独立验证。
- **G3 复核（入库版）**：反模式由案例版 3 条/模式扩充为 **6 条/模式**（补充跨场景失效形态与代价），检验标准 5 条/模式；核心步骤 5~6 步/模式。扩充内容只在库内通用版，本包案例版未同步改写。
- **回写范围**：仅 `patterns.md`（入库说明 + 库内路径表）与本文件；未改动 8 篇概念页、3 篇示例页、`references/` 事实登记与 `index.md`。
- **跨仓引用口径**：库内条目以 `source` / `source_report` 单向指回本包 `index.md`；本包以主仓路径文本回指，不建跨仓相对路径链接（子模块独立发布时相对链接会越出仓库根）。

### CMD-LOG

```text
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S0 | event=CMD_START | session=sc-20261116-trae-agent-camp-01-pattern | msg=模式沉淀开始：五模式独立入库 | ctx={"scenario":"knowledge","topic":"trae-agent-camp-01","depth":"standard"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S99 | event=CHAIN_COMPLETED | session=sc-20261116-trae-agent-camp-01-pattern | msg=入库完成：5条L1-draft、3处索引登记、入库V门通过、上游已回写 | ctx={"patterns":5,"areas":3,"gates":["G3","V"]}
```

## 2026-11-15

- **创建知识包**：以 TRAE 训练营第二期 01 课课程文档（采集于 2026-11-15，revision_id 1236）为唯一主信源，按 R→I→E→V→C 链路生成 8 篇概念、3 篇示例、2 篇信源参考与 5 条洞察、5 个模式。
- **事实登记**：F-001~F-091 共 91 条，其中课程原文 80 条（含 F-090、F-091）、核验补充 9 条（F-079~F-087）、元信息 2 条（F-088、F-089）。
- **P0 核验**：10 项 → 5 ✅ / 5 ⚠️ / 0 ❌。通过项为 Base URL、模型存在性与视觉/GUI 能力、豆包手机助手 2026 年 9 月发布、APK 大小、ReAct 定义；部分通过项集中于免费额度口径、仓库归属、设备边界、费用估算与 App 内部行为。
- **敏感度处理**：课程文档托管于企业内部飞书域，本包按用户指定目录落盘；正文与信源层均不引用其 URL，不转载课堂体验额度的领取流程、令牌与个人登记信息（该项已于 2026-11-13 21:00 过期），课程文档直接引用的附件令牌与视频令牌不收录。
- **V 审查**：四视角共 7 条意见，采纳 5 条、部分采纳 2 条、不采纳 0 条；采纳项已回归到 01、02、03、05、07 与 index 正文。
- **索引接入**：新增 `jishu/ai/ecosystems/trae/trae-agent-camp-01/`，并同步 trae 分组、ecosystems 分类、ai 域与 bundles 总索引四层计数。
- **门禁**：`check-toctrees.py`、`check-bundles-index.py`、`check-utf8.py`、链接检查四项结果见下方记录。

### 门禁记录

| 门禁 | 命令 | 结果 |
|------|------|------|
| toctree 完整性 | `python scripts/check-toctrees.py` | 通过：全部 index.md 引用有效，所有内容文档可达 |
| 总索引计数对账 | `python scripts/check-bundles-index.py` | 通过：9 域 / 65 组 / 738 束，五面一致 |
| UTF-8 编码 | `python scripts/check-utf8.py` | 通过：13336 个文件均为有效 UTF-8 |
| Markdown 链接 | `.agents/scripts/check-links.py --path <bundle>` | 通过：20 文件 / 75 条本地引用零断链（过程中修复 3 处跨组相对路径） |
| 库规模基线 | `python scripts/check-asset-baseline.py` | 规模数字通过（README 与 doc/index.md 已同步 738）；字节残差为工作区未提交变更（含并行会话改动），按脚本要求提交后复跑 |
| Sphinx dummy 构建 | `sphinx-build -b dummy -E doc _build/dummy` | 通过：构建成功，全库 364 条既有警告（集中在其他既有束）；本束 0 告警 |

### CMD-LOG

```text
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S0 | event=CMD_START | session=sc-20261115-trae-agent-camp-01 | msg=方法论编排开始：TRAE 训练营第二期 01 课学习与洞察 | ctx={"scenario":"knowledge","topic":"trae-agent-camp-01","depth":"standard"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S1 | event=SCENARIO_DETECTED | session=sc-20261115-trae-agent-camp-01 | msg=场景4知识沉淀 | ctx={"chain":"R-I-E-V-C"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S2 | event=CHAIN_SELECTED | session=sc-20261115-trae-agent-camp-01 | msg=链路R-I-E-V-C，含P0核验与四视角审查 | ctx={"gates":["G1","G2","G3","V","G4"]}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S3 | event=GATE_PASSED | session=sc-20261115-trae-agent-camp-01 | msg=G1事实无因果词，91条编号事实 | ctx={"facts":91}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S4 | event=GATE_PASSED | session=sc-20261115-trae-agent-camp-01 | msg=G2洞察四元组完整，5条 | ctx={"insights":5}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S5 | event=GATE_PASSED | session=sc-20261115-trae-agent-camp-01 | msg=G3模式要素完整，5个L1-draft | ctx={"patterns":5}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S6 | event=GATE_PASSED | session=sc-20261115-trae-agent-camp-01 | msg=V四视角7条意见，采纳5条部分采纳2条 | ctx={"adopted":7}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S99 | event=CHAIN_COMPLETED | session=sc-20261115-trae-agent-camp-01 | msg=知识包落盘完成 | ctx={"files":20}
```
