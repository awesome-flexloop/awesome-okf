# 变更日志

## 2026-11-10

- **初始版本**：基于 Build 2026 公告博文（2026-06-03）、Microsoft Learn 中文文档（2026-10 ~ 2026-11 更新）与 GitHub 仓库/Releases 生成。
- **事实登记**：F-001 ~ F-120，覆盖框架定位、运行时、Harness、工具技能、记忆安全、工作流、托管、Build 2026 与迁移。
- **核验**：18 项 P0 对账；5 处口径差异（压缩条件、CodeAct 基准、Copilot SDK 时间线、Go 后增、文件记忆路径）单列于 `references/verification.md`。
- **结构**：10 篇概念 + 5 篇示例 + 2 篇信源；设 `examples/`，因文档提供可复现的安装/代码/调用流程。
- **索引**：接入 `jishu/ai/frameworks` 分组导航与 toctree；同步 `ai`、`jishu`、`bundles` 三级计数。
- **说明**：示例代码为最小化改写，非官方原文；厂商自述数据已标注单源。
- **门禁说明**：invoke gates.toctrees / invoke gates.utf8 依赖未确认安装，按 Skill §7 手动等效验证执行（UTF-8 strict、双份 F 编号、toctree、相对链接、计数、敏感路径），结果见 spec eview.md。
