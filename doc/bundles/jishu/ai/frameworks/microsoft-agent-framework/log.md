# 变更日志

## 2026-11-10（第二轮：源码核验）

- **新增信源**：本地源码检出 commit `098214127`（`dotnet-1.28.0-19-g098214127`），Python core 1.25.0 / .NET 1.28.0；登记于 `references/source-code-map.md`。
- **新增事实**：F-121 ~ F-170（源码符号、默认值、目录/文件计数、文档-源码差异）。
- **新增概念**：10 源码地图、11 核心运行时、12 Harness 源码、13 工作流源码、14 FIDES 源码、15 CodeAct 与 .NET。
- **新增示例**：05 源码阅读路径（6 条检索命令）。
- **文档-源码差异**：Shell 在 Python 侧经预发布 `agent-framework-tools` 可用（文档写“仅 .NET”）；源码 1.25.0 领先最新 Release 1.21.0；Go 仍为独立仓库。
- **计数**：Python 包 44、.NET 项目 38、core 顶层 py 文件 24（脚本计数）。
- **未重写**：第 00–09 篇结论保持不变，仅新增源码篇并在索引/根索引追加导航。

## 2026-11-10

- **初始版本**：基于 Build 2026 公告博文（2026-06-03）、Microsoft Learn 中文文档（2026-10 ~ 2026-11 更新）与 GitHub 仓库/Releases 生成。
- **事实登记**：F-001 ~ F-120，覆盖框架定位、运行时、Harness、工具技能、记忆安全、工作流、托管、Build 2026 与迁移。
- **核验**：18 项 P0 对账；5 处口径差异（压缩条件、CodeAct 基准、Copilot SDK 时间线、Go 后增、文件记忆路径）单列于 `references/verification.md`。
- **结构**：10 篇概念 + 5 篇示例 + 2 篇信源；设 `examples/`，因文档提供可复现的安装/代码/调用流程。
- **索引**：接入 `jishu/ai/frameworks` 分组导航与 toctree；同步 `ai`、`jishu`、`bundles` 三级计数。
- **说明**：示例代码为最小化改写，非官方原文；厂商自述数据已标注单源。
- **门禁说明**：invoke gates.toctrees / invoke gates.utf8 依赖未确认安装，按 Skill §7 手动等效验证执行（UTF-8 strict、双份 F 编号、toctree、相对链接、计数、敏感路径），结果见 spec 
eview.md。
