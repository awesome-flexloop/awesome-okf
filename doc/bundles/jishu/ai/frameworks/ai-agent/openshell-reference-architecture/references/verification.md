---
type: Reference
title: 关键声明核验与证据边界
description: 可用性、性能、生态、信任边界和审查记录
source: article-source.md
sources:
  - id: ledger
    resource: article-source.md
  - id: blog
    resource: https://blogs.nvidia.cn/blog/openshell-reference-architecture/
  - id: sentry
    resource: https://developer.nvidia.com/blog/inside-nvidia-sentry-secure-ai-agents-at-runtime/
  - id: runtime
    resource: https://docs.nvidia.com/openshell/latest/about/architecture.html
generated: {by: "process:okf-wiki-author", at: "2026-10-27"}
status: draft
stale_after: 2026-12-31
---

# 关键声明核验

核验只确认来源及其表达范围。官方页面之间的互证属于同一厂商文档核对，没有三家独立证据，也没有本次性能或安全实测。核心产出是带条件的架构学习材料，不把宣传成效作为选型结论。

## 日期与版本

| 对象 | 来源口径 | 采用结论 | F 编号 |
|---|---|---|---|
| 参考架构发布 | 英文新闻稿 2026-10-21，GTC 柏林 | 发布事件按英文新闻稿日期记；不臆定中文页面发布日期 | F-001 |
| 现已推出 | 中文链接到公开参考设计 | 参考设计文档已开放，不代表组件全部 GA | F-002、F-012 |
| Sentry 可用性 | planned availability early next year | 2026 年文章语境下计划 2027 年初；不承诺具体日期 | F-011 |
| 软件行为 | `latest` 官方文档 | 2026-10-27 阅读记录，未固定 release/commit；关键短引文见下表，不称完整快照 | F-013～F-030、F-061 |
| DOCA 可实验 | 部分库可在整产品可用前使用 | 库可用不等于 Sentry 全产品已交付 | F-059 |

## 成效与口径

| 声明 | 回源结果 | 教程处理 | F 编号 |
|---|---|---|---|
| Vera 为 x86 的 2 倍 | 技术博客为关键 Agent 工作负载上 up to 2x；本次无独立复现 | 写“厂商自述，限定工作负载，最高值”，不作普遍保证 | F-009 |
| Agent 容量提升高达 20% | 新闻稿厂商自述；未取得完整测试方法或独立原始基准 | 保留为未独立验证声明，不据此算 ROI | F-010 |
| 毫秒级隔离 | Sentry 官方技术叙述，无本次端到端测量 | 不写零窗口，不替代检测时延及业务副作用分析 | F-010、F-044、F-056 |
| OPA 亚毫秒 | 原文依策略复杂度和配置 | 仅是策略评估条件性声明，不等于全系统撤销时延 | F-052 |
| CoreWeave 1.8x 与启动 >3x | 仅取得 NVIDIA 转述 | 不纳入正文性能论证；待原始测试报告及环境说明 | F-060 |

以上成效未验证，不是已证伪。正文的机制判断以参考文档为据，性能结论保持缺口。英文稿额外出现的 Rubin 吞吐倍数不属于本教程事实集，未向正文扩展。

## 官方表态与引文

| 原文短语 | 逐字回验来源 | 中文用法 |
|---|---|---|
| `planned availability early next year` | Sentry 深潜可用性末段 | 计划次年年初，按文章年份解释 |
| `tamper-evident` | Sentry 深潜证据章节 | 篡改可察觉；不译为绝对不可篡改 |
| `depending on policy complexity and configuration` | Sentry 深潜 OPA 段落 | 保留评估时延条件 |
| `up to` | 参考架构技术博客 Vera 性能段落 | 最高值；不省去场景限定 |

黄仁勋引语未整段复制为教程论据；“Rubin 思考、Vera 行动、BlueField 治理”采用标明来源的架构意译。官方描述和教程作者推导在不同页面分层。

## 动态机制证据摘录

以下短引文在 2026-10-27 回读原文后登记。它们能保留关键主张，不能重建整页或替代固定版本；源 URL 与来源 ID 见[信源台账](article-source.md)。

| 来源与章节 | 原文短摘录 | 对应事实 |
|---|---|---|
| runtime / Gateway and Sandbox JWTs | `one run of that sandbox, called a generation` | F-027 |
| runtime / Renewing and revoking | `should set gateway_jwt.ttl_secs so tokens expire` | F-061 |
| runtime / What the agent can see | `Only the same supervisor process can reconnect and resume it.` | F-029 |
| governance / Baseline and Phase I Workspace Controls | `Publishing a data-classification policy is a precondition before turning autonomous agents on.` | F-062 |
| governance / Application session and token revocation | `Cover pending approvals, queued writes, child authority, cached credentials and live connections.` | F-064 |
| operations / Operating Properties | `Consequential writes are human-reviewed, asynchronously.` | F-063 |
| operations / Optional DPU dependencies | `define fail-closed behavior and verify update, rollback and recovery before admission` | F-065 |
| tiers / What changes between tiers | `centralized FinOps integration with budget gates` | F-066 |

## 更新与传播规则

维护者在新版本、实际交付公告或 `stale_after` 到期时复核。F-011 是历史发布计划，不改写成当前 GA；新增连续编号记录实际发布或延期，注明日期和支持范围，再同步范围页、Sentry 页、部署页及根入口。

机制变化逐条核对 F-013～F-030、F-061，对旧事实注明适用阅读时点，用新编号记录新机制及差异。同步引用概念页、验收项和受影响洞察，再复跑编号、链接及导航检查。只刷新日期或局部改词不构成更新完成。

## 生态核验边界

原稿对伙伴使用了不同动词。安全厂商“正在集成”、银行“探索”、制造商“构建”、云商“协作部署”不能统一改为“已经生产交付”（F-006～F-008）。

SAP 原始文章返回 403，不能记作 SAP 独立确认。ServiceNow Arc 的 GA 与 AI Passport 跨软硬件撤销均为 NVIDIA 转述，未回读伙伴公告；不将某伙伴产品 GA 推导成 Sentry GA。

## 方法论记录

- **R/G1**：66 条连续编号事实，设计要求、机制、自述与转述分别标记；因果推导未混入事实表。
- **I/G2**：[洞察与迁移](../concepts/05-insights-and-pattern.md)包含三条四元组洞察。
- **E/G3**：模式“边界先行治理”按单案例 L1 记录，迁移是思想实验，没有多案例成熟度声明。
- **V**：四个独立视角返回 14 条意见（含交叉重复）：2 项 P1、9 项 P2、3 项 P3。下表记录已落实修订；机械门禁结果另记。
- **C**：用户未要求提交或推送，保持工作树交付。

本子项目采用轻量 bundle 流程，不复制主仓规范资产或另建公共 Spec 工作流。事实以 `article-source.md` 单一台账承载，不伪造不存在的第二份事实表或“双份一致”检查记录。

## 四视角修订记录

| 视角 | 攻击点与级别 | 处理 |
|---|---|---|
| 老板 | P1 数据分类前置门遗漏 | 回读 governance，补 F-062 与部署前置门 |
| 老板 | P1 高影响写入人工批准未验收 | 回读 operations，补 F-063 与业务批准验收 |
| 老板、魔鬼 | P2 在途撤销及传播上界缺失 | 补 F-064 与五类存量授权覆盖 |
| 老板 | P2 运维责任、失效关闭及恢复准入 | 补 F-065 与 Sentry、验收表 |
| 老板 | P2 ROI 未计全成本及停止门 | 补 F-066；成本细项和停止条件标作者建议 |
| 魔鬼 | P2 共享部署凭证有效期遗漏 | 回读 runtime，补 F-061、续期和删除验收 |
| 新人 | P2 JWT/generation 与连接未定义 | 软件页分别解释令牌、连接和 sandbox 重启 |
| 新人 | P2 OPA/Rego、SPIFFE/SPIRE 混称 | Sentry 页分别定义引擎/语言、规范/实现 |
| 新人 | P3 缺最小填写例 | 增加非实测职责表与完成判据 |
| 未来、魔鬼 | P2/P3 动态信源缺历史锚点 | 保留逐字短摘录及章节；仍声明未固定整页版本 |
| 未来 | P2 更新缺逐事实传播规则 | 历史计划保留，新事实续号并同步引用页 |
| 未来 | P3 模式晋降级判据缺失 | 明确实际案例计数、L2 条件和反例处理 |

## 机械验证结果

- 显式输入本包全部 12 个 Markdown 文件运行主仓链接检查：最终回验 27 个本地引用存在，frontmatter 路径字段有效；24 个外链未执行自动可达性检查，不将本地通过记为外链通过。
- 子项目 UTF-8 检查：12 文件通过；补充检查确认无 BOM、追踪参数或家目录绝对路径残留。
- YAML、非空 `type`、每条 `sources.resource` 及内部来源路径通过；事实 F-001～F-066 连续且引用不越界，来源条目为 14。
- 调用子项目导航脚本 `run_scan(bundle_root)` 完整局部检查：断链、可达性、目录一致性及 bundle 根检查通过。Agent 组实际 59 束、frameworks 实际 92 束。
- 全库计数对账通过：9 域、63 组、685 束。最终全库导航复查报其他会话的 `gpt-61-sol` 与 `contest-writing-guide` 在途目录：共 6 页不可达及 2 个根 `index.md` 缺失；本包无命中。该结果是检查时点的工作树状态，后续并行写入可能改变。
- 总索引 Mermaid 检查的单文件 CLI 曾扫描 0 文件，未记为通过；改为显式调用检查器 `_process_file`，确认处理 1 个图且无问题。此项是静态规则检查，不是浏览器渲染验收。
- Sphinx 全库 `dummy` 解析已结束，后台任务退出码为 0，完整日志末尾报告 `build succeeded, 285 warnings`；本包路径无 `WARNING:` 或 `ERROR:` 命中。全库其他文档仍有告警与 docutils 错误，不能称全库零告警通过；伪构建器不生成 HTML，未做页面渲染验收。
- 已跟踪变更 `git diff --check` 通过。本包新建文件另经编码与结构检查，不以该命令替代新文件验证。

维持 `draft`：四视角审查与结构验证已经完成，但滚动机制未固定完整版本，性能、伙伴落地和部署验收仍无独立实证。该状态不表示尚未阅读，亦不将文档审查提升为生产安全认证。
