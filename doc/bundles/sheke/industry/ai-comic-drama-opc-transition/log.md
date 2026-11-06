# 变更日志

## 2026-11-06

- 使用 `/七概念`（`seven-concepts-cmd`）执行**知识沉淀/方法论**链路：**R → I → E → V → C（入库）**。场景识别依据：全面学习一篇公开文章并沉淀为可迁移教程。
- **启动协议**：从磁盘回读 `AGENTS.md` 原文，确认「启动协议 / 文档边界 / 内容敏感度预检」三锚点；三层路由为根 → `projects/AGENTS.md` → `projects/awesome-okf-xs/AGENTS.md`，并读取 `frontmatter.md`、`global-core-rules.md`、`bundle-structure.md`、`check-bundles-index.py` 等子项目规范。
- **内容敏感度预检**：主源 URL 含 `share_code` / `utm_psn`，判定为**分享追踪参数**而非 `share?code=`、`token=`、`invite=` 类访问控制凭据；文章为公开知乎专栏、无登录墙、正文可完整获取 → **Public**，走标准工作流入 `doc/bundles/`，不进 `playground/`，不创建公共 spec。
- **落位（I/E）**：源文主题是 AI 漫剧产业结构、OPC 与注意力经济，**不是** AI 工具实操教程；按 `doc/bundles/index.md` 判为 `sheke/industry/`「AI 行业与商业趋势」，新建 `ai-comic-drama-opc-transition`，采用 `index.md` / `log.md` / `concepts/` / `examples/` / `references/` 结构。

### R · 事实采集（G1）

- 提取主源全文，登记元信息、章节结构、三位受访者与平台方发言；建立 **F-001~F-062** 台账，连续无跳号、共 62 条。
- 因果句一律改写为陈述句并在「分类」列标 `作者判断`；事实层与主张层分离，按 **A 平台方公开口径 / B 受访者自述 / C 记者判断 / D 假设计算** 四层登记。
- 源文字词瑕疵不进 F 台账，统一移入核验报告 E-01（「人参参与到」「二原来你做一个」「投多少都都做不出头」等）。
- 外部交叉核验覆盖：2026 阅文创作大会时间地点（10-16 杭州）、侯晓楠身份与原话、DramaBuddy 升级 OPC 一站式平台、签约 5000 多个个人及个人工作室、前十大 OPC 年收入破 100 万、REDTEN / 玛尔芙依德（Malfoid）事件、平台侧 4.3 亿元 / +230% / 660 部破千万 / 107 部破亿等并列指标。深链不固化，记录「发布主体 + 指标名 + 时点 + 结论」四元组。

### I · 洞察 / E · 萃取

- 五条洞察均按**四元组**（陈述 / 证据 / 反常识 / 下次行动）书写，并显式给出失效条件；可迁移模式为「要素替代三段式」「瓶颈迁移判据」「总量/分配两层模型」「职能上移检查表」「预测四步降级」。
- **信源先行**：先落盘 `references/`（事实台账 → P0 核验报告 → 信源清单 → 目录索引），再写 `concepts/`，保证每篇洞察都能挂回 F/E 编号。
- **P0 核验**：22 项结论 **✅9 / ⚠️7 / ⭕6 / ❌0**；无确定事实错误，但存在 3 处口径张力与 2 处「把预测写成事实」风险 → 全包 `status: flagged`。
- **E-01~E-12 入库必标勘误**：文本校勘、30 倍人效的部/人口径、总流水与单部爆款分母冲突、「降 90%」抹掉「不止」、预测非事实、亏损率无分母、出海 9 月为预估、假设计算非实测、玛尔芙归属与首发、平台口径主体与时点、总量/分配层面混淆、批量剧/精品剧路线口径。
- **操作可复现性两问**：主文无输入输出样例、无版本、无可复现步骤 → `examples/` 不生成操作型示例或行动建议，只保留**可复算算例**与**判据清单**，并显式标注为编者构造。

### V · 对抗性审查（G2/G3/G4 与 V 门）

四视角 + 编者视角共 **6 条具体攻击意见，采纳 4 条、部分采纳 1 条**：

| 视角 | 处置 |
|---|---|
| 魔鬼代言人 · 两种叙事不独立 | ✅ 采纳：`concepts/04` 增设「利益立场检查」，平台与机构叙事分别标注主体，不合并计为独立印证 |
| 魔鬼代言人 · 平台增长数据与「无生存土壤」冲突 | ✅ 采纳：上升为 E-11，`concepts/03` 建立 L1 总量 / L2 分配两层模型 |
| 新人 · 「内容判断力」易被读成可培训写稿技能 | ✅ 采纳：`concepts/02` 首节即区分生产能力 / 筛选能力 / 可培训性 |
| 老板 · 据「机构无价值」裁撤会忽略非制作职能 | ✅ 采纳：`concepts/04` 增加六项组织职能清单，结论限定回制作环节 |
| 未来 · 「很快」与「3~5 年」时间尺度冲突、预测不可证伪 | 部分采纳：写入 E-05，并在 `concepts/05` 展开四步降级与 2027 事后检验清单 |
| 编者 · 模板化「如何转型 OPC」会把 flagged 预测变成行动指令 | ✅ 采纳：`examples/` 只保留算例与判据，不含建议 |

- G1 事实清单无因果词、G2 洞察四元组完整、G3 模式均给出 ≥1 个非本领域迁移验证、G4 行动项原子化（本场景不产出行动建议，行动项限于「引用纪律」与「事后检验观察项」）。

### C · 原子提交（入库）

- 落盘 **16 个 `.md`**：根 `index.md`、`log.md`、`concepts/` 7 个（index + 00~05）、`examples/` 3 个（index + 01~02）、`references/` 4 个（index + 3 篇参考）。
- 修复 `concepts/01` 与 `concepts/02` 中 `../../examples/` → `../examples/` 的相对路径错误。
- 三级索引注册：分组 `sheke/industry/index.md`（导航表新增一行、`42 束 → 43 束`、toctree 新增条目）、域 `sheke/index.md`（`industry 42 → 43`）、总索引 `doc/bundles/index.md`（`total_bundles / 计数行 / sheke 节标题 / Mermaid / industry 表行`）。
- **计数基线说明**：本次开工前总索引已被并行会话从 712 更新至 713 且五面一致；新 bundle 补齐根 `index.md` 后目录树才计入 1 束，故本次目标为 **714 束 / sheke 92 / industry 43**，以 `scripts/check-bundles-index.py` 的目录树地面真值为准。
### 质量门（收口）

- `invoke` 集合因环境缺 `invocations` 包元数据无法加载（`PackageNotFoundError: No package metadata was found for invocations`）；按仓库既有惯例绕过 invoke，直接运行 `scripts/` 下与 `gates.*` 同一实现的官方脚本。
- `scripts/check-bundles-index.py`：**通过**，9 域 / 64 组 / **714 束**，frontmatter、计数行、节标题、分组表、toctree 五面一致。
- `scripts/check-utf8.py`：**通过**，`doc/` 下 12907 个文件均为有效 UTF-8。
- `scripts/check-toctrees.py`：全量报 **1 处**——并行会话在途束 `doc/bundles/jishu/ai/products/wechat-intelligence-hub` 缺 `index.md`；**本束 16 个文件零命中、全部可达、目录清单一致**。按仓库惯例不修他方在途束，仅在此注记。
- `scripts/check-asset-baseline.py`：本次计数变更引出的「规模数字矛盾」已消除——同步 `doc/index.md`、`README.md`（713 → 714、sheke 91 → 92、industry 42 → 43、合计 713 → 714）；余 1 项「行尾归一失效」为工作区存在大量未提交改动所致（脚本明确要求先提交或 stash 后复跑），非本束引入。
- `scripts/check-section-anchors.py`：全库既存 6500+ 处锚点/路径告警，**本束零命中**。
- `check-utf8` / `check-toctrees` / `check-bundles-index` / `check-asset-baseline` 四个 `--self-test` 探针 **4/4 通过**。
- **环境限制**：`pytest` 与 `sphinx` 未安装 → `gates.redline` 与 `invoke build` 无法在本环境执行；需在装有项目依赖的环境中补跑。
- **手动补充校验**：本束 16 个 `.md`、114 个本地相对链接零断链（含两处 `../../examples/` → `../examples/` 修复）；F-001~F-062 与 E-01~E-12 引用全覆盖且无越界；无 `file://` 或家目录绝对路径泄漏；12 个内容文档 `type` 字段齐备，三层 `index.md` 与 `log.md` 保留文件名无 frontmatter，根 `index.md` 带 `okf_version: "0.2"`。
- 未执行 Git 提交，等待用户明确提交请求。（此为首次入库时状态；后续已由子项目提交 `12efe455` 与主仓指针提交 `94f848331` 闭环。）

### 拓展：单位经济算例进阶（同日，`/七概念` R→I→E→V→入库）

- **触发**：用户要求「/七概念 单位经济算例 可以进一步拓展」。场景仍为知识沉淀/方法论，链路 `R → I → E → V → 入库`，`depth: standard`。
- **启动协议**：再次从磁盘回读根 `AGENTS.md`（三锚点齐备），路由 `projects/AGENTS.md` → `projects/awesome-okf-xs/AGENTS.md`，读取 `seven-concepts.md`、`content-sensitivity-precheck.md`、`frontmatter.md`。内容敏感度判为 **Public**：对象为公开源文 + 已入库公开知识包，产出仍在 `doc/bundles/`，不进 `playground/`。
- **R（复盘）**：核对 `examples/01` 四模块（成本 / 产量×平均单价 / 两种人效 / 假设题敏感性）与 `concepts/03` 两层模型、`references/verification.md` 的 E-01~E-12 及 F-008~F-020、F-034、F-036、F-043、F-044、F-058 台账。
- **I（洞察）**：01 只产出「禁止混算」的禁令；全包最核心的 L1/L2 两层模型在算例层**没有任何正面建模**，E-11 仅以禁令形式出现。缺的是「口径固定后结构如何决定方向」与「什么观测会推翻模型」两层。
- **E（萃取）**：新增 `examples/03-two-layer-unit-economics.md`，符号化推导 `R_total = kA` → `p = kA/(nQ)` → `R_i = kA/n` → `π_i = (kA/n)(1−s) − cQ − F`，给出 `∂π/∂Q = −c < 0`、`∂π/∂n < 0` 与 `h > g` 判定条件；另给成本率阈值 `α* = 0.45`（区间 0.325~0.625）、盈亏平衡 `Q*`、降本/进入者赛跑判据、四条证伪清单、五领域参数替换模板（G3）。
- **V（对抗审查）**：6 条具体攻击、采纳 5 条 + 部分采纳 1 条；最关键两条为「`p − C` 不是会计贡献毛利、须补 H4 前置假设」与「符号参数不得被读成实测」，已落为 §二路径隔离声明与 §八禁用 4/5。
- **A/C（原子化与入库）**：不撑大 01，改新增单一职责的 03 文档；同步 `examples/index.md`（三篇 / 导航表 / toctree / 使用边界）、根 `index.md`（description / 表格 / 阅读地图）、`sheke/industry/index.md`（16→17 篇）、01 与 `concepts/03` 的互链。bundle 数不变，`total_bundles` 与各域束数**无需改动**。
- **边界延续**：`status: flagged`、`stale_after: 2027-04-30` 与全包一致；不新增 F/E 编号（未引入新事实、未发现新勘误），不含任何行动建议。

### 续篇：把「内容判断力」写进方程（同日，`/七概念` 续推）

- **触发**：上一轮收尾提出的开放问题——「`concepts/02` 的内容判断力在两层方程里该改写哪个符号」；用户「继续推进」。
- **I（关键判断）**：要改的不是某个已有符号，而是 **H3 均匀分配假设本身**。`p = kA/S` 已把差异抹平，判断力无位置；它只能落在注意力份额 `φ_i` 上。
- **E 产出**：新建 `examples/04-judgement-as-parameter.md`（**第三条参数化路径 · 份额法**）。`φ_i = θ_i^γ/Σθ_j^γ`、`R_i = φ_i·kA`；J1 `γ=0` 或 `θ` 趋同时退回 03 模块 E 且 `∂π/∂θ=0`（判断力不值钱的可证伪条件）；J2 `∂π/∂θ>0` 与 `∂π/∂Q=−c` 并列 = 02 篇「瓶颈迁移」的偏导数版本；J3 广撒网条件 `kA(1−s)·∂φ/∂Q > c`，推出「判断力越强越不需要多产」；模块 K 三分表对齐 02 篇、模块 L 归一化例题、证伪表与引用边界。
- **V 续篇**：5 条攻击、采纳 4 + 部分采纳 1；与 03 篇合计 11 条攻击、采纳 9 + 部分采纳 2。最关键两条为「`θ` 不得变成能力测评分数」与「权重函数形式为编者任选」。
- **原子化**：同样不撑大 03，另建单一职责补篇；同步 `examples/index.md`（四篇 / 表格 / toctree / 使用边界）、根 `index.md`（description / 表格 / 阅读地图）、`sheke/industry/index.md`（17→18 篇）、03 与 `concepts/02` 互链。`total_bundles` 与各域束数仍不变。
- **边界**：`status: flagged`、`stale_after: 2027-04-30` 一致；不新增 F/E 编号；不提供训练方案、不含行动建议；显式声明三条参数化路径互不代入。

### 接线闭环与质量门（同日收口）

- **接线实做（以 `git diff` 核对为准）**：`examples/index.md` 由「三篇」改「四篇」——新增 `04` 导航表行、toctree 条目 `04-judgement-as-parameter`、阅读顺序补「差异化何时改写方向」、使用边界补 `θ/γ/φ` 符号非实测与三条参数化路径互不代入；根 `index.md` 表格 `示例工具 3 → 4`、阅读地图第 5 步补 `04`；`concepts/03` 相关概念补 `04` 互链；`04` 首段把含混的「03 篇」改为「03 进阶算例」，并新增**编号约定**区分 `examples/03`（H1/H2/H3、模块 E~I）与 `concepts/03`（第一性原理篇），防止混引。此前已写入的 `concepts/02`、`examples/03`、`industry/index.md`（17→18 篇）互链与计数一并复核通过。
- **不新增 bundle**：本轮只在既有 bundle 内加文档，`total_bundles`、`groups`、`domains`、域束数、分组束数**均不变**；唯一索引投影变化是 `sheke/industry/index.md` 中本束文件数 `17 → 18`。共享索引（`README.md`、`doc/index.md`、`doc/bundles/index.md`）刻意不动，避免覆盖并行会话内容。
- **官方门禁**：`check-toctrees.py` **通过**（全部 index 引用有效、所有内容文档可达，`04` 已非孤立文档）；`check-bundles-index.py` **通过**（9 域 / 64 组 / **718 束**，frontmatter / 计数行 / 节标题 / 分组表 / toctree 五面一致）；`check-utf8.py` **通过**（12963 个文件）；`check-asset-baseline.py` 仅余 1 项「行尾归一失效」（残差 `+299491`），**未报「规模数字矛盾」**，即 718 三处规模数字仍一致。
- **残差归属定量核对**：本束未提交/未跟踪文件字节合计 `75448`（73.7 KiB），远小于 299491 字节（≈292 KiB），且其中多为替换型修改而非净增；该项由并行会话在途内容漂移主导，脚本明确要求「先提交或 stash 工作区变更再复跑」，按仓库惯例不代修他方 WIP。
- **自检探针**：`check-toctrees` / `check-bundles-index` / `check-utf8` / `check-asset-baseline` 四个 `--self-test` **4/4 通过**；`check-section-anchors.py` 本束 **0 命中**。
- **本束专项**：18 个 `.md`（16 篇初入库 + 03 + 04），本地相对链接 **0 断链**，内容文档 `type` 字段齐备（三层 `index.md` 与 `log.md` 为保留文件名无 frontmatter，根 `index.md` 带 `okf_version: "0.2"`），`F-001~F-062` 与 `E-01~E-12` 引用**零越界**，无 `file://` 绝对路径泄漏。
- **环境限制（沿用前记）**：`invoke` 因缺 `invocations` 包元数据无法加载，直接运行 `scripts/` 下与 `gates.*` 同一实现的官方脚本；`pytest` 与 `sphinx` 未安装，`gates.redline` 与 `invoke build` 需在装有项目依赖的环境补跑。
- 本轮**未执行 Git 提交**，等待用户明确提交请求。
