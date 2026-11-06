# 实战层

三篇可照做的操作文档。命令、配置与回执格式整理自官方 `INSTALL.md` / `README.md`（2026-11-06 `main` 分支快照）。

> **⚠️ 可复现性声明**：以下操作**均未在本知识包生成环境中实测**（本机 Windows，官方 Windows 版待定，F-045）。官方另标注四类 Webhook 模板只在本地模拟服务验证、多家 Agent 接入命令「还没有逐个跑过」（F-054、F-055、F-067）。执行前请按 [03 插件生态](../concepts/03-plugin-ecosystem.md) 的三档分级判断，并以本机版本与仓库最新 Release 为准。

| 文档 | 内容 | 主要 F 编号 |
|------|------|------------|
| [01 · 安装与首次试跑](01-install-and-first-run.md) | Node 24+ 前置与合规前置、安装命令与目录布局、`doctor`/`check`、`try`→`answer`→`status` 序列、WSL2 五项限制、卸载保留数据 | F-044~F-048、F-064、F-066 |
| [02 · 规则与回执](02-rules-and-receipts.md) | `rules.json` 官方定时规则原文示例、外部事件规则字段表、规则热生效、`rules explain` 与 `emit --dry-run` 预演、五类回执与 `ask` 代码块、`why 1` 复查 | F-019、F-027、F-029、F-034、F-049~F-051 |
| [03 · 插件接入与交付演练](03-plugins-and-delivery.md) | `add <git 地址>`、`command` 接入与 `{prompt}` 独立参数、接真实服务前的分档检查、`deliver` 七步流程、官方四条自测命令、收尾检查清单 | F-052~F-056、F-059、F-060、F-063、F-068 |

## 建议顺序

安装验证 → `rules explain` / `emit --dry-run` 预演 → 启用真实事件 → `deliver` 交付演练 → 需要时用 `sim/` 与 `benchmark` 自测。

```{toctree}
:hidden:

01-install-and-first-run
02-rules-and-receipts
03-plugins-and-delivery
```
