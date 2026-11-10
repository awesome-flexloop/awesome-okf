# 信源参考

本目录登记 Microsoft Agent Framework 知识包的事实来源与核验记录。

## 文档

* [事实登记簿（F-001 ~ F-120）](article-source.md) - Build 2026 博文、Microsoft Learn 中文文档与 GitHub 仓库的事实编号登记；与 spec `facts.md` 双份一致。
* [核验报告（P0 对账与口径说明）](verification.md) - GA 日期、版本号、包名、Harness 压缩条件、CodeAct 基准、Copilot SDK 时间线等 18 项核验与 5 处口径差异，以及第二轮源码核验。
* [源码信源登记与模块地图](source-code-map.md) - commit 098214127、1.25.0/1.28.0 版本快照、Python/.NET 模块地图与计数口径。

## 信源清单

| 编号 | 信源 | 类型 | 覆盖 |
|------|------|------|------|
| S1 | [Build 2026 公告博文](https://devblogs.microsoft.com/agent-framework/microsoft-agent-framework-at-build-2026-announce/) | 官方博客（2026-06-03） | Harness、Hosted、CodeAct、Copilot SDK、Handoff 公告口径 |
| S2 | [Microsoft Learn 中文文档](https://learn.microsoft.com/zh-cn/agent-framework/) | 官方文档（2026-10 ~ 2026-11 更新） | 概念、快速开始、工具、技能、工作流、托管、迁移 |
| S3 | [GitHub 仓库](https://github.com/microsoft/agent-framework) | 开源仓库 | README、包结构、Releases、Hyperlight 包说明 |
| S4 | [源码检出 commit 098214127](https://github.com/microsoft/agent-framework/commit/098214127) | 本地源码（env-bound，按 commit 固定） | python/dotnet 实现、类与默认值、计数核验 |

```{toctree}
:hidden:
:maxdepth: 2

article-source
verification
source-code-map
```
