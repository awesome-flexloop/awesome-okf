# 更新日志

## 2026-11-18

- **复读课程文档**：revision_id 由 1074 变为 1076，正文有修订（F-119）。
- **补充事实**：新增 F-120~F-124，总数 118 → 124。包括：02 课三处统一「安卓与鸿蒙 4.x 及以下」（F-120）；淘宝排错新增「App 里的聊天提示词」修复项（F-121）；课程称课程版源码在 `main`、技能自建在 `camp/02-skill-builder`（F-122）；评论区新增 superagent-lead 打不开反馈（F-123）；「7 个问题」标题与 6 行表格差异保留（F-124）。
- **正文回归**：01 篇补计数事实、05 篇补课程分支口径、06 篇补评论反馈、07 篇补聊天提示词修复；index、references/index 与核验报告同步。
- **结论**：文档层 P0 维持 8 ✅ / 3 ⚠️；源码复读后升为 9 ✅ / 2 ⚠️ 并转 `stable`（见下）。
- **门禁**：本轮结束复跑 toctree、总索引、UTF-8 与链接检查。

### 源码复读（2026-11-18）

- **仓库前进**：main 08cd059（小满，`dev.xiaoman.app`）；远端新增 `camp/02-skill-builder`（0.2.0 / versionCode 2）。
- **事实更新**：S-001、S-003、S-004、S-035、S-038 改为当前状态；新增 S-053~S-059（MCP、网页版、iOS、11 个示例技能、SKILL_SAVE、docs）。
- **关键结论**：`chat` 已进入 `SkillChannel`；五个场景技能已公开；02 分支含 `SKILL_SAVE` 与 `SkillAuthoringTest`；P0 由 8✅/3⚠️ 升为 **9✅/2⚠️**，状态升为 `stable`。
- **新增页面**：`concepts/09-module-internals.md`（技能生命周期、循环参数、Sentinel、MCP、SKILL_SAVE、三种运行形态）。

### 门禁记录（2026-11-18）

| 门禁 | 结果 |
|------|------|
| toctree 完整性 | 通过 |
| 总索引计数对账 | 通过：9 域 / 65 组 / 741 束 |
| UTF-8 编码 | 通过：13389 个文件 |
| Markdown 链接 | 通过：本束全部相对链接有效 |

## 2026-11-17

- **源码核验轮**：只读核验本地 `xiaoman` 仓库（`main` 580fdf7 与 `origin/camp/xiaoman`），新增 [源码核验事实登记](references/source-code.md)（选录 36 条 S 事实，编号与 01 包一致）。
- **关键修正**：`channel` 源码枚举为 api/cli/deeplink/gui/deeplink-then-gui/mixed，**没有 chat**（S-035）；公开远端没有 `camp/02-skill-builder`（S-001）；02 课的五个场景技能不在公开分支（S-038）；lint/push 输出改为源码实际格式（S-047、S-048）。
- **P0 复核**：11 项 → **8 ✅ / 3 ⚠️ / 0 ❌**；G-04、G-05、G-06、G-07 关闭，G-01、G-03 部分关闭，新增 G-10（02 课专属能力未公开）。
- **正文改动**：第 2、3、4、5、6、7、8 篇与 index、references/index 同步更新；其余课程事实保持不变。
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

- **创建知识包**：以 TRAE 训练营第二期 02 课课程文档（采集于 2026-11-16，revision_id 1074）为唯一主信源，按 R→I→E→V→C 链路生成 9 篇概念、6 篇示例、2 篇信源参考与 5 条洞察、6 个模式。
- **事实登记**：F-001~F-118 共 118 条，其中课程原文 112 条、元信息 2 条（F-113、F-114）、核验补充 3 条（F-115~F-117）、社区反馈 1 条（F-118）。
- **P0 核验**：11 项 → 4 ✅ / 7 ⚠️ / 0 ❌。通过项为方舟 Base URL、模型视觉/GUI 能力、adb 平台机制、体验额度已过期；部分通过项集中于仓库与分支可达性、总管技能仓库、401/404 归因、App 私有目录与热替换、lint/push 输出、提醒行为。
- **敏感度处理**：课程文档托管于企业内部飞书域，本包按用户指定目录落盘；正文与信源层不引用其 URL，不转载课堂体验额度的领取入口、IP 形式服务地址、令牌与个人登记信息（该项已于 2026-11-13 过期），附件与视频令牌不收录。
- **V 审查**：四视角共 10 条意见，采纳 8 条、部分采纳 2 条、不采纳 0 条；采纳项已回归到 00、04、05、06、08 与 index 正文。
- **与 01 课的关系**：同目录兄弟束，01 课讲「装好能用」，02 课讲「按你的习惯改造」；两包在「主题关联」中互链，口径差异（鸿蒙支持范围、确认关卡位置）在核验报告中并列。
- **索引接入**：新增 `jishu/ai/ecosystems/trae/trae-agent-camp-02/`，并同步 trae 分组、ecosystems 分类、ai 域与 bundles 总索引四层计数。
- **模式入库（2026-11-16）**：6 个模式逐条去重后处置——P2 四问成技、P4 证据先行、P5 单产出拆分、P6 双闸门入库为独立模式（L1-draft）；P1 三层改造面并入 `base-first-minimal-customization`，P3 试改验循环并入 `edit-verify-separation`（去重裁定为「核心动作同构」，不新建独立篇目）。库内路径见 `patterns.md` 头部表。

### 门禁记录

| 门禁 | 命令 | 结果 |
|------|------|------|
| toctree 完整性 | `python scripts/check-toctrees.py` | 通过：全部 index.md 引用有效，所有内容文档可达 |
| 总索引计数对账 | `python scripts/check-bundles-index.py` | 通过：9 域 / 65 组 / 739 束，五面一致 |
| UTF-8 编码 | `python scripts/check-utf8.py` | 通过：13360 个文件均为有效 UTF-8 |
| Markdown 链接 | `.agents/scripts/check-links.py --path <bundle>` | 通过：24 个文件零断链（过程中修复 6 处跨目录相对路径） |
| 库规模基线 | `python scripts/check-asset-baseline.py` | 规模数字通过（README 与 doc/index.md 已同步 739）；字节残差为本次 24 篇新增文件（约 149 KB），按脚本要求提交后复跑 |
| Sphinx dummy 构建 | `sphinx-build -b dummy -E doc _build/dummy` | 通过：构建成功，全库 364 条既有警告（与上一轮同量，集中在其他既有束）；本束 0 告警 |

### CMD-LOG

```text
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S0 | event=CMD_START | session=sc-20261116-trae-agent-camp-02 | msg=方法论编排开始：TRAE 训练营第二期 02 课学习与知识包生成 | ctx={"scenario":"knowledge","topic":"trae-agent-camp-02","depth":"standard"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S1 | event=SCENARIO_DETECTED | session=sc-20261116-trae-agent-camp-02 | msg=场景4知识沉淀 | ctx={"chain":"R-I-E-V-C"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S2 | event=CHAIN_SELECTED | session=sc-20261116-trae-agent-camp-02 | msg=链路R-I-E-V-C，含P0核验与四视角审查 | ctx={"gates":["G1","G2","G3","V","G4"]}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S3 | event=GATE_PASSED | session=sc-20261116-trae-agent-camp-02 | msg=G1事实无因果词，118条编号事实 | ctx={"facts":118}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S4 | event=GATE_PASSED | session=sc-20261116-trae-agent-camp-02 | msg=G2洞察四元组完整，5条 | ctx={"insights":5}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S5 | event=GATE_PASSED | session=sc-20261116-trae-agent-camp-02 | msg=G3模式要素完整，6个L1-draft | ctx={"patterns":6}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S6 | event=GATE_PASSED | session=sc-20261116-trae-agent-camp-02 | msg=V四视角10条意见，采纳8条部分采纳2条 | ctx={"adopted":10}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S99 | event=CHAIN_COMPLETED | session=sc-20261116-trae-agent-camp-02 | msg=知识包落盘完成 | ctx={"files":24}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S0 | event=CMD_START | session=sc-20261116-trae-agent-camp-02-pattern | msg=模式沉淀开始：6 个模式去重后入库 | ctx={"patterns":6,"mode":"dedup-then-persist"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S99 | event=CHAIN_COMPLETED | session=sc-20261116-trae-agent-camp-02-pattern | msg=模式沉淀完成：4 篇新建 + 2 篇并入 | ctx={"created":4,"merged":2,"maturity":"L1-draft"}
```
