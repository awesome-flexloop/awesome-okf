---
okf_version: "0.2"
type: Reference
title: "信源与事实登记：分级、口径与时效"
description: "本 bundle 的官方一手信源清单与事实分级——官方核实事实与社区经验内容的边界声明、各信源时效与复核方式"
tags: [信源, 事实分级, 核验, 时效]
generated: { by: "agent/seven-concepts-research", at: "2026-10-28T18:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-10-28T18:00:00+08:00" }
status: stable
stale_after: 2027-01-31
---

# 信源与事实登记：分级、口径与时效

## 一手信源清单（官方文档，本次调研实抓核验）

| id | 信源 | 覆盖事实域 | 抓取/核对时点 |
|----|------|-----------|--------------|
| ms-wsl-config | [Microsoft Learn《WSL 中的高级设置配置》](https://learn.microsoft.com/zh-cn/windows/wsl/wsl-config) | wsl.conf/.wslconfig 全部配置键与默认值、8 秒规则、systemd、networkingMode 五值、GPU 准虚拟化、autoMemoryReclaim/sparseVhd、defaultVhdSize、virtiofs 实验开关 | 2026-10-28（页面 ms.date 2026-10-16） |
| uv-workspaces | [uv 官方文档 Using workspaces](https://docs.astral.sh/uv/concepts/projects/workspaces/) | workspace 定义、members/exclude、单一 lockfile、editable 成员依赖、`--package`、单一 requires-python 交集、path 依赖逃生舱、**「插件系统：每插件一个 workspace 包」官方用例**、依赖隔离边界声明 | 2026-10-28（页面日期 2026-10-26） |
| mcp-spec-2026 | [MCP 规范 2026-07-28 版](https://modelcontextprotocol.io/specification/2026-07-28) | JSON-RPC 2.0、无状态自包含请求、每请求能力协商、Host/Client/Server 三方、Resources/Prompts/Tools、Elicitation、Extensions（Tasks/Skills over MCP/MCP Apps）、安全三原则 | 2026-10-28 实抓 |
| importlib-metadata | [Python 官方 importlib.metadata](https://docs.python.org/3/library/importlib.metadata.html) | entry_points API 行为、3.12 移除旧接口 | 官方文档，本调研经多篇社区文章交叉印证 |
| pytest-plugins | [pytest 官方插件文档](https://docs.pytest.org/en/stable/how-to/plugins.html) | `pytest11` 入口点组、内置/外部/conftest 三通道 | 官方文档 + 社区文章交叉 |
| pluggy-docs | [pluggy 官方文档](https://pluggy.readthedocs.io/en/stable/) | hookspec/hookimpl/hookwrapper 机制 | 官方文档 |
| pep-723 | [PEP 723](https://peps.python.org/pep-0723/) | 内联脚本元数据格式 | 官方 PEP |
| anthropic-skills | [Anthropic 工程博客 Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) | SKILL.md 结构、渐进披露三级、项目级/个人级存放 | 官方博客 + 多篇社区解读交叉 |

## 事实分级

### A 级：官方文档直接核实（正文可放心引用）

- wsl.conf / .wslconfig 的全部配置键、默认值与平台版本条件（ms-wsl-config）
- 8 秒规则、`wsl --shutdown`、`wsl --list --running` 行为（ms-wsl-config）
- networkingMode 取值：NAT 默认、mirrored（Win11 22H2+）、consomme（NAT 失败回退，WSL 2.3.25+）、bridged 已弃用（2.4.5+）、none（ms-wsl-config）
- workspace 六条关键行为（单一 lockfile、editable、`--package`、应用+库成员、requires-python 交集、根 sources 继承）与「插件系统」官方用例（uv-workspaces）
- uv 无法保证包间依赖纪律的官方声明（uv-workspaces）
- MCP 2026-07-28：无状态核心、每请求能力协商、Server 三特性、Client Elicitation、三个 Extensions、安全三原则（mcp-spec-2026）
- entry points 发现依赖已安装发行版、3.12 起 `entry_points(group=...)` 唯一接口（importlib-metadata）
- pytest `pytest11` 入口点组与三通道插件（pytest-plugins）
- SKILL.md 渐进披露三级与两级存放路径（anthropic-skills）

### B 级：社区经验（正文已显式标注口径）

- /mnt/c（9P）跨文件系统 IO 比Linux ext4 慢约一个量级——多篇社区实测共识，微软未发布官方对比基准。
- uv 比 pip 快 10–100 倍——社区基准（Astral 与第三方均发布过），实际数字随负载与缓存状态浮动。
- 「uv 一个工具替代 pip/pip-tools/pipx/pyenv/poetry/twine/venv」——社区定位表述，官方文档未逐项背书。
- vLLM v1 `vllm.general_plugins` 入口点组——知乎源码解析文章（单一社区源，机制与 entry points 标准行为一致，风险低）。
- mirrored 模式对「Windows 宿主 ↔ WSL MCP Server」localhost 互通的简化效果——模式特性为 A 级（官方），「简化效果」判断为架构推演。

## 时效声明

| 主题 | 演进速度 | 复核建议 |
|------|---------|---------|
| MCP 规范 | 高（2026 年内五个规范版本；2026-07-28 为无状态重构版，SDK 支持在铺开） | stale_after 2027-01-31 前后重查规范与所用 SDK 支持矩阵 |
| uv | 高（0.5.x 起多次破坏性变更；workspace 语义稳定化中） | 同上 |
| WSL 配置项 | 中（consomme/virtiofs/WSL 容器 wslc.exe 均为新近演进） | 同上 |
| entry points/pluggy/PEP 723 | 低（标准库与成熟库） | 一年后 |

## 与相关束的信源分工

- WSL 安装与 CLI 基础操作的信源与教程：[WSL 子系统中文教程](../../../systems/wsl/index.md)
- Windows 原生执行隔离（MXC）信源：[microsoft-mxc-agent-containment 束信源层](../../microsoft-mxc-agent-containment/references/verification.md)
