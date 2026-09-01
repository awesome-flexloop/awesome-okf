# 生成日志（mai-ui bundle）

## 概要

- **束名**：mai-ui（MAI-UI 源码精读教程）
- **生成日期**：2026-08-29
- **工作流**：source-code-to-okf-wiki R→I→**E**→V→C 链路，本束为 E 阶段（批量生成）产出
- **目标目录**：`projects/awesome-okf-xs/doc/bundles/ai/ai-agent/mai-ui/`

## R→I→E 链路记录

| 阶段 | 产出 | 位置 |
|---|---|---|
| R（事实采集） | F-001~F-054 源码事实（零推测，逐模块精读） | `.trae/specs/tongyi-mai-okf-wiki/facts-mai-ui.md`（本束适配于 `/references/facts.md`） |
| R（网站事实） | F-025~F-040（MAI-UI-blog 站点，B 部分） | `.trae/specs/tongyi-mai-okf-wiki/facts-websites.md` |
| I（架构洞察） | mai-ui 5 个洞察四元组 + 知识地图（7 concepts / 2 examples / references 清单 / 学习路径） | `.trae/specs/tongyi-mai-okf-wiki/insights.md` |
| E（批量生成） | 本 bundle 全部 16 个文件（references 先行 → concepts/examples → index 最后） | 本目录 |

## 信源

- **源码根**：`external/libs/tools/Tongyi-MAI/MAI-UI/MAI-UI`（伞仓 README 位于其上一级），逐项登记见 [/references/source-registry.md](/references/source-registry.md)
- **官方渠道**（仅限事实台账已登记条目）：arXiv:2512.22047（技术报告，F-001）、GitHub `Tongyi-MAI/MAI-UI`、HuggingFace `Tongyi-MAI/mai-ui` 集合（F-027）
- **博客边界**：MAI-UI-blog 两篇 Notion 重定向 stub（F-036/F-037）仅登记存在性与 URL 字面标题，正文零引用

## 生成顺序（信源先行纪律）

1. `references/facts.md`（F-001~F-054 全量适配台账，含模块覆盖核对表）
2. `references/source-registry.md`（伞仓 + 内层根文件 + src 6 文件 + evaluation + cookbook/tests + 博客站 stub）
3. `references/index.md`
4. `concepts/` 7 篇（00-project-overview → 01-quickstart-installation → 02-base-agent-traj-memory → 03-grounding-agent → 04-navigation-agent → 05-prompt-action-space → 06-evaluation-pipeline，按蓝图 F-xxx 覆盖范围生成）
5. `examples/` 2 篇（01-grounding-notebook、02-navigation-trajectory-notebook）
6. `concepts/index.md`、`examples/index.md`
7. `log.md`（本文件）与根 `index.md`（最后写，toctree 收录全部）

## 关键执行决策

- **references 结构**：任务要求 references 仅含 facts.md 与 source-registry.md 两文件（事实台账 + 统一信源登记），未按 insights 蓝图拆 7 篇——信源范围全部并入 source-registry.md 的分区表。
- **00 篇并入博客站内容**：模型家族声明、四大亮点卡与 AndroidWorld/MobileWorld/ScreenSpot-Pro 三张 HTML 表（[WEB-B] F-025~F-030、F-033~F-035），引用处均注明"博客站 HTML 页面"出处；F-038/F-039（leaderboard.json 收录范围差异）在 00/06 的"已知边界"提示。
- **01 篇补充两套环境对照**：按 insights 洞察 1 行动项，并列根 4 包依赖（F-003）与评估依赖（F-045）。
- **05 篇设坐标口径对照表**：999（src 两文件，F-017/F-023）/ 1000（评估批量与 eval_server，F-036/F-040）/ resized_width（评估单样本，F-036）三列，呼应洞察 4。
- **跨束互链**：mai-ui → mobile-world（04/06 及多篇"相关概念"：mai_ui_agent 注册与观测回填宿主）、mai-ui → qwen-ui-agent 束（00 版本谱系，单向不回写）、根 index 汇总三束互链（含 mobilepa-bench）。
