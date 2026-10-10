---
type: Reference
title: "LIFT 评测资料来源台账"
description: "登记微信公众号文章、LIFT 官方仓库与论文、相关基准的访问状态和支撑范围。"
status: stable
stale_after: 2026-12-31
generated: { by: "reference_agent", at: 2026-10-10T11:38:56+08:00 }
verified: { by: "process:seven-concepts-r", at: 2026-10-10T11:38:56+08:00 }
sources:
  - id: blog
    resource: "https://mp.weixin.qq.com/s/2I_eem6KwJ3hKeM9nyHSBg?from=industrynews&color_scheme=light#rd"
    title: "Agent 会越用越聪明吗？这个开源项目开始量化「自我进化」！"
  - id: repo-snapshot
    resource: "https://github.com/FeiZhuNiU-INFJA/LIFT/tree/9d282e415c5e3b0f65b82c8758a013b269583d93"
    title: "LIFT checked repository snapshot"
---

# 来源台账

采集时点：2026-10-10。LIFT 源码及文档按 GitHub API 当时返回的提交 `9d282e415c5e3b0f65b82c8758a013b269583d93` 固定；排行榜 JSON 与 GitHub 仓库元数据仍分别按其自身生成时间和采集时点描述。仅记录公开页面的必要元数据与事实定位，不保存文章全文、原始 HTML 或访问受限内容。

| source_id | 来源与 URL | 来源级别 | 可访问性与归属信号 | 支撑范围 |
|---|---|---|---|---|
| blog | [微信公众号文章](https://mp.weixin.qq.com/s/2I_eem6KwJ3hKeM9nyHSBg?from=industrynews&color_scheme=light#rd) | 三级线索来源 | 无登录要求可读；页面账号显示「开源星探」，标记原创；显示发布时间 2026-10-09 07:03，未注明时区；URL 由用户提供。未据页面署名推断法律主体归属。 | F-001–F-006；作者主张以归因形式使用 |
| repo | [LIFT GitHub 仓库](https://github.com/FeiZhuNiU-INFJA/LIFT) | 官方项目来源 | 公开仓库；页面可访问。仓库描述为可变元数据，按采集时点记录。 | F-007、F-026 |
| repo-snapshot | [固定版本树](https://github.com/FeiZhuNiU-INFJA/LIFT/tree/9d282e415c5e3b0f65b82c8758a013b269583d93) | 官方仓库快照 | 2026-10-10 检查时 `main` 指向该提交；提交时间 2026-09-11T05:33:00Z。 | F-027、F-031 |
| benchmark | [Benchmark Introduction](https://raw.githubusercontent.com/FeiZhuNiU-INFJA/LIFT/9d282e415c5e3b0f65b82c8758a013b269583d93/docs/benchmark-intro.md) | 官方项目文档 | 固定提交的 raw 文档 | F-013–F-014 |
| eval-flow | [Evaluation Flow](https://raw.githubusercontent.com/FeiZhuNiU-INFJA/LIFT/9d282e415c5e3b0f65b82c8758a013b269583d93/docs/eval-flow.md) | 官方项目文档 | 固定提交的 raw 文档 | F-015、F-017 |
| suite | [Suite Requirements](https://raw.githubusercontent.com/FeiZhuNiU-INFJA/LIFT/9d282e415c5e3b0f65b82c8758a013b269583d93/assets/suite_requirement.md) | 官方项目文档 | 固定提交的 raw 文档 | F-016、F-028 |
| leaderboard | [Leaderboard JSON](https://raw.githubusercontent.com/FeiZhuNiU-INFJA/LIFT/9d282e415c5e3b0f65b82c8758a013b269583d93/docs/leaderboard.json) | 官方项目数据 | 固定提交的 raw JSON；数据自身带生成时点 | F-008–F-010、F-018、F-029 |
| leaderboard-script | [Leaderboard Builder](https://raw.githubusercontent.com/FeiZhuNiU-INFJA/LIFT/9d282e415c5e3b0f65b82c8758a013b269583d93/scripts/build_leaderboard.py) | 官方项目代码 | 固定提交的 raw Python 源码 | F-019–F-021、F-030 |
| runtime-task-loop | [run_task.py](https://github.com/FeiZhuNiU-INFJA/LIFT/blob/9d282e415c5e3b0f65b82c8758a013b269583d93/src/lift/eval/run_task.py) | 官方运行时代码 | 固定提交；`src/lift/eval/run_task.py::run_task` 的返回值和文档字符串定义任务内 work↔judge 实际轮数 | F-030 |
| paper | [LIFT Paper](https://raw.githubusercontent.com/FeiZhuNiU-INFJA/LIFT/9d282e415c5e3b0f65b82c8758a013b269583d93/docs/paper-neurips.md) | 项目论文/预印本 | 固定提交的 raw 文档；文档自述 v1 preprint | F-011–F-012、F-022–F-023、F-027 |
| se-bench | [SE-Bench arXiv v1](https://arxiv.org/html/2602.04811v1) | 学术预印本 | 公开 HTML 页面 | F-024 |
| evoagentbench | [EvoAgentBench arXiv](https://arxiv.org/pdf/2607.05202) | 学术预印本 | 公开 PDF 页面 | F-025 |
| github-api | [GitHub repository API](https://api.github.com/repos/FeiZhuNiU-INFJA/LIFT) | 官方平台元数据 | API 可访问；结论仅代表采集时仓库状态 | F-026 |

## 来源使用纪律

- 公众号文章用于记录页面事实和作者观点，不作为 LIFT 实现细节的唯一依据。
- LIFT 机制、指标、统计和论文边界优先引用其官方仓库材料。
- SE-Bench 与 EvoAgentBench 仅用于反驳领域“无人研究/无人评测”的绝对化叙述；不把不同任务设计或指标混为同一基准。
- GitHub 仓库公开可访问不等于拥有开源许可证。F-026 未确认许可证，bundle 将相关开源属性标记为待核实。
