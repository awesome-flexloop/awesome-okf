---
okf_version: "0.2"
type: bundle
title: "SWE-ReX：给 Agent 的可替换沙箱执行后端"
description: "SWE-ReX v1.4.0-18-g5c995c3 源码全栈中文教程——Deployment/Runtime 两级解耦、pexpect 会话状态机、10 路由 HTTP 协议与 511 异常传输、7 种部署与 3 种运行时、12 类异常与 89 个测试；含 10 概念、5 示例、3 信源，固定 commit 5c995c3"
tags: [swe-rex, SWE-agent, sandbox, shell, docker, modal, fargate, daytona, fastapi, pexpect, OKF]
generated: { by: "seven-concepts-cmd/E", at: "2026-11-10T17:52:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-10T18:05:00+08:00" }
status: stable
stale_after: 2027-03-31
sources:
  - id: github-swe-rex
    resource: https://github.com/SWE-agent/SWE-ReX
    title: "SWE-agent/SWE-ReX 官方仓库（v1.4.0，commit 5c995c3）"
  - id: docs-site
    resource: https://swe-rex.com/latest/
    title: "SWE-ReX 官方文档站"
  - id: repo-facts
    resource: /references/source-code-map.md
    title: "源码事实登记 F-001 ~ F-114"
  - id: docs-facts
    resource: /references/official-docs-source.md
    title: "README 与 docs 事实登记"
  - id: verification
    resource: /references/verification.md
    title: "P0 验证报告 V-01 ~ V-12"
---

# SWE-ReX：给 Agent 的可替换沙箱执行后端

> **性质声明**：本 bundle 为**源码教程**。全部行为结论来自固定快照 `v1.4.0-18-g5c995c3`（commit `5c995c3`，2026-03-02）的源码、`pyproject.toml` 与官方文档；示例未在本机逐条执行，已在 [示例索引](examples/index.md) 标注。文档与源码的 5 处漂移见 [验证报告](references/verification.md)。

SWE-ReX 把 coding agent 最脏的一层——“在某个环境里跑 shell 命令、拿回输出和退出码、保持会话状态”——抽成稳定接口。它不思考、不规划、不调用模型；它只保证无论命令落在本机、Docker、Modal、Fargate 还是 Daytona，agent 侧代码都一样。

## 核心结论

1. **两级正交抽象**：`Deployment` 管环境生命周期，`Runtime` 管执行语义；换环境不触碰 agent 代码（F-017、F-039、F-098）。
2. **会话是伪终端状态机**：pexpect + 固定 PS1 哨兵 + 旁路退出码；交互式程序走独立路径（F-052、F-053、F-055）。
3. **协议只有 10 个路由**：认证、单槽幂等、HTTP 511 异常重建是三个关键设计（F-073 ~ F-076）。
4. **七种部署共享一套执行语义**：差异在资源编排与网络暴露，不在命令怎么跑（F-020、F-025、F-030、F-031）。
5. **失败可分层定位**：部署启动、连接、会话、文件传输各有明确异常（F-084）。
6. **代码/文档/打包存在漂移**：CHANGELOG 停在 1.2.1、Daytona 未入导航、`aiohttp`/`typing_extensions` 未声明（F-008、F-014、F-015、F-106）。

## 知识结构

```text
swe-rex/
├── concepts/                     # 10 篇概念
│   ├── 00-project-overview.md    # 定位、谱系、规模、适用性
│   ├── 01-architecture.md        # Deployment / Runtime / Server
│   ├── 02-session-model.md       # pexpect、PS1、退出码、中断
│   ├── 03-http-protocol.md       # 10 路由、认证、幂等、511
│   ├── 04-deployments.md         # 7 种部署的生命周期
│   ├── 05-runtimes-and-execution.md  # 3 种运行时与 9 个方法
│   ├── 06-configuration-and-extension.md  # 配置、hook、新增部署
│   ├── 07-failure-modes-and-tests.md  # 异常、排障、测试地图
│   ├── 08-source-map.md          # 符号、行号、调用链、扩展点
│   └── 09-agent-integration.md   # 接入 agent 的四种模式
├── examples/                     # 5 篇示例
│   ├── 01-local-hello-world.md
│   ├── 02-docker-sandbox.md
│   ├── 03-remote-server.md
│   ├── 04-agent-loop.md
│   └── 05-parallel-deployments.md
├── references/                   # 3 份信源
│   ├── source-code-map.md
│   ├── official-docs-source.md
│   └── verification.md
├── spec/                         # R/I 阶段产物
│   ├── facts.md
│   └── insights.md
├── index.md
└── log.md
```

内容文档合计 **10 + 5 + 3 = 18 篇**。

## 三条阅读路线

1. **只想用**：`00 → 01 → examples/01 → examples/02`。
2. **要接新平台**：`01 → 04 → 06 → 08`。
3. **要排障/改协议**：`02 → 03 → 05 → 07 → 08`。

## 关键数字（脚本复核）

| 指标 | 值 | 事实 |
|---|---:|---|
| Python 文件 | 29 | F-009 |
| Python 行数 | 3,715 | F-009 |
| 测试用例 | 89 | F-011 |
| HTTP 路由 | 10 | F-077 |
| 部署配置 | 7 | F-035 |
| 运行时实现 | 3 | F-071 |
| 异常类 | 12 | F-084 |

## 使用边界

`LocalDeployment` 无沙箱，直接在本机执行；需要隔离请用 Docker/Modal/Fargate/Daytona。SWE-ReX 只提供执行接口，不提供 LLM、评测指标、补丁提取或安全策略。接入方式见 [作为 Agent 执行后端](concepts/09-agent-integration.md)。

## 目录

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
examples/index
references/index
spec/facts
spec/insights
log
```
