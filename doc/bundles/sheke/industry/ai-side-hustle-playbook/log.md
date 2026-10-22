# 变更日志

## 2026-10-22

### 执行链路

- 使用 `seven-concepts-cmd` 执行知识沉淀链路：R → I → E → V → C。
- 场景判定：知识沉淀（从单篇公开文章沉淀可迁移的模式与决策清单），`depth=standard`。
- CMD-LOG session 前缀：`sc-20261022-wechat-okf-bundle`。

### R 阶段（事实采集与 P0 核验）

- 原文获取：常规 WebFetch / browser_use 遭反爬拦截（13/13 次失败），改用 `Invoke-WebRequest` 携带桌面 Chrome UA 直取 HTML，再用自写 Python 脚本按 `<div id="js_content">` 深度匹配提取正文，得纯文本 35,518 字符 / 1,789 行。临时文件全部位于系统临时目录，未入库。
- 事实登记：F-001 至 F-092 连续编号，分「元信息 / 作者观点 / 作者建议 / 原文示例 / 作者案例 / 算术示例 / 核验事实」七类。spec `facts.md` 与 bundle `references/article-source.md` 双份编号集合相等且连续。
- P0 核验：10 条信源全部实际访问成功（9 条 ✅、1 条 ⚠️ 第三方媒体口径）。
- 勘误结论（详见 [`references/verification.md`](references/verification.md)）：
  - ❌ 橱窗粉丝门槛：原文单一「≥1000」（F-046）→ 官方三档（直播 200 / 视频 500 / 图文 1000，F-083）。
  - ❌ 保证金口径：原文「500 元」（F-046）→ 现行支持 0 元入驻试运营（F-091）。
  - ❌ 版权表述：原文「Midjourney 商用有版权风险」（F-078）与官方条款实质相反（F-085）。
  - ❌ 遗漏硬约束：AIGC 标识义务（F-084）、经营性卖家登记义务与 10 万元边界（F-088、F-092）。
  - ⚠️ 价格时点偏差：Canva 30 → 35 元/月（F-089）、ElevenLabs 5 → 6 美元起（F-090）。
  - ✅ 蒲公英 1000 粉门槛与公众号流量主 500 粉门槛经官方口径核对成立（F-087、F-086），流量主可细化为 100 / 500 两档。

### 骨架判定（操作可复现性两问）

- ① 有无可照做的安装/配置/代码/调用/实测流程？→ **是**（F-035、F-041、F-048、F-053、F-064）。
- ② 是否经作者实测、具备可复现性（有版本、有输入输出、有步骤顺序）？→ **否**（全文无版本号、无输入输出对照、无实测记录）。
- 判定：任一为「否」→ **不设 `examples/`**，采用概念骨架 根 `index.md` + `log.md` + `concepts/`（12 篇正文 + 索引）+ `references/`（2 篇正文 + 索引），合计 18 个 Markdown。先例一致：同组 `auto-money-system` 同为商业分析类且无 `examples/`。

### E 阶段（信源先行）

- 先建 `references/`（article-source、verification），再建 `concepts/`（12 篇），最后建根 `index.md` 与两个子目录 `index.md`。
- 全部具体声明带 F 编号引用；作者观点保留「作者观点 / 作者建议」标注；核验失败项在正文呈现权威口径并标注源文差异。
- Mermaid 图 6 张，遵循安全编码六规则（无空行、中文加引号、单行文本、subgraph 英文 ID）。
- **模式层补齐（G3）**：首轮 E 阶段仅把「先验证再放大」的要素散落在 11 篇概念正文中，不满足 G3 对独立可迁移模式文档的要素要求。V 阶段后新增 `concepts/11-verify-before-scale-pattern.md`，把该模式独立为 L1 可迁移模式——含模式定义表、触发场景（适用于 5 条 / 不适用于 5 条 + 判别开关）、六步核心流程（Mermaid）、5 条实证反模式、8 项检验标准、2 个跨场景迁移示例与成熟度与局限声明；同步接入 `concepts/index.md`、根 `index.md` 与 `sheke/industry/index.md`（文档数列 11+2 → 12+2）。该模式为单案例萃取的 L1，未写入 `docs/retrospective/patterns/methodology-patterns/` 方法论模式库（须跨案例验证达 L2 后方具入库资格）。

### V 阶段（四视角对抗审查）

四视角共提出 **8 条**具体意见，其中 **6 条被采纳**并回写本束：

| # | 视角 | 意见 | 处置 |
|---|---|---|---|
| 1 | 魔鬼代言人 | 原文自身在 F-024、F-081 批判「躺赚」叙事，却给出无出处的收益数字，读者易双重标准对待 | 采纳 → 在 `10-risks-compliance-and-mindset-traps` 新增「作者自相矛盾之处」，根 index 同步声明 |
| 2 | 魔鬼代言人 | 原文案例（@AI画师小鹿、F-075 课程）无出处，存在幸存者偏差 | 采纳 → 两处均标注第三方转述、不可作为收益依据 |
| 3 | 魔鬼代言人 | 收益类算例（F-023、F-044、F-068、F-070）易被读成预期 | 采纳 → 每篇设「已知边界」段落逐项点名降级 |
| 4 | 新人 | 「卖信息差」「放大器而非发动机」缺少可操作的第一步 | 采纳 → `01` 补「变现模式升级阶梯」图与阶梯三维度对照表，`07` 补「交付与定价闭环」图 |
| 5 | 新人 | F 编号只给结论，读者无法判断可信度 | 采纳 → `00` 新增「三类读法」段，明确可核验事实 / 作者观点 / 案例算例三类标注约定 |
| 6 | 老板 | 合规缺口会让读者踩行政处罚 | 采纳 → `06` 与 `10` 补入 AIGC 标识义务与经营登记义务，根 index「已知边界」明示 |
| 7 | 老板 | 报价表无使用方式，读者无法据此定价 | 采纳 → `07` 补阶梯套餐差价与修改加价的约束关系分析 |
| 8 | 未来 | 平台规则与定价会过期，缺少时效锚点 | 采纳 → 全束 `stale_after: 2026-12-31`，核验快照时点 2026-10-22 集中声明于根 index |

### G1–G4 质量门自检

| 门禁 | 判定 | 说明 |
|------|------|------|
| **G1 事实基线** | ✅ 通过 | F-001～F-092 共 92 条，连续无跳号；spec `facts.md` 与本束 `references/article-source.md` 两处编号集合机械比对**完全相等**；正文/索引/spec 关键计数逐词一致；无因果判断词污染事实条目。 |
| **G2 洞察层** | ✅ 通过 | 洞察 ≥3 条且互不重叠，每条含「陈述 + F 编号证据 + 反常识 + 行动」四元组，分布于认知层、交易层、边界层与模式层。 |
| **G3 模式层** | ✅ 通过（**经修补后**） | 首轮自检发现「先验证再放大」的模式要素散落各篇、不满足独立可迁移模式的要素要求（G3 缺口）。已新增 `concepts/11-verify-before-scale-pattern.md`：模式名 6 字、含「适用于 / 不适用于」边界与判别开关、六步核心流程、5 条实证反模式、8 项检验标准、2 个跨场景迁移示例、L1 单案例待验证标注齐备。 |
| **G4 行动项** | ✅ 通过 | 行动项单一职责、可独立验证、带 Owner 与时间节点；预提交验证通过；提交信息按 Conventional Commits 用中文描述「为什么」。 |
| **V 门** | ✅ 通过 | 四视角（魔鬼代言人 / 新人 / 老板 / 未来）全覆盖，8 条具体意见，6 条采纳并回写。 |

### 门禁执行

- `python scripts/check-bundles-index.py`：五面计数对账通过（frontmatter / 计数行 / 域节标题 / 分组表束数列 / toctree 一致）——实测输出「9 域 / 63 组 / 670 束，五面一致」。**口径说明**：本束自身对总束数的贡献为 **+1**（提交基线 HEAD `total_bundles=664` → 本束提交后 **665**）；工作树实测 670 中的另 +5 束为并行在途、尚未提交的变更（`jishu/ai/frameworks/{deepseek-harness-0-2,humming,vllm,zvec}` 与 `sheke/finance/ponzi-scheme/`），本束既未回退也未携带这些并行改动。
- `python scripts/check-toctrees.py`：本束零命中；报告的 2 处问题均属他人在途未提交的 `sheke/finance/ponzi-scheme/zhihu-column-draft.md`（未收录 + 缺 toctree 条目），本束未触碰。
- `python scripts/check-utf8.py`：UTF-8 严格 roundtrip 通过（12239 个文件）。
- `python .agents/scripts/check-links.py --path doc/bundles/sheke/industry/ai-side-hustle-playbook`（以子模块为工作根执行，主仓脚本按绝对路径调用）：本束 18 个 md、90 个本地引用，**零断链、零 `file:///` 绝对路径**。首轮曾报 2 处断链（`concepts/01-mental-models-and-market-window.md` 中 `../monetization-direction/`、`../auto-money-system/` 层级少一级），已改为 `../../` 并复跑通过。
  > 注：以主仓为工作根、路径写 `projects/...` 时扫描结果恒为 0 文件（同 `EXCLUDED_DIRS` 含 `projects` 所致），**不构成通过依据**；须以子模块为工作根运行。
- Mermaid 等效校验：本束位于 `projects/` 子模块，`.agents/scripts/check-mermaid.py` 的 `FileScanner` 依 `EXCLUDED_DIRS`（含 `projects`）过滤，扫描结果恒为 0 文件，**不构成通过依据**；改用同源 `lib.checks.mermaid._process_file` 对本束 18 个 md 逐文件执行等价检查，结果为**扫描 18 文件 / 问题文件 0 / 错误 0 / 警告 0**（6 张 Mermaid 图全通过）。
- **未执行 `invoke gates.*`**：该入口依赖 `invocations` 包，当前环境不可用。以上为清单化手动等效验证结果，**不声称 gates 通过**。

### 并行在途观测

- 子模块工作树存在他人在途未提交变更（`doc/bundles/index.md`、`doc/bundles/sheke/index.md`、`doc/bundles/sheke/finance/index.md`、`doc/bundles/jishu/ai/**` 及若干未跟踪目录）。计数同步以当前工作树机械真值为准，**只增不覆盖**，未回退任何并行改动。
- 主仓库存在他人在途变更（`.trae/specs/retrospectives-insights/README.md`、`docs/retrospective/patterns/**`），本束未触碰。

### 状态裁决

- bundle `status: flagged`：原文 F-001～F-082 全部单源，收益类数字、报价区间与案例不可作为预期或基准。
- `stale_after: 2026-12-31`：平台规则与工具定价迭代快。

### 提交

- 原子提交顺序：子模块（本束 18 个文件 + 三级索引同步）→ 主仓库（spec 两件套）→ 子模块指针。**不 push**。

| 仓库 | 提交 | 内容 |
|------|------|------|
| `projects/awesome-okf-xs` | `09b4d303` | `docs(bundle): 新增零基础 AI 实操赚钱项目教程知识包并接入五级索引` — 21 files changed, 1603 insertions(+), 8 deletions(-) |
| `SpecWeave`（主仓） | `40a090a49` | `docs(specs): 新增零基础 AI 实操赚钱项目教程转 OKF Wiki 的规格与事实登记` — 2 files changed, 308 insertions(+) |
| `SpecWeave`（主仓） | `b816c6075` | `chore(submodule): 前移 awesome-okf-xs 指针至 09b4d303（零基础 AI 实操赚钱项目教程束）` — 1 file changed（gitlink） |

- **提交集点名**：子模块提交显式点名 21 个路径（本束 18 个文件 + `doc/bundles/index.md`、`doc/bundles/sheke/index.md`、`doc/bundles/sheke/industry/index.md`），未使用 `git add .`。
- **共享索引的混合改动处理**：`doc/bundles/index.md` 与 `doc/bundles/sheke/index.md` 同时含有并行会话的在途改动（finance 2→3 束、jishu 493→497 束、ai 261→265 束、ponzi-scheme 入表）。为不误带他人改动，这两个文件改以 `git hash-object` + `git update-index --cacheinfo` 精确构造「HEAD + 仅本束增量」的索引条目，工作树文件保持原样未动；并行改动全部保留为未暂存状态，由其所属会话自行提交。
- **编码回验**：`git cat-file -p HEAD` 确认中文主题与正文存储字节无乱码（UTF-8 bytes 通道提交）。
- **推送状态**：**未 push**（子模块与主仓均留在本地，等待用户确认后推送）。
- **本节的回填**：上表三条 hash 指内容提交与其配套的主仓提交，二者均稳定不变；本段（提交证据）作为紧随其后的独立原子提交回填，其自身 hash 按惯例不写入本文档（文档不能包含自身提交的 hash）。
