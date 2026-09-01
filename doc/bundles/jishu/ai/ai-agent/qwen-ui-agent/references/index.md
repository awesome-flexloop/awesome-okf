# 信源登记簿（References）

本目录收录 Qwen-UI-Agent 技术评测知识包的信源事实清单和核验报告。

## 信源清单

| 编号 | 信源 | 类型 | 覆盖事实 |
|------|------|------|---------|
| R1 | [博文原文](article-source.md) | 微信公众号"人间彷徨"（2026-08-26） | F-001 ~ F-031（博文全部事实与观点）+ F-032 ~ F-044（核验补充与勘误） |
| R2 | [核验报告](verification.md) | WebSearch + arXiv/GitHub 官方来源 | 8 项 P0 声明核验结论（5✅ + 2⚠️ + 1❌） |

## 事实编号索引

| 事实编号 | 简述 | 信源 | 文档 |
|---------|------|------|------|
| F-001 | 博文元信息（标题/作者/时间） | R1 | article-source.md |
| F-002 | 2026-08-20 开源发布 | R1+R2 | 00-project-overview |
| F-003 | GUI智能体非聊天机器人 | R1+R2 | 00-project-overview |
| F-004 | 12306查票+钉钉建会举例 | R1 | 00-project-overview |
| F-005 | 同类产品痛点 | R1 | 00-project-overview |
| F-006 | 真机训练100+设备/150+App/400+任务 | R1+R2 | 01-capabilities-benchmarks |
| F-007 | MobileWorld 82.1% | R1+R2 | 01-capabilities-benchmarks |
| F-008 | 真机实测92.2% | R1+R2 | 01-capabilities-benchmarks |
| F-009 | 安卓日常97.5% | R1+R2 | 01-capabilities-benchmarks |
| F-010 | WebArena 73.6%排名第一 | R1+R2 | 01-capabilities-benchmarks |
| F-011 | CLI执行+批量动作 | R1+R2 | 01-capabilities-benchmarks |
| F-012 | 近四成批量/整体省58% | R1+R2 | 01-capabilities-benchmarks |
| F-013 | 安全确认（钱/删/隐私） | R1+R2 | 01-capabilities-benchmarks |
| F-014 | HF权重/GitHub仓库 | R1+R2 | 00-project-overview, 02-practice |
| F-015 | 自部署隐私优势 | R1 | 02-practice |
| F-016 | 8B消费级显卡（有误） | R1+R2 | 02-practice |
| F-017 | Python 3.10+/PyTorch 2.0+（有误） | R1+R2 | 02-practice |
| F-018 | 等托管API | R1 | 02-practice |
| F-019 | 流程一财务对账40分→5分 | R1 | examples/01 |
| F-020 | 流程二运营日报85%成功率 | R1 | examples/01 |
| F-021 | 流程三老CRM最稳 | R1 | examples/01 |
| F-022 | 坑1静默点错 | R1 | 02-practice, examples/01 |
| F-023 | 坑2长任务迷失 | R1 | 02-practice |
| F-024 | 坑3安全边界自守 | R1 | 01-capabilities, 02-practice |
| F-025 | 适合老软件无接口团队 | R1 | 02-practice |
| F-026 | 适合RPA升级 | R1 | 02-practice |
| F-027 | 分数自报提醒 | R1 | 01-capabilities, 02-practice |
| F-028 | 最强开源GUI智能体评价 | R1 | 02-practice |
| F-029~F-031 | 作者总结观点 | R1 | 00-project-overview |
| F-032 | MAI-UI续作/权重未发布（勘误） | R2 | 00-project-overview, 02-practice |
| F-033 | 58%仅限OSWorld-v2对比M3（勘误） | R2 | 01-capabilities-benchmarks |
| F-034 | 27B模型/requirements 4项（勘误） | R2 | 02-practice |
| F-035 | 官方项目主页 | R2 | 00-project-overview |
| F-036 | arXiv论文链接 | R2 | 00-project-overview |
| F-037 | GPT-5.6/Claude版本确认 | R2 | 01-capabilities-benchmarks |
| F-038 | 3流程为团队自述实测 | R1 | examples/01 |
| F-039 | 四类能力覆盖 | R2 | 00-project-overview |
| F-040 | 官方副标题 | R2 | 00-project-overview |
| F-041 | GitHub两子目录 | R2 | 00-project-overview |
| F-042 | 权重开源为部分不实 | R2 | 00-project-overview, 02-practice |
| F-043 | 40%批量动作核验通过 | R2 | 01-capabilities-benchmarks |
| F-044 | 发布时间线 | R2 | 00-project-overview |

## 可信度说明

| 等级 | 事实编号 | 说明 |
|------|---------|------|
| ✅ 已核验 | F-002, F-006~F-010, F-013, F-035~F-037, F-039~F-041, F-043 | 经arXiv/官方页/GitHub交叉验证 |
| ⚠️ 部分有误 | F-012, F-014, F-016, F-042 | 博文表述存在以偏概全或混淆，已勘误 |
| ❌ 有误 | F-016, F-017 | 硬件要求和软件版本无官方依据 |
| 📝 作者观点 | F-004, F-005, F-018~F-031, F-038 | 博文作者/团队观点和自述体验，非客观事实 |

```{toctree}
:hidden:
:maxdepth: 7

article-source
verification
```
