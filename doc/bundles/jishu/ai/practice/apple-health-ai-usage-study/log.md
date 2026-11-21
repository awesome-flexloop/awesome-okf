# 变更日志（apple-health-ai-usage-study）

> 本文件只追加，不重写。计数遵循「读取现值 → 修改 → 复核」，不使用历史记忆值。

## 2026-11-17 · 建束（公开公告解读，17 文件）

**背景**：用户提供 Apple Newsroom 2026-11-15 官方公告 URL，标注 `@scene#47 创作文档`、`@scene#50 深度研究`、`@skill:seven-concepts-cmd`，要求全面学习后生成 OKF wiki 教程到 `doc/bundles/` 恰当位置。

**阶段记录（七概念场景 4 · 知识沉淀，链路 R→I→E→A→V→C）**：

- **阶段 0 路由与预检**：回读磁盘 `AGENTS.md` 三锚点 → `projects/AGENTS.md` → `projects/awesome-okf-xs/AGENTS.md`（嵌套优先）；内容敏感度判定为**公开内容**（Apple 官方新闻稿，无访问控制参数），子项目规范明确公开内容存 `doc/bundles/`，与用户指定落点一致；vendor 方法论资产预检未命中（非 Skill 创建 / 非子模块协同治理）。
- **R 事实采集**：48 条 F 编号（F-001～F-048 连续）。S1 官方稿全文抓取，S4～S9 媒体交叉比对，S10～S14 背景资料。分七组登记于 `references/facts.md`，G1 门通过。
- **I 洞察**：3 条四元组洞察（I-1 测的是人不是模型 / I-2 研究形态不等于产品发布 / I-3 临床接地双轨），见 `references/verification.md` §四。
- **E 萃取**：模式「公告四层核验」（5 步 / 4 反模式 / 检验标准 / Release Notes 跨领域迁移 / L1 单案例标注），见 `concepts/06-transferable-pattern.md`。
- **A 原子化**：17 文件，按 `concepts/`（7）→ `examples/`（2）→ `references/`（3）三层 + 各级 index + log 组织。7 篇概念页与 2 篇演练均落在 500–5000 字符区间；`references/facts.md`（5,175 字符）与 `references/verification.md`（6,001 字符）属结构化事实/核验台账，按库内同组束惯例保持单文件，不做机械拆分。
- **V 对抗审查**：四视角 8 条意见、采纳 5 条（V-1～V-5），逐条登记正文改写位置；回归对抗通过。
- **C 原子提交**：见下方「提交记录」。

**落点论证**：`doc/bundles/jishu/ai/practice/apple-health-ai-usage-study/`。归类仲裁以读者查找意图为准——`practice/` 已有 `u2flash-free-month`、`deepseek-v41-flash-1017`、`microsoft-mxc-agent-containment` 等多个「官方公告 → OKF 知识包」资讯核验束，与本主题同构；`products/` 收可直接上手的工具教程，`yixue/` 域首页明确限定为中医古籍文献学，均不匹配。库内 Grep 确认无 OpenEvidence / HealthKit / Apple Health 相关束，无重复。

**索引计数（并发撞号，未代改共享台账）**：动手前基线为 741 束（五面一致）；本束落地后，门禁脚本报出的目录树真值为 **746 束**（`jishu` 域 548）。执行期间检测到 4 个并发会话同时建束（共 5 个未跟踪束），共享计数文件已被他方推进到 742 / jishu 545，仍有总数 +4、jishu +3 未对账，**本束的 +1 包含在内**。按「不代改、不代提交他方 WIP」纪律，本会话只做属于本束的最小增量：在直接父索引 `doc/bundles/jishu/ai/practice/index.md` 幂等插入一行表格与一条 toctree 条目，**未改任何计数数字**，未改动 `doc/bundles/index.md`、`doc/index.md`、`README.md`、`doc/bundles/jishu/index.md`、`doc/bundles/jishu/ai/index.md` 的规模数字。统一五面对账留待并发收口会话按目录树真值执行。

**机械门禁结果（2026-11-17 实跑）**：

- `python scripts/check-toctrees.py doc/bundles/jishu/ai/practice/apple-health-ai-usage-study` ✅ **EXIT=0**：本束全部 `index.md` 引用有效，17 个内容文档零断链、零孤立。
- `python scripts/check-utf8.py` ✅ **EXIT=0**：全库 13,473 个文件均为有效 UTF-8。
- 字节级自查 ✅：17 文件 `CR=0`、无 BOM；12 个内容页 `type` 齐备、`okf_version` 仅在 bundle 根；全部相对链接（含跨 4 层指向 `yixue/index.md`）机械点开可达；F-001～F-048 连续无跳号；「48 条」口径在首页 / references 索引 / facts / verification / log 五处一致。
- `python scripts/check-toctrees.py`（全量）⚠️ EXIT=1：16 处，**全部**位于并发在途束 `claude-code-verification/`（尚未挂入父索引），本束 0 处；动手前基线 5 处位于 `life-84000-backup-plan/`，期间由他方自行修复。
- `python scripts/check-bundles-index.py` ⚠️ EXIT=1：3 处计数漂移（frontmatter 742 vs 树 746，差 +4；jishu 节标题 545 vs 548，差 +3；分组表和 545 vs 548，差 +3），由 5 个并发在途束的共享台账半完成状态造成，非本束单独引入。
- `check-asset-baseline.py` **未判定**：该门以 HEAD 为口径，工作区含大量他方未提交内容时恒红，不作通过声明。

**提交记录（C 阶段处置）**：**未执行 git 提交**。子模块工作区同时存在 4 个并发会话的在途束与 9 个共享索引文件的未提交修改，此时提交会代提交他方 WIP，违反项目纪律。本束以「工作区原子化文件集 + 父索引导航可达 + 门禁自证」交付；待并发收口后，由收口会话把本束 17 文件与 `practice/index.md` 增量纳入统一提交，并按目录树真值完成五面计数对账。父仓 gitlink 前移同样留待后续，本次不执行。

**产出文件（17）**：

```
apple-health-ai-usage-study/
├── index.md
├── log.md
├── concepts/
│   ├── index.md
│   ├── 00-study-overview.md
│   ├── 01-four-measurement-axes.md
│   ├── 02-clinical-grounding.md
│   ├── 03-privacy-and-guardrails.md
│   ├── 04-eligibility-and-enrollment.md
│   ├── 05-research-lineage.md
│   └── 06-transferable-pattern.md
├── examples/
│   ├── index.md
│   ├── 01-claim-verification-drill.md
│   └── 02-enrollment-self-check.md
└── references/
    ├── index.md
    ├── facts.md
    ├── source-manifest.md
    └── verification.md
```

**复核要点（后续回访）**：① 研究是否结束、名额与规则是否变化，若变则更新 `stale_after` 与 04 篇；② Apple 是否公布护栏触发条件、数据留存期限与统计方案（U-3/U-4/U-5）；③ 媒体单源的去标识化与 24 小时删除是否获官方确认，若是则把 F-035/F-036 升格；④ 研究结论发布后，四轴测量是否产生公开成果，可另立新束；⑤ 「公告四层核验」模式在下一个公告转化任务中复用后评估是否升级 L2。

## 2026-11-17 · 交付前复测（并发收口后）

- 并发会话在其在途束上完成统一对账，共享计数台账自行推进到目录树真值；本会话全程未代改任何他方 WIP 的数字，也未代提交。
- `python scripts/check-toctrees.py`（全量）✅ **EXIT=0**：全部 `index.md` 引用有效、所有内容文档可达，本束 0 问题。
- `python scripts/check-bundles-index.py` ✅ **EXIT=0**：**9 域 / 65 组 / 746 束**，frontmatter、计数行、节标题、分组表、toctree 五面一致。
- 限定本束路径复测 ✅ EXIT=0；父索引的表格行与 toctree 条目仍在；17 文件 `CR=0`、UTF-8 有效、12 个内容页 frontmatter 齐备。
- 仍未执行 git 提交（4 个并发会话的在途工作仍在工作区，遵循 WIP 隔离）。
