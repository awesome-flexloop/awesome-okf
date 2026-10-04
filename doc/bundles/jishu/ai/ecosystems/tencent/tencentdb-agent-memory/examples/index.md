# Examples

本目录包含 TencentDB Agent Memory 的 4 个实战示例。所有示例基于 commit 8b86874 截面的文档与源码整理，**未在真实环境运行验证**，命令落地前请先实测。

- [01 - 十分钟一键部署](01-quickstart.md) — 配置两组 LLM、start-all.sh 拉起三件套、读取 .admin-key、purge 重置
- [02 - Claude Code 经 Proxy 零插件接入](02-claude-code-proxy.md) — ANTHROPIC_BASE_URL/TOKEN、首轮 sessionInit、mem 指令、8 适配器口径
- [03 - 自定义记忆 Prompt](03-custom-memory-prompt.md) — v3 三元组、memory-prompt create/set/log、500/10000 限额与固定协议红线
- [04 - Wiki/CodeGraph 摄取与查询](04-wiki-codegraph-ingest.md) — create→轮询 ready、MCP 12 只读工具、llm-binding、auto-sync

## 示例对应关系

| 示例 | 对应概念 | 涉及信源 |
|------|----------|----------|
| 一键部署 | [11 部署拓扑](../concepts/11-deploy-topology.md)、[00 四件架构](../concepts/00-overview.md) | [安装与部署](../references/04-deploy-install.md) |
| Proxy 接入 | [09 MemoryProxy](../concepts/09-memory-proxy.md)、[01 四层记忆](../concepts/01-four-layer-memory.md) | [v3 API 信源](../references/03-api-references.md)、[安装与部署](../references/04-deploy-install.md) |
| 自定义 Prompt | [03 L2/L3/Prompt](../concepts/03-l2-scene-l3-persona.md)、[06 网关隔离](../concepts/06-gateway-isolation.md) | [v3 API 信源](../references/03-api-references.md)、[SDK 信源](../references/05-sdk-ci.md) |
| 资产摄取 | [08 MemoryKnowledge](../concepts/08-memory-knowledge.md)、[05 Skill 资产](../concepts/05-skill-memory.md) | [v3 API 信源](../references/03-api-references.md) |

```{toctree}
:hidden:
:maxdepth: 7

01-quickstart
02-claude-code-proxy
03-custom-memory-prompt
04-wiki-codegraph-ingest
```
