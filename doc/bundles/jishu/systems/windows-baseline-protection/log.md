# 变更日志

## 2026-11-20 · 建包

- **路由与预检**：按 AGENTS.md 启动协议回读磁盘原文（三个锚点齐备）→ SpecWeave 根 → `projects/AGENTS.md` → `awesome-okf-xs/AGENTS.md` → `.agents/context-routing.md` → `.agents/rules/frontmatter.md` → `.agents/global-core-rules.md`。源 URL 无 code/token/邀请码、未登录可读，判为**公开内容（Public）**；子项目规则「公开内容入 `doc/bundles/`」与用户指定路径一致。
- **落点判定**：主题实体是 Windows 11 系统层安全机制（TPM / 安全启动 / 内存完整性 / 驱动签名），归 `jishu/systems/`。对照 `sheke/industry/` 的收录边界（「技术实现类教程归技术域」）与 `jishu/iot/` 的物联网定位，均未采用。
- **route 决策**：`chaptered-summary`（深度摘要 + 原创改写），**不走逐字转录**；决策写入全部 19 个文件的 frontmatter，可审计。
- **采集**：WebFetch 直取公众号正文；WebSearch 定位微软官方一手 7 源（Windows Experience Blog、Windows IT Pro Blog、Insider build 26340.10013 发行说明、SAC FAQ、SAC overview、应用控制文档、Baseline protection 支持页）与 5 组媒体交叉。

### 七概念链路（知识沉淀 · depth=standard · V 强制）

| 阶段 | 产出 | 质量门 |
|---|---|---|
| **R** | 事实台账两卷 [卷一](references/article-source.md) F-001~F-024 / [卷二](references/facts-mechanism-and-claims.md) F-025~F-048；三类口径 `page_fact` 20 / `official_fact` 21 / `author_claim` 7 | **G1** ✅ 无因果推断词、每条带 `src` 与 `locator`、编号连续无跳号 |
| **I** | [3 条四元组洞察](references/insights-and-pattern.md)：变化在读出方 / 平台退出裁决 / 数字需问口径 | **G2** ✅ 每条含陈述·证据·反常识·行动，证据引用 F 编号 |
| **E** | 模式「读出方优先」（L1 单案例待验证）：6 步做法、4 个反模式、五问检验标准、3 个跨领域迁移 | **G3** ✅ 含适用/不适用边界、反模式 ≥3、迁移 ≥1 |
| **V** | [四视角对抗审查](references/adversarial-review.md)：8 条攻击点、8 条采纳、修复后回归 | **V 门** ✅ 4/4 视角覆盖、≥5 条具体意见、≥2 条采纳 |
| **A** | 6 概念页 + 2 示例页 + 6 参考页 + 4 个 index，共 **19 个文件**，每页 500–5000 字符 | **G4** ✅ 单一职责、页内自洽、相对路径按 bundle 内 `../` 层级 |
| **C** | 两卷索引 + 共享计数文件最小增量编辑；**未执行 Git 提交**（用户未要求） | 见下方「门禁执行记录」 |

- **V 门关键采纳**：A4 要求保留 `examples/`（存在读者可照做的操作，不能按纯分析包处理）；A6 要求以官方一手源为骨架、源文降为切入案例；A7 要求所有「8 项」带首版限定词。
- **机械自查**：F 编号与口径计数由脚本统计（首轮发现手写计数 16/7/1、9/10/5、25/17/6 三处漂移，按真值 14/9/1、6/12/6、20/21/7 修正）；`references/` 页指向同 bundle `concepts/` 的 `../../` 层级错误已批量改为 `../`。

### 核验摘要

- ✅ 官方一手通过 9 项（C1、C2、C4、C7、C8、C9、C12、C13、C14）
- ⚠️ 口径差异 / 部分通过 4 项（C3 操作放大、C5 7/8 口径、C6 时点、C10 名单）
- ❌ 实质勘误 1 项（C11 / E4：把开发者可选 `block` 写成 Adobe 既定策略）
- ⭕ 不采信 2 项（C15 Defender 黑历史、C16 AI 推演）
- 口径分账 E1~E6 并列登记；缺口 G1~G6 不以推测填空

### 已知环境基线（并发 WIP）

- 建包前 `git status` 显示**他方未提交 WIP**：`README.md`、`doc/bundles/index.md`、`doc/index.md`、`doc/bundles/jishu/ai/index.md`、`doc/bundles/jishu/ai/products/index.md` 已修改，另有未跟踪新束 `doc/bundles/jishu/ai/products/univer-office-sdk/`。
- **HEAD** 计数为 **750 束**；工作区因他方 WIP 已为 **751 束**（jishu 552→553、ai 313→314）。本包在此基础上 **+1 → 752 束**，jishu **553→554**，systems **4→5**，组数 65 与域数 9 不变。
- 共享计数文件一律走**精确最小增量编辑**（只改数字与新增一行），**不整文件重写**，避免覆盖他方 WIP。
- 未运行 `generate_index.py` 等全量索引生成器；`index.md` 全部手写。
- 本包未执行 Git 提交，等待用户明确提交请求。

### 未实测

- 未在 Insider 构建 26340.10013 实机查看基线保护设置页；绿盾/黄盾与按钮文案来自 B 类媒体界面走查，预览期 UI 可能调整。
- 各早期伙伴的实际策略档位、2027 GA 覆盖版本均无公开信息，已登记为缺口 G3、G4。

---

## 2026-11-20 · 门禁执行记录

在 `projects/awesome-okf-xs/` 下直接执行底层脚本（`invoke gates.*` 依赖未确认可用）：

| 门禁 | 命令 | 结果 |
|---|---|---|
| UTF-8 | `python scripts/check-utf8.py` | ✅ 13578 个文件均为有效 UTF-8 |
| toctree | `python scripts/check-toctrees.py` | ✅ 全部 index.md 引用有效，所有内容文档均可达 |
| 总索引对账 | `python scripts/check-bundles-index.py` | ✅ **9 域 / 65 组 / 752 束**，frontmatter、计数行、节标题、分组表、toctree 五面一致 |
| 资产基线口径 | `python scripts/check-asset-baseline.py` | ⚠️ **EXIT=1**，唯一失败项 `[行尾归一失效]`，残差 **+184613** 字节 |

### 资产基线红的逐项归因（闭合验算）

> **时点说明**：下列数字为**本记录写入前**的门禁快照；`log.md` 自身也是新增文件，本节写入会等量增加 A 与残差，但不改变归因结构与闭合关系。最终数值以复跑 `python scripts/check-asset-baseline.py` 为准。

脚本检查 0 的触发条件为「工作区存在 CRLF 文件 **且** 归一后字节与 HEAD 残差超容差」；残差即**未提交内容字节**。按 LF 归一逐文件对账：

| 项 | 归属 | 文件数 | 字节 |
|---|---|---:|---:|
| A · 本包新增文件 | 我方 | 19 | +90471 |
| B · `univer-office-sdk/` 新增文件 | 他方 WIP | 16 | +93079 |
| C · `doc/bundles/jishu/ai/products/index.md` 净变化 | 他方 WIP | 1 | +651 |
| D · `doc/bundles/jishu/systems/index.md` 净变化 | 我方 | 1 | +412 |
| **合计** | | | **+184613** = 脚本残差 ✅ 闭合无残差 |

- **我方贡献 90883 字节 / 他方贡献 93730 字节**；无未解释差额。
- 该门其余检查（规模数字单一真相源三处对账、口径漂移、`.spec/` 泄漏守卫）**均通过**——脚本仅报 1 项。
- 按脚本设计，工作区与 HEAD 一致（提交后）时该检查自然通过。**本包未提交**，故不宣称该门转绿；也未为转绿改写任何规模数字、未代提交他方 WIP。

### 自定义机械验收（本包范围内）

| 检查 | 结果 |
|---|---|
| 文件数 | 19（14 内容页 + 4 个 index + 1 个 log） |
| frontmatter | ✅ 14 个内容页 `type` 非空、`route: chaptered-summary` 齐备；`title`/`description` 引号闭合 |
| 原子化页长 | ✅ 1403 ~ 3662 字符，全部落在 500–5000 |
| 相对链接 | ✅ 逐条解析可达，零断链（含 `references/` → `concepts/` 的 `../` 层级修正） |
| F 编号 | ✅ F-001~F-048 连续、无跳号、无重号；区间上界 48 ↔ 统计表 48 ↔ 交叉引用一致 |
| 口径计数 | ✅ `page_fact` 20 / `official_fact` 21 / `author_claim` 7 = 48（脚本统计，非目视） |
| 行尾 | ✅ 本包 19 个文件均为 LF、无 BOM |

> 两处校验器假信号已人工回原文核对并排除：`\s*\S` 正则在命令传输中被吞导致 frontmatter 误报（换字符类后全通过）；F 区间判据把分卷区间 `F-001~F-024` 误判为矛盾（改按全包最大上界对账）。

### 计数同步面

`doc/bundles/index.md`（frontmatter / 计数行 / mermaid / 域节标题 / 分组表 systems 行）、`doc/index.md`、`README.md`、`doc/bundles/jishu/index.md`、`doc/bundles/jishu/systems/index.md` 共 5 个文件、**15 处精确最小改动**；全部采用唯一锚点替换，未整文件重写，他方 WIP 的 ai 组改动（313→314、552→553 等）保持原样。
