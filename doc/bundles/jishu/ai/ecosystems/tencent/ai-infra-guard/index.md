---
okf_version: "0.2"
type: bundle
title: AI-Infra-Guard 知识包
description: 腾讯朱雀实验室 AI 基础设施安全检测工具源码解析，涵盖分布式架构、指纹DSL、漏洞匹配、WebSocket协议与Go/Python桥接。
tags: [ai-infra-guard, security, ai-security, fingerprint, vulnerability, mcp, go, python]
generated: { by: "reference_agent/trae-solo", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-08-23
---

# AI-Infra-Guard（A.I.G）知识包

AI-Infra-Guard 是腾讯朱雀实验室开源的 AI 基础设施安全检测工具，采用 Go + Python 混合架构，支持 AI 组件指纹识别、CVE 漏洞匹配、MCP 插件安全审计、大模型越狱评测和 Agent 安全评估。

- **仓库**：https://github.com/Tencent/AI-Infra-Guard
- **许可证**：Apache-2.0
- **数据规模**：142 个指纹规则、2014 条 CVE 记录、15 个 MCP 安全规则、17 个评测数据集

## 知识地图

### 入门层

| 文档 | 说明 |
|------|------|
| [分布式架构总览](concepts/00-architecture.md) | Server-Agent 三层架构、通信流、部署模式 |
| [四种任务类型](concepts/01-task-types.md) | AI-Infra-Scan、Mcp-Scan、Model-Redteam-Report、Agent-Scan |

### 核心层

| 文档 | 说明 |
|------|------|
| [指纹规则 DSL](concepts/02-fingerprint-dsl.md) | body/header/icon/hash 匹配、操作符、AST 求值 |
| [CVE 漏洞匹配](concepts/03-vuln-matching.md) | 语义化版本比较、AdvisoryEngine、安全评分 |
| [WebSocket 通信协议](concepts/04-websocket-protocol.md) | 消息格式、8 种事件类型、SSE 推送、心跳 |

### 进阶层

| 文档 | 说明 |
|------|------|
| [Go/Python 桥接](concepts/05-python-bridge.md) | 子进程调用、stdout JSON 行协议、uv run |
| [MCP 安全扫描](concepts/06-mcp-scan.md) | stdio/SSE/HTTP 传输、规则匹配、LLM 动态分析 |

### 示例

| 文档 | 说明 |
|------|------|
| [CLI 命令行扫描](examples/cli-scan.md) | scan/webserver 命令参数、输出格式、常用场景 |
| [自定义指纹规则](examples/custom-fingerprint.md) | YAML 编写、DSL 语法、版本提取、关联漏洞 |
| [Docker 部署](examples/docker-deploy.md) | docker-compose、环境变量、多 Agent 扩展 |

### 信源溯源

| 信源 | 覆盖源码 |
|------|---------|
| [Go Server 信源](references/go-server.md) | common/websocket/、cmd/cli/、cmd/agent/ |
| [扫描引擎信源](references/scan-engine.md) | common/runner/、common/fingerprints/parser/ |
| [漏洞结构信源](references/vuln-struct.md) | pkg/vulstruct/ |
| [Python 子系统信源](references/python-subsystems.md) | mcp-scan/、agent-scan/、AIG-PromptSecurity/ |
| [数据规则信源](references/data-rules.md) | data/fingerprints/、data/vuln/、data/mcp/、data/eval/ |

## 变更日志

见 [log.md](log.md)。

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
spec/facts
spec/insights
log
```
