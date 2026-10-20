---
type: Reference
title: Kaggle SAE 来源核验与边界记录
description: 记录来源层级、文档内一致性、注册字段差异、当前服务未知状态及本次只读核验范围。
tags: [Kaggle, SAE, 核验, 时效边界]
generated: { by: "process:sae-bundle-task-2", at: 2026-10-19T00:00:00Z }
verified: { by: "process:fact-register-crosscheck", at: 2026-10-19T00:00:00Z }
status: stable
stale_after: 2026-12-18
sources:
  - id: kaggle-article
    resource: https://www.kaggle.com/blog/standardized-agent-exams
    title: Kaggle Standardized Agent Exams 博文
  - id: kaggle-sae-skill
    resource: https://www.kaggle.com/static/experimental/sae/SKILL.md
    title: Kaggle SAE 官方静态 Skill
  - id: source-register
    resource: /references/article-source.md
    title: 本 bundle 的 F 编号事实清单
---

# Kaggle SAE 来源核验与边界记录

## 核验范围与结论

本次 bundle 以任务提供的 F-001–F-022 事实登记为唯一事实基准；该登记列出 Kaggle 博文 S1 与 Kaggle 官方静态 Skill S2，并记录了各声明的来源章节和证据状态。本文只做事实编号、主张类别、日期及文档间口径的对照，没有新增外部事实，也没有把两份 Kaggle 材料当作独立第三方验证。

当前考试注册、开始、提交、排行榜及成绩服务状态为 **UNVERIFIED**。未请求考试页面或 SAE API；因此既不据此断言服务在线，也不据此断言服务下线。Skill 中的操作与错误处理条款均作为静态文档规则记录，不表示服务端行为已经实测。（F-018、F-020）

## 来源与日期核对

| 项目 | 核对口径 | 处理 |
|---|---|---|
| 博文日期和署名 | 页面标注 2026-04-01，署名 Nicholas Kang。 | 正文将其写作文章发布日期和作者信息，不外推为产品更新日期。（F-001） |
| Skill 日期与版本 | 文件自述版本 1.0.0；`reviewedAt` 和 `lastChangedAt` 均为 2026-09-18。 | 标为 Skill 文件自身元数据，不称为独立版本历史验证。（F-010） |
| 事实清单范围 | F-001–F-022 覆盖两份指定 Kaggle 来源；所有事实编号均保留在 `article-source.md`。 | Concepts 中使用对应编号归因；没有增加事实编号或无来源的产品断言。 |

## 关键声明交叉核对

| 声明 | 结果与证据边界 | 文档处理 |
|---|---|---|
| 首个考试的题数 | 博文与 Skill 均描述 16 题；来源同属 Kaggle，因此只是文档一致，不是独立验证。（F-003、F-013、AN-01） | 表述为来源所描述的题数，并保留对未来版本不外推的限制。（F-022） |
| Reasoning 与 Adversarial Safety | 两个维度及解释来自博文；Skill 仅在开始考试示例中对应 16 题，不能由此补出维度分配。（F-003、F-004、F-021） | 只复述作者对维度的解释，不声称有维度级评分或题目分布。 |
| 不需要 Kaggle 账户 | 博文与 Skill 均有此表述，但不是独立来源互证。（F-007、AN-01） | 标为发布材料/Skill 的说法，不扩展为无需凭据或无需授权。 |
| 注册字段 | 博文称注册只需名称和描述；Skill 示例含 `model`、`version`、`agentType`，且将 `description` 标为可选。服务端是否强制这些字段未知。（F-011） | 明示来源口径差异，不合并成确定的注册字段契约。 |
| 用户确认和计时 | Skill 规定注册前明确确认，并要求告知开始后有 30 分钟倒计时；为文档规则，未实测。（F-012、F-013） | 仅用于说明安全与授权边界，不给出调用步骤或要求用户操作。 |
| 答案提交与次数 | Skill 规定一次提交全部 16 题、未回答计错，并写明每场每 Agent 最多提交 3 次；均为静态规则而非实测行为。（F-014、F-016） | 保留其规则来源和未实测属性。 |
| 凭据域名 | Skill 限定 API key 只发送到 `www.kaggle.com` 的 `https://www.kaggle.com/api/v1/*` 请求头，且不得分享、记录或输出。（F-017） | 明确写为凭据安全规则；bundle 不包含凭据、示例密钥或请求示例。 |
| 结果字段 | `score`、`maxScore`、`percentage`、`passed`、`certificateId` 出现在 Skill 响应示例中，不构成对当前接口响应的实测。（F-015、F-020） | 称为文档示例字段，不推断算法、及格标准或证书有效性。 |
| 可用性、评分与效度 | 当前服务可用性未知；材料没有给出可复核评分算法、及格阈值、信度/效度研究或排行榜统计方法。（F-020、F-021） | 明示 UNVERIFIED / NOT SPECIFIED；不判断在线/下线，不作算法或效度推断。 |

## 勘误与未解决项

- **注册字段差异：**保留为 SOURCE-MISMATCH（F-011），没有证据判断 Skill 示例字段是否是服务端必需字段。
- **当前运行状态：**保留为 UNVERIFIED（F-020）；静态 Skill 的存在和博文发布时的描述都不能证明当前服务可用或不可用。
- **测量解释：**评分算法、题目维度分配、及格阈值、测量信效度和排行榜统计方法均未由指定材料说明（F-021）。`passed` 等字段不能替代这些证据。
- **规则持续性：**首个考试的题数和 Skill 文件版本不得外推为未来持续不变的服务规则（F-022）。
- 指定来源内没有发现需要改写成另一数值的源文错误；这不表示完成了独立服务端核验。

## 结构与安全复核记录

- 所有概念页的产品数字、日期、操作约束和安全规则均附 F 编号，并在 frontmatter sources 中列出相应 Kaggle 官方来源。
- 所有 Skill 行为均以“Skill 规定/文档示例”表述；没有声称已经注册、开始、提交或访问结果。
- 本任务没有调用 SAE API、注册 Agent、启动考试、提交答案或处理凭据。
- 当前 bundle 只含 references、concepts、索引和日志；没有创建 `examples/`。该产品/技术综述不提供经实测、可复现的考试操作流程，因此不满足设立示例目录的两项判据。
- 本段记录生成时，独立 Spec Mode Review 尚未执行；以下 Task 3 结果属于实施者 V 自审，不能替代独立评审。独立 Review 结论应以 Spec Mode 的 `review.md` 为准。

## 2026-10-19 实施 Task 3 V 审查

| 核验面 | 检查与结论 |
|---|---|
| 事实溯源与概念声明 | 将 Spec `facts.md` 与本文件 `article-source.md` 的事实编号集合机械比对：两边均为 22 条，序列完全相同且连续覆盖 F-001–F-022。逐页检查三篇 concept：产品数字、日期、流程、安全规则及未知项均指向相应 F 编号；作者定位和分析判断分别标记 AI/AN 编号，未发现无来源的实质性产品断言。 |
| 来源与时效 | S1 博文、S2 官方静态 Skill 的 URL 与事实登记一致；二者在事实采集时以公开只读方式读取。页面日期 2026-04-01 和 Skill 自述日期 2026-09-18 均保留为来源时点，不外推为服务更新状态。S3 于 2026-10-19 返回 reCAPTCHA；未绕过，也未访问 SAE API，因此当前注册、考试、排行榜及成绩服务继续标为 **UNVERIFIED**。 |
| OKF 结构与 toctree | bundle 共 9 个 Markdown 文件；5 个非保留文档具备 OKF frontmatter。根、`concepts/`、`references/` 索引均列出其内容；`python scripts/check-toctrees.py` 通过，全库 index 引用有效、内容文档可达。 |
| 导航及相对链接 | practice 索引的人类可读条目和 toctree 均指向独立 SAE bundle；evaluation 索引保留原有两个评测 bundle，并以 `../../../standardized-agent-exams/index` 交叉链接 SAE。bundle 内检查 29 条本地 Markdown 链接，断链为 0；相关评测专题链接均可解析。 |
| 操作安全 | concept 仅转述静态 Skill 规则，明确注册前用户同意、API key 仅限 Kaggle 指定域名/路径，不含密钥或请求样例。本任务未调用 API、注册 Agent、开始考试、提交答案、删除数据或处理凭据。 |
| 计数与工作区保留 | `python scripts/check-bundles-index.py` 通过：9 域 / 62 组 / 650 束，计数各面与目录树一致；practice 为 21 束 / 19 个目录，AI 域 252 束，jishu 域 481 束。现有 WorkBuddy 相关变更仍在工作树中，包括 ecosystems 计数 99 及 `workbuddy-library-practice/` 未跟踪目录；没有清理这些文件。 |
| 门禁与构建 | 直接脚本 `check-toctrees.py`、`check-utf8.py`（11828 个文件）、`check-bundles-index.py` 均通过。`invoke gates.toctrees`、`invoke gates.utf8`、`invoke gates.bundles`、`invoke build` 均在任务加载阶段因 `PackageNotFoundError: No package metadata was found for invocations` 失败；未安装依赖。`sphinx-build -b html doc _build/html` 成功，报告 13 条来自其他既有页面的警告，SAE 页面没有构建警告。 |

本记录是实施者基于上述本地对照和命令结果完成的 V 自审，不是独立评审；全库 Sphinx 警告与 Invoke 依赖限制按实际情况保留，未通过修改无关内容消除。
