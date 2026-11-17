# 信源登记簿（References）

本目录收录 mini-SWE-agent 知识包的信源事实清单与核验报告。所有正文数字、日期、类名、命令都应能回溯到这里的 F 编号。

## 信源清单

| 编号 | 信源 | 类型 | 覆盖事实 |
|---|---|---|---|
| R1 | [博客事实清单](blog-source.md) | 第三方技术博客（2026-03-22） | F-001 ~ F-034 |
| R2 | [仓库事实清单](repo-source.md) | 官方源码 v2.4.6 + docs + GitHub API | F-035 ~ F-100 |
| R3 | [P0 核验报告](verification.md) | GitHub API / arXiv / 官方 docs / 源码对账 | 11 项 P0 + 4 条硬勘误 + 6 条单源边界 |
| R4 | [官方教程事实清单](tutorial-source.md) | minimal-agent.com 官方教程（2026-02-03） | F-101 ~ F-114 |

## 事实编号索引

| 事实编号 | 主题 | 文档 |
|---|---|---|
| F-001 ~ F-006 | 博客元信息、出品方、Stars、74%、代码量 | 00-project-overview |
| F-007 ~ F-014 | SWE-agent 谱系、三原则、团队引语 | 00、01 |
| F-015 ~ F-022 | 基准表、对比表、伪代码、环境清单 | 01、06 |
| F-023 ~ F-030 | 三条结论、适用/不适用、快速开始、模型归因 | 06、07 |
| F-031 ~ F-034 | SWE-bench 设计、能力边界、资源、版本声明 | 06 |
| F-035 ~ F-047 | 仓库身份、许可证、版本、README、依赖、入口 | 00、02、05 |
| F-048 ~ F-055 | AgentConfig、run/step/query/execute、LocalEnvironment | 02、03 |
| F-056 ~ F-057 | Docker 与其他环境后端 | 03 |
| F-058 ~ F-062 | 模型注册表、toolcall/textbased、v2 迁移 | 04 |
| F-063 ~ F-066 | 默认 YAML、观察截断、CLI 三模式 | 03、05 |
| F-067 ~ F-069 | Python bindings、SWE-bench 批处理/单实例 | examples |
| F-070 ~ F-073 | 官方 74% 声明、News、FAQ 限制与 shell session 理由 | 01、06 |
| F-074 ~ F-077 | 轨迹格式、代码/测试规模、docs 结构 | 02、05 |
| F-078 ~ F-081 | README 滞后、100 行口径、示例模型、依赖排除 | 02、04 |
| F-082 ~ F-083 | 采用者名单、启动速度（单源） | 06 |
| F-084 ~ F-087 | 四条硬勘误（Stars/年份/API/tool-calling） | verification |
| F-088 ~ F-090 | 74% 口径边界、对比表单源、知乎缺口 | verification |
| F-091 ~ F-100 | Agent/环境注册表、配置查找、CLI 装配、模型重试、toolcall 校验、递归合并、SWE-bench 流程、测试地图、行数口径 | 08-source-map |
| F-101 ~ F-114 | 官方教程的 50 行原型、三组件、两种动作格式、异常/格式纠错、环境变量、与生产代码的差异 | 04-minimal-agent-from-scratch |

## 可信度图例

| 标记 | 含义 |
|---|---|
| ✅ 已核验 | 有官方源码、官方 docs、GitHub API 或论文级来源支撑 |
| ⚠️ 口径/版本边界 | 事实成立但有统计口径、版本或表述范围限制 |
| ❌ 勘误 | 与权威来源冲突，正文采用正确值 |
| 单源 | 仅博客或仅 README 自述，未获独立佐证 |

```{toctree}
:hidden:
:maxdepth: 4

blog-source
repo-source
tutorial-source
verification
```
