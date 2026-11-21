# 变更日志 —— TokenEconomizer 经验驱动的黑盒成本控制

## 2026-11-17 · 初始创建

### 1. 开工前检查

- 目标目录 `jishu/ai/practice/tokeneconomizer-experience-cost-control/` 不存在，按「新建」处理。
- 归属判定：`jishu/ai/practice`。该分组已容纳 `context-optimization`、`token-economy-explosion`、`fable5-cost-optimization`、`microsoft-mxc-agent-containment`、`designer-rsi-procedural-memory` 等成本 / 官方博客 / 论文转化束；本束是微软研究院公开研究博客 + 论文 + 开源仓库的机制解读，无独立生态组织目录，不新建分组。
- 内容敏感度预检：分析对象为微软研究院公开技术博客与公开 arXiv 论文，**公开内容**；子项目 AGENTS.md 明确「公开内容 → `doc/bundles/` 或 `doc/`」，与用户指定落点一致。采用深度摘要 + 原创改写路线，不逐字转录。
- 启动协议：已按磁盘原文回读根 `AGENTS.md`（三锚点确认）、`projects/AGENTS.md`、子项目 `AGENTS.md`、根与子项目 `context-routing.md`、`content-sensitivity-precheck.md`、`frontmatter.md`。vendor 方法论资产预检未命中（本任务不是 Skill 创建 / 子模块协同）。

### 2. 信源获取

| 步骤 | 结果 |
|---|---|
| 微软研究院博客 | 全文抓取，标题、作者、发布日期 2026-11-16、三类浪费与三机制 |
| 论文出版页 | 摘要全文、11 位作者中的署名差异、2026-10 日期 |
| arXiv abs / HTML | arXiv:2610.22732v1（cs.CL，2026-10-15，CC BY 4.0）；HTML 全文 910 KB 下载并本地解析 |
| 表格提取 | 按 `<table>` 结构逐格提取表 1、表 2(a)(b)、表 4、表 6、表 7、表 11、式 (1)–(6)，数字未被 MathML 剥离 |
| 项目页 | 逐步参数（T / n / ρ / γ / λ / k / R / p / β / c / κ）、逐组合数字、九个标注运行入口 |
| GitHub README | 538 行全文；Settings 表、Supported versions、安装命令族、各 agent 降级行为、复现说明 |

> 环境坑记录：本机 `python` 为 Windows 原生解释器，读不到 Git Bash 的 `/tmp` 路径；论文与 README 的中间产物改放工作区绝对路径后解析成功。

### 3. 归属与骨架

- 骨架：`index + concepts/ (10) + examples/ (2) + references/ (4) + 三级 index + log`。
- **设 `examples/`** 的理由：有官方安装 / 状态命令与 `experiments/` 复现 harness，操作可复现性两问至少一问成立；每篇示例显式标注「官方文档转述，本束未实测」。
- 计数规则：本束根目录下直接含 `concepts/`、`examples/`、`references/`，按 `check-bundles-index.py` 的「锚点束」口径计 **1 束**。

### 4. 事实与核验

- F 编号 **F-001 ~ F-110，共 110 条**，单份登记在 `references/article-source.md`；G1 自检：无因果词、逐条带信源定位与口径类型、编号连续。
- P0 核验 **14 组（C1–C14）**，全部通过。
- 口径差异并存登记（不合并抹平）：
  - D-1 泛化降幅四种写法（表 2(b) 逐基准 / 摘要 6.4–21.2% / 博客 6.4–19.6% / README 6–20%）；
  - D-2 参数字母同名异义（论文 `k` `p` vs README `k` `p`）；
  - D-3 默认配置 ≠ 实验全栈（micro-skills 默认 off；插件不自行停止 turn）；
  - D-4 署名 "Chinmay Singh" / "Chandan Singh" 未裁决；
  - D-5 README 徽章 Apache 2.0 与尾部 MIT LICENSE 链接标注不同，未读 LICENSE 文件，不判定；
  - D-6 博客列名 9 人是论文 11 人的子集。
- **三处对账**：区间上界（F-110）、统计表（110 条 / 14 组 / 7 条意见）、交叉引用（根 index、article-source、verification）逐词一致，由机械脚本校验。

### 5. 生成顺序（信源先行）

1. `references/article-source.md`（R / G1）
2. `references/verification.md`（V 记录）、`references/parameter-ledger.md`、`references/glossary.md`
3. `concepts/00` → `concepts/09`（I 三条四元组洞察落在 00；E 模式落在 08）
4. `examples/01`、`examples/02`
5. 三级 `index.md`
6. 根 `index.md`
7. 本 `log.md`
8. 四级索引计数与 toctree 同步

### 6. 方法论链路（seven-concepts-cmd）

| 阶段 | 产出 | 质量门 |
|---|---|---|
| S0/S1/S2 | 场景识别为「知识沉淀」，链路 R→I→E→V→A→C，depth=standard | — |
| R | 110 条客观事实、无因果词、四信源分账 | G1 ✅ |
| I | 3 条四元组洞察（环境是成本控制对象 / 省得多≠砍得狠 / 可逆性比正确性关键） | G2 ✅ |
| E | 「可逆节流」模式：适用边界、5 步、5 个反模式、6 项检验标准、2 个跨领域迁移；标 L1 单案例 | G3 ✅ |
| V | 四视角 7 条具体攻击，采纳 7 条并修正产出 | V 门 ✅ |
| A | 拆为 16 个内容文档，每篇 500–5000 字符，三级 toctree | G4 前置 ✅ |
| C | 文件落盘 + 四级索引计数与导航同步 | 见下节说明 |

**F（第一性原理）未启用**：知识沉淀场景的核心链路不含 F，强行加入属过度工程（compiled-methodology 反模式 #5）。

### 7. V 阶段四视角（摘要）

| 视角 | 攻击点 | 落点 |
|---|---|---|
| 🔴 魔鬼代言人 | 数字全部作者自测、四信源同源、cache-aware 口径依赖计价；合并区间掩盖 ReposVul 低降幅 | 结果页「证据等级」、正文改逐基准数字 |
| 🟢 新人视角 | 「装插件=论文效果」误读；参数字母同名异义 | 速览「先读这一条」、参数分账台账 |
| 🟠 老板视角 | 省的是 token 不是人力、前 6 个任务才回本；示例看似实测 | 投入产出判据表、示例未实测声明 |
| 🔵 未来视角 | 受测版本区间窄，结论易过期 | `stale_after: 2027-02-28`、术语页版本快照 |

### 8. 计数同步口径与并发在途基线（实测后修正，含同日复测）

采集时工作区**不是干净树**，且他方在本次执行期间持续并发写入，因此放弃「全局计数一并改绿」的原计划，改为最小侵入注册：

- **采集时基线**：`HEAD:doc/bundles/index.md` 为 `total_bundles: 741`；当时工作区目录树 **746 束** = 741 + 4 个他方在途束 + 1 个本束；他方彼时把工作区 frontmatter 改为 742（仅计入其 1 束）。
- **他方在途内容**：共享台账 5 个（`README.md`、`doc/bundles/index.md`、`doc/bundles/sheke/index.md`、`doc/bundles/sheke/personal-growth/index.md`、`doc/index.md`）；未跟踪 bundle 4 个（`hf-openrouter-inference-providers`、`apple-health-ai-usage-study`、`claude-code-verification`、`life-84000-backup-plan`）；临时脚本 `.check-life84000.py` / `.rewrite-life84000.py` / `.stage-life84000.py` / `.sync-life84000.py`。
- **本束实际改动范围**：只在 `doc/bundles/jishu/ai/practice/index.md` 幂等插入本束的导航行与 toctree 条目，使本束在全站导航中可达。
- **未改动**：`doc/bundles/index.md`、`jishu/index.md`、`ai/index.md`、`doc/index.md`、`README.md` 及 sheke 相关索引，一律不代改、不代提交（项目纪律：他方未提交 WIP 不代改；勿为转绿改写规模数字）。

**同日复测更新（收口前最后一次核对）**：他方在并发过程中已按目录树真值统一收口全局计数，工作区现状为 `doc/bundles/index.md` frontmatter、`doc/index.md`、`README.md` 均为 **746 束 / 65 组 / 9 域**，`practice/index.md` 为 **35 个知识包 / 33 个目录**；本束的导航行与 `tokeneconomizer-experience-cost-control/index` toctree 条目均仍在（第 18 / 87 行）。因此：

- ✅ `python scripts/check-toctrees.py` 全站**通过**（输出中提及本束 0 次）；
- ✅ `python scripts/check-bundles-index.py` 全站**通过**：9 域 / 65 组 / 746 束，frontmatter、计数行、节标题、分组表、toctree 五面一致，**已含本束**；
- ✅ `python scripts/check-utf8.py` 通过：13473 个文件均为有效 UTF-8；
- ❌ `python scripts/check-asset-baseline.py` 仍失败，行尾归一残差 **+461448**（含本束 21 个未提交新文件 + 他方 WIP）；该门以 HEAD 为基线，工作区含未提交内容时恒红，按纪律「提交后判」，**不声称通过**。

- ⚠️ **提交状态**：用户未要求提交，且工作区含他方 WIP，本束**未执行 git commit**。C 阶段在本任务中的落点为「文件落盘 + 父级导航注册」。
  - **不提交的精确判据**：主暂存区已被并发会话 staged（`life-84000-backup-plan` 全套，以及 `README.md` / `doc/bundles/index.md` / `doc/index.md` 的 746 版），而本束仍是未跟踪 `??`、直接父级 `practice/index.md` 仍是未 staged 的 ` M`。直接 `git commit` 必夹带他人 WIP；即便用 `GIT_INDEX_FILE` 隔离提交，对方随后基于其旧 index 提交也会把本束父级的表格行**覆盖回退**。并发双方都不提交是当前正确态，应等对方落地后再基于新 HEAD 提交本束，或由用户授权一次性收口。
- **提交后待办**（原「提交前待办」的计数与 toctree 两项已由他方收口，仅剩基线门）：在工作区变更提交后复跑 `check-asset-baseline.py`；若仍红，须用 `git clone --local` 干净克隆在提交态复跑自证（EXIT=0／残差 +0），不能只写「他方 WIP」就归因结案。

### 9. 机械门禁记录

| 检查 | 方法 | 结果 |
|---|---|---|
| UTF-8 / BOM / 行尾 | 字节级脚本：全部新增 .md 以 UTF-8 解码、无 BOM、统一 LF | 见本日志末尾补记 |
| frontmatter 闭合 | 每个非保留文件首块 `---` 成对，`type` 非空 | 见末尾补记 |
| F 编号连续与三处对账 | 正则 `^\|\s*F-(\d{3})\s*\|` 提取，比对 001–110 与三处统计数字 | 见末尾补记 |
| 相对链接可达 | 正则提取 Markdown 链接，逐一解析路径 | 见末尾补记 |
| 三级 toctree 完整 | `python scripts/check-toctrees.py` | 见末尾补记 |
| 总索引计数对账 | `python scripts/check-bundles-index.py` | 见末尾补记（含他方 WIP 归因） |
| 概念页原子化 | 每篇 500–5000 字符 | 见末尾补记 |

#### 9.1 实测结果（补记，2026-11-17）

| 检查 | 命令 / 方法 | 结果 |
|---|---|---|
| 字节级自查 | 21 个 .md 逐字节：UTF-8 可解码、无 BOM、纯 LF；非保留文件 frontmatter 成对且含 `type` + `status` | ✅ 通过（`log.md` 是 OKF 保留文件，与库内其他 bundle 一致不带 frontmatter，豁免此项） |
| 结构不变式 | `.agents/scripts/check-line-form.py --path <本束>` + 围栏配对自测 | ✅ 0 处行合并故障 / 行首标记残缺；围栏数全偶 |
| 概念页原子化 | 10 篇 concepts 字符数 | ✅ 2717–4126，全部落在 500–5000 |
| 相对链接 | 剔除行内代码 span 与围栏块后提取 Markdown 链接，逐一 `resolve().exists()` | ✅ 78 条相对链接，0 处断链 |
| F 编号 / 三处对账 | 正则 `^\| F-(\d{3}) \|` 全束提取 | ✅ 110 条连续 F-001~F-110、无缺口；根 index / 事实清单 / 本日志一致 |
| 章节锚点 | `python scripts/check-section-anchors.py <本束路径>`（位置参数限定路径） | ✅ 21 文件全部章节锚点可解析；全库存量告警不计入本束（该门不在 `gates.all` 内） |
| UTF-8 门 | `python scripts/check-utf8.py` | ✅ 初测 13472 个 → 复测 13473 个文件均为有效 UTF-8 |
| 本束导航 | `python scripts/check-toctrees.py <本束路径>` | ✅ 引用有效、内容文档全可达 |
| 全站 toctree | `python scripts/check-toctrees.py` | 初测 ❌ 49 处（提及本束 0 次）→ **复测 ✅ 通过**：他方收口后红项清零 |
| 总索引对账 | `python scripts/check-bundles-index.py` | 初测 ❌ 差 +4（742 vs 树 746）→ **复测 ✅ 通过**：9 域 / 65 组 / 746 束五面一致，已含本束 |
| 资产基线 | `python scripts/check-asset-baseline.py` | ❌ 初测残差 +392048 → 复测 +461448；工作区含未提交内容，按纪律「提交后判」，不声称通过 |

**初测全站红项逐条归因**（当时不虚报「门通过」）：
- `hf-openrouter-inference-providers`、`apple-health-ai-usage-study`、`claude-code-verification`、`life-84000-backup-plan` 四束的内容文档未注册到各自父级 toctree；
- `claude-code-verification/index.md` 的 toctree 引用了不存在的 `log`；
- `practice/index.md` 两条「缺失条目」明确点名 `apple-health-ai-usage-study/index` 与 `claude-code-verification/index`，均为他方束；
- 本束已注册到 `practice/index.md` 表格与 toctree，独立门禁通过；全站输出中提及本束 **0 次** ⇒ 红项与本束无关。

> **复测结论**：他方收口后，全站 toctree 与总索引五面对账均已转绿，746 束口径已包含本束；本束**未引入任何新断链或结构错误**。唯一未通过项为 `check-asset-baseline.py`，原因是工作区仍含未提交内容（本束 21 个新文件 + 他方 WIP），属「提交后判」的门，需在提交态用干净克隆复跑自证，不能只写「他方 WIP」就归因结案。

### 10. 后续复核

- 触发：arXiv 出现 v2；仓库 Settings / 支持矩阵变更；出现独立第三方复现；`stale_after: 2027-02-28` 到期；常用 agent 版本超出术语页快照。
- 重点：复核表 1/表 2 数字是否修订、D-4 署名差异是否澄清、D-5 许可证是否统一、插件默认开关是否改变。
