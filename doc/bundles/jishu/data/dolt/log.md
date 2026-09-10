# Dolt Bundle 生成日志

> 记录本 bundle 的完整生成过程，供审计与回溯使用。

---

## 任务元信息

| 项目 | 内容 |
|------|------|
| 方法链 | seven-concepts-cmd 场景 4：R→I→E→V→C |
| 质量门 | G1（事实无因果词）→ G2（洞察四元组）→ G3（模式可迁移）→ G4（行动项原子化） |
| 来源博文 | 《数据库也能像 Git 一样进行 fork、branch 和 merge 吗？》，公众号「开源日记」，2026-06-18 |
| 来源 URL | https://mp.weixin.qq.com/s/ES_KncqKLiQxIzaEZ-58gg |
| 归属路径 | `jishu/data/dolt/`（data 分组直挂束，与 pydata 子组同级） |
| 生成时间 | 2026-09-08 |

---

## 执行步骤

### R 阶段（事实采集）

#### R-1 博文全文提取
- **时间**：2026-09-08
- **方法**：browser_use 子代理提取 `#js_content` innerText
- **原因**：微信反爬（WebFetch 13/13 均被拦截）
- **产出**：`.trae/specs/okf-wiki-ecosystem/dolt-okf-wiki/article-source-raw.md`
- **标题差异说明**：URL 锚点标题为"数据库也能像 Git 一样进行 fork、branch 和 merge 吗？"，正文实际显示标题为"数据库也能 Git 了，比备份更香了。"——两者为同一文章的不同标题层次，以正文实际显示为准

#### R-2 F 编号事实采集
- **数量**：59 条（F-001 ~ F-059）
- **产出**：`.trae/specs/okf-wiki-ecosystem/dolt-okf-wiki/facts.md`
- **G1 预检**：全部事实句无因果推断词，作者观点显式标注
- **P0 候选**：9 项（F-007/F-011/F-013/F-014/F-024/F-026/F-042/F-043/F-045）

#### R-2b 二轮补充事实（2026-09-09 回查原文补登）
- **动作**：逐句回查 `article-source-raw.md`，比对首轮 60 条事实，补登遗漏的机制细节、工作流对比与作者实测体验
- **新增数量**：10 条（F-061 ~ F-070）
- **新增内容**：
  - 机制细节：行级提交粒度（F-061）、who/when 审计（F-062）、全变更链（F-063）、版本控制底层追踪（F-070）
  - 工作流对比：分支替代数据复制（F-064）、传统改错痛点（F-069）
  - 作者观点/实测：Workbench 对分析师友好（F-065）、绝大多数客户端直连（F-066）、建表/插数据/commit（F-067）、TablePlus/DBeaver 操作自然（F-068）
- **P0 核验**：无新增 P0 声明（F-066 系 F-013 已核验协议兼容性的作者概括）
- **双份登记**：facts.md 与 article-source.md 同步补登至 F-070，信源距离分布表更新为 59 客观事实 + 10 作者观点 + 1 官方源 = 70 条
- **正文落实**：concepts/00（F-066~F-069）、concepts/01（F-061~F-064、F-070）已补充引用

#### R-4 三轮补充事实（2026-09-09 三轮回查原文补登）
- **动作**：三轮回查 `article-source-raw.md`，补登溯源完整性与信息架构事实
- **新增数量**：2 条（F-071 ~ F-072）
- **新增内容**：
  - F-071：博文微信列表页/分享标题"数据库也能 Git 了，比备份更香了。"（区别于 H1 标题，标题双版本溯源）
  - F-072：博文核心功能以五个编号块组织（01 行级历史追踪 / 02 分支工作流 / 03 AI Agent 安全操作 / 04 Workbench 可视化 / 05 MySQL 协议兼容）
- **P0 核验**：无新增 P0 声明（均为 P2 级元信息/结构事实）
- **双份登记**：facts.md 与 article-source.md 同步补登至 F-072，信源距离分布表更新为 61 客观事实 + 10 作者观点 + 1 官方源 = 72 条
- **正文落实**：三轮补充为元信息/结构类事实，不涉及 concepts 正文改写

#### R-5 源码事实采集（2026-09-09 基于本地 DoltHub 源码）
- **信源**：用户克隆 `dolthub` 组织源码至 `external/dao/action/DoltHub`，含 12 个仓库（dolt/cli/dolt-mcp/dolt-workbench/doltgresql/doltlite/doltlite-android/doltlite-python/driver/dumbodb/go-mysql-server/vitess）
- **动作**：读取各仓库 README + 存储引擎源码（`go/store/prolly/doc.go`、`go/store/datas/doc.go`、`go/store/nbs/README.md`、`go/serial/commit.fbs`）+ MCP 工具实现，系统采集源码事实
- **新增数量**：13 条（F-073 ~ F-085），信源距离 ① 官方源码
- **新增内容**：
  - 产品矩阵（5 条）：12 仓库生态（F-073）、Doltgres Beta（F-074）、DoltLite（F-075）、DumboDB（F-076）、driver（F-077）
  - 存储引擎架构（4 条）：Prolly Tree/NodeStore（F-078）、NBS（F-079）、Commit flatbuffer（F-080）、Noms 渊源（F-081）
  - 机制澄清（4 条）：MySQL 兼容基于 Vitess（F-082）、客户端 8.4（F-083）、MCP 40+ 工具（F-084）、Workbench Agent Mode（F-085）
- **信源升级**：从 ③ 第三方综述 → ① 官方源码（第一手），产品矩阵从 6 个扩展为 12 个生态组件、4 种数据库协议
- **正文落实**：concepts/00 扩展产品矩阵 + 澄清 MySQL 兼容；concepts/01 深化存储引擎架构 + MCP 三方言；concepts/02 补充多协议生态趋势

#### R-3 P0 权威核验
- **方法**：WebSearch + 官方文档/GitHub README 交叉验证
- **结果**：
  - F-007（Stars 23K）：✅ 时点值合理
  - F-011（Apache-2.0）：✅ 官方确认
  - F-013（MySQL 5.7 兼容）：✅ 官方确认
  - F-014（端口 3306）：✅ 官方确认
  - F-024（MCP Server）：✅ 官方仓库存在
  - F-026（Workbench）：✅ 官方仓库存在
  - F-042（Sysbench 接近 MySQL）：⚠️ 口径需细化（实际读写已超越）
  - F-043（TPC-C 54%）：✅ 数值准确（54.4%）
  - F-045（1G 阈值）：❌ **勘误**——混淆 Web UI 限制与数据库能力

- **勘误补充**：新增 F-060，引用 2021-05-26 官方博客原文
- **产出**：`references/verification.md`

#### R-3b 二轮 P0 复核与 P1 能力声明核验（2026-09-09）
- **P0 计数修正**：首轮误将 F-042（Sysbench）与 F-043（TPC-C）合并计为 1 项，实际为 **9 项 P0**（非 8 项）；全库文档计数已统一修正
- **二轮 P0 分级复核**：逐条扫描 F-061~F-070，判定无数字/日期/官方表态/成效数字类 P0 声明（5 条 P1 能力声明 + 5 条 P2 背景/观点）
- **P1 能力声明核验**（WebSearch 官方源）：
  - F-061（行级提交）、F-062（who/when 审计）、F-063（全变更链）→ 官方 `dolt_history_$TABLENAME` 系统表确认 ✅
  - F-070（版本控制底层）→ 官方 Commit Graph 文档（Prolly Tree 存储引擎原生实现）确认 ✅
  - F-064（分支替代复制）→ 官方 README "fork/clone/branch/merge" 确认 ✅
- **结论**：5 项 P1 能力声明均与官方文档一致，博文转述准确，无编造或夸大
- **产出**：verification.md 追加「二轮 P0 分级复核」与「P1 能力声明核验」两节

### I 阶段（知识拆分）

#### I-1 骨架判定
- **一问**（有读者可照做的安装/配置/代码/调用流程？）：博文含命令但无完整实测记录 → 部分满足
- **二问**（经作者实测、有版本/输入输出/步骤顺序？）：博文称"我试了一把"但无具体版本/输出 → 否
- **结论**：两问均未完全满足，**不设 examples/**，定位为"技术综述/产品介绍"
- **归属判定复核**（候选位置对照表）：
  - `jishu/data/`（数据科学）：✅ 采纳——Dolt 主线实体是"版本化 SQL 数据库"，核心是数据管理；data 分组已有 PyData 科学计算栈，语义贴切
  - `jishu/dev/`（开发与协作工具）：❌ 否决——dev 的 Git/GitHub 面向"代码版本控制"，Dolt 面向"数据版本控制"，服务对象不同；Dolt 是数据库而非开发工具
- **产出**：三层知识拆分定稿，落 `jishu/data/dolt/` 直挂束（与 pydata 子组同级）

#### I-2 三层知识拆分
- **发布事实层**（What）：概念 00 —— 产品定位/功能/矩阵/生态
- **机制原理层**（Why/How）：概念 01 —— Prolly Tree/历史视图/分支合并/MCP
- **边界趋势层**（Boundaries）：概念 02 —— 性能限制/勘误/适用场景/选型启示

### E 阶段（信源先行生成）

#### E-1 信源先行
- 先写 `references/article-source.md`（F-001~F-072 双份登记，其中 F-061~F-070 为二轮补登、F-071~F-072 为三轮补登）
- 再写 `references/verification.md`（核验报告+勘误四清单）
- 最后写 concepts/ 与根 index.md

#### E-2 正文生成
- 概念 00：Dolt 概述与产品矩阵
- 概念 01：行级版本控制机制
- 概念 02：边界、限制与选型建议
- 根 index.md：导航 + 骨架判定说明 + 信任与生命周期说明
- references/index.md：信源索引

### V 阶段（对抗审查）

#### V-1 机械门禁自检

| # | 检查项 | 结果 | 说明 |
|---|--------|------|------|
| 1 | UTF-8 strict roundtrip | ✅ | 9 个文件均通过 |
| 2 | F 编号双份一致 | ✅ | facts.md 85 条 = article-source.md 85 条（F-001~F-085 唯一编号集合一致，博文 72 条 + 源码 13 条） |
| 3 | toctree 完整 | ✅ | 根/concepts/references 三级均已生成 |
| 4 | 无绝对路径引用 | ✅ | bundle 文件内无绝对路径引用（file 协议与本地绝对路径均零出现） |
| 5 | 敏感路径零残留 | ✅ | 同上，已清理 log.md 描述避免误报 |
| 6 | 三级计数同步 | ✅ | jishu/index.md data 行 `| 10 |`；bundles/index.md total_bundles: 510，文字已修正为 510 |
| 7 | 根 index frontmatter 完整 | ✅ | okf_version/type/title/status/stale_after/sources/verified 均存在 |
| 8 | 勘误在正文落实 | ✅ | F-045 勘误表位于 concepts/02 第22-33行，勘误提示框位于 index 第62行；F-042 口径细化位于 concepts/02 第16行 |

**总计**：8/8 通过 ✅

**注**：V-1 自检表格检查项描述曾含绝对路径前缀字面量，导致机械门禁 Grep 自指误报，已改为中性表述；bundle 正文无任何实际违规引用。

#### V-1b 四视角对抗审查

**读者视角**（能否直接理解并应用）：
- 优点：学习路径建议清晰（入门→进阶→溯源），导航层次分明
- 问题：无 examples/（骨架判定已说明原因，两问未完全满足），读者无法获得"照做"的实操记录——这是博文性质决定的，非知识包缺陷
- 改进建议：可在后续迭代中补充社区实测案例至独立的 examples/ 目录

**编辑视角**（格式与结构规范性）：
- OKF v0.2 frontmatter 完整，tags 合理，generated/verified 时间戳正确
- toctree 三级结构完整，noexamples/ 目录存在但为预期行为
- 勘误提示框置于根 index 第62行，醒目且易于发现
- 事实编号（F-001~F-085）贯穿所有文档，引用一致

**技术专家视角**（事实准确性与深度）：
- P0 声明 9 项核验覆盖率达 100%，其中 F-042/F-045 两处偏差已识别并纠正
- F-045 勘误引用 2021-05-26 官方博客原文，区分了 Web UI 限制与数据库能力
- F-042 补充了 Sysbench 读写已超越 MySQL 的更新数据（read mult 0.83，write mult 0.91）
- MCP Server 与 Workbench 均已通过官方仓库核验（✅）
- 性能数据时效性标注合理（stale_after 设为 2026-12-31）

**审计员视角**（溯源完整与可审计性）：
- 所有事实编号均可追溯至 article-source.md，无悬空 F 编号
- verification.md 提供勘误四张清单，来源明确可复现
- 信源距离分布：③第三方综述 71 条（61 客观事实 + 10 作者观点）+ ①官方发布 1 条（F-060 勘误补充）+ ①官方源码 13 条（F-073~F-085），合计 85 条；P0/P1 核验信源覆盖 GitHub/docs.dolthub.com/本地源码
- log.md 记录完整生成链路，支持事后审计

#### V-2 索引接入（已完成）
- `jishu/data/index.md`：导航表新增 dolt 条目 ✅，toctree 追加 `dolt/index` ✅
- `jishu/index.md`：data 行束数 9 → 10 ✅
- `bundles/index.md`：total_bundles 509 → 510 ✅（frontmatter 与正文文字均同步）

### C 阶段（原子提交）
- **顺序**：①子模块 bundle+索引 ②主仓库 spec ③主仓库子模块指针
- **规范**：Conventional Commits，不 push

---

## 独立审查（Task 10 — fresh context）

### AC-10：知识拆分与洞察质量（rubric）

| 维度 | 评估 | 证据 |
|------|------|------|
| 事实/机制/趋势三层清晰 | ✅ | concepts/ 三篇分别对应：发布事实层（00）、机制原理层（01）、边界趋势层（02）；concepts/index.md 明确"三层递进"路径 |
| 事实与观点显式分层 | ✅ | F-059 标注"作者观点"；概念 02 第67-74行"作者观点汇总"表格，编号/观点/性质三列 |
| 趋势与选型启示有分析增量 | ✅ | "Git 理念向数据领域延伸"三段分析（开发体验一致性/数据实验沙箱/AI Agent 友好）、"行业趋势观察"定位 Dolt 从单一产品向"数据版本控制平台"演进 |
| 超出原文的独立贡献 | ✅ | F-045 勘误（澄清 Web UI 限制≠数据库能力）、F-042 口径细化（补充 Sysbench 读写超越 MySQL 数据） |

**评分**：**4/5**（三层结构完整、事实观点分离清晰、有独立分析增量；距 5 分差距在于概念 02 趋势层可进一步深化多项目横向对比）

---

### AC-11：读者可用性（rubric）

| 维度 | 评估 | 证据 |
|------|------|------|
| 中文表达流畅 | ✅ | 全文无机翻痕迹，术语中英文对照恰当（如 Prolly Tree 保留英文原名并解释） |
| 表格/列表结构得当 | ✅ | 产品矩阵表、适用场景评分表、作者观点汇总表、勘误对照表均格式规范 |
| 根 index 导航完整 | ✅ | 核心概念导航 + 信源与核验导航 + 学习路径建议三步走 |
| 信源与时效边界一目了然 | ✅ | frontmatter 含 sources/stale_after/verified；根 index 第62行勘误提示框醒目 |
| 无断链/乱码 | ✅ | 所有内部相对链接指向存在文件 |

**评分**：**5/5**（表达流畅、结构清晰、信源与时效完整、勘误提示醒目）

---

### 独立审查结论

| AC 项 | 评分 | 是否通过 |
|-------|------|---------|
| AC-10（知识拆分与洞察质量） | 4/5 | ✅ >= 4 |
| AC-11（读者可用性） | 5/5 | ✅ >= 4 |

**Bundle 质量状态**：符合规范，可进入 C 阶段提交。

---

## G 质量门检查记录

| 质量门 | 检查项 | 结果 |
|--------|--------|------|
| G1 | 事实句无因果推断词 | ✅ 全部通过 |
| G2 | 洞察四元组（现象+根因+影响+建议） | ✅ 概念 02 实现 |
| G3 | 模式可迁移/信源先行 | ✅ references/ 先于 concepts/ |
| G4 | 行动项原子化 | ✅ 勘误 F-060 独立登记 |

---

## 勘误摘要

| 编号 | 原文 | 问题 | 正确值 | 来源 |
|------|------|------|--------|------|
| F-045 | "超过 1G 数据会变慢" | 误读：将 Web UI 限制泛化为数据库能力 | 该限制仅适用于 DoltHub Web UI 浏览器查询（2021 年过时信息），Dolt 生产环境可处理 TB 级数据 | F-060 / [dolthub.com/blog/2021-05-26-dolt-web-ui/](https://www.dolthub.com/blog/2021-05-26-dolt-web-ui/) |
| F-042 | "Sysbench 接近 MySQL" | 措辞保守 | Sysbench 读写基准实际已超越 MySQL（read mult 0.83，write mult 0.91） | [dolthub.com/latency-benchmarks](https://www.dolthub.com/latency-benchmarks) |

---

## 深化扩展（2026-09-09）

> 用户要求使用 seven-concepts-cmd + source-code-to-okf-wiki Skill，基于本地 `dolthub/dolt` 主仓源码（HEAD 65bd3306b0，tag v2.3.2）生成 OKF wiki 分层全景教程，深化扩展现有 dolt/ 束。

### 决策记录

| 决策项 | 选择 | 理由 |
|--------|------|------|
| 束归属 | 深化扩展现有 dolt/ 束 | 与既有 dolthub-cli/dolt-mcp 并列，保持知识连贯性 |
| 覆盖深度 | 分层全景教程（CLI → SQL → 存储内核） | 博文层仅覆盖产品认知，源码层补全实现细节 |
| 提交策略 | 完成后原子提交到 awesome-okf-xs | 遵守子模块提交规范 |

### R 阶段（源码事实采集）

- **动作**：三组并行子代理分别采 CLI 层/SQL 版本控制层/存储内核层源码事实
- **信源**：本地 `d:\spaces\SpecWeave\external\dao\action\DoltHub\dolt` 主仓（HEAD 65bd3306b0，tag v2.3.2）
- **新增数量**：107 条（F-086~F-192），信源距离 ① 官方源码
- **核心发现**：
  - CLI 层：main() 两行体、三组白名单（22/10/6 项）、DoltEnv 惰性加载、RefType 常量体系、Hash base32 {0-9,a-v}
  - SQL 层：dprocedures(38)/dfunctions(10)/dtablefunctions(13) API 体系、HistoryTable 分区模型、三种冲突类型
  - 存储层：NBS 内容寻址 DAG、Prolly Tree NodeStore/StaticMap/MutableMap/AddressMap、21 个 .fbs 文件、Commit 高度算法
  - 生态层：DoltDB struct + Resolve 系列 API、12 仓库生态工作流、AGENT.md 源码阅读指南
- **产出**：`references/source.md`（F-086~F-192 登记，29 章节）

### I 阶段（骨架判定更新）

- **一问**（有读者可照做的安装/配置/代码/调用流程？）：✅ 满足——examples/ 四篇提供完整源码对照工作流
- **二问**（经作者实测、有版本/输入输出/步骤顺序？）：当前环境未安装 dolt，示例以源码对照形式呈现（非实测输出）
- **结论**：bundle 从"技术综述"升级为"分层全景教程"，保留 examples/ 目录（源码对照形式）

### E 阶段（生成）

| 产出 | 路径 | 对应 F 编号 |
|------|------|------------|
| 源码事实登记 | `references/source.md` | F-086~F-192 |
| CLI 命令层概念 | `concepts/03-dolt-cli-architecture.md` | F-086~F-111 |
| SQL 版本控制层概念 | `concepts/04-sql-version-control-api.md` | F-112~F-153 |
| 存储内核层概念 | `concepts/05-storage-kernel-architecture.md` | F-157~F-182 |
| 生态与工作流层概念 | `concepts/06-dolt-ecosystem-and-workflows.md` | F-183~F-192 |
| CLI 工作流示例 | `examples/00-cli-workflow.md` | F-086~F-111 |
| SQL 版本控制示例 | `examples/01-sql-version-control.md` | F-112~F-153 |
| 分支合并工作流示例 | `examples/02-branch-merge-workflow.md` | F-112~F-156 |
| 系统表与测试示例 | `examples/03-system-tables-and-testing.md` | F-157~F-192 |
| 索引更新 | `concepts/index.md`、`references/index.md`、`examples/index.md`、`index.md` | — |

### 文件变更摘要

- **新增文件**（9 个）：`references/source.md`、`concepts/03~06.md`、`examples/00~03.md`、`examples/index.md`
- **更新文件**（4 个）：`concepts/index.md`（3→7 篇）、`references/index.md`（+source.md）、`index.md`（骨架判定更新 + examples 导航）、`log.md`（追加深化扩展记录）
- **隔离变更**：不修改 `dolt-mcp/` 束（WIP 竞态风险），仅修改 dolt/ 束及相关索引

---

## G 质量门检查记录
