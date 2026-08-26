---
okf_version: "0.2"
type: bundle
title: "jupyter_client Wiki"
description: "Jupyter 协议客户端实现——内核生命周期管理、ZMQ五通道通信、消息序列化与签名"
tags: ["jupyter", "kernel-client", "zmq", "messaging", "ipython", "notebook"]
version: "8.9.1"
protocol_version: "5.4"
python_requires: ">=3.10"
license: "BSD-3-Clause"
generated: { by: "source-code-to-okf-wiki/trae-cn", at: "2026-08-21T15:57:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T15:57:00Z" }
sources:
  - id: jupyter-client-repo
    resource: external/libs/jupyter/jupyter_client
    title: jupyter_client 源码
---

# jupyter_client Wiki

jupyter_client 是 **Jupyter 协议的客户端侧实现**，负责 Jupyter 前端（Notebook/Lab/Console）与内核（Kernel）之间的通信。它提供内核生命周期管理、ZeroMQ 五通道通信、消息序列化与签名等核心能力。

- **版本**：8.9.1
- **协议版本**：5.4
- **Python 要求**：≥3.10
- **许可证**：BSD-3-Clause

## 快速开始

```bash
pip install jupyter_client ipykernel
```

```python
from jupyter_client import start_new_kernel

km, kc = start_new_kernel()
kc.execute_interactive("print('Hello, Jupyter!')")
kc.stop_channels()
km.shutdown_kernel()
```

→ [5分钟快速上手](concepts/01-getting-started.md)

## 文档结构

```
jupyter-client/
├── README.md              # 本文件——bundle入口
├── concepts/              # 概念文档（13篇）
│   ├── index.md
│   ├── 00-introduction.md
│   ├── 01-getting-started.md
│   ├── 02-architecture-overview.md
│   └── ...
├── examples/              # 示例代码（3篇）
│   ├── index.md
│   ├── 01-basic-execution.md
│   ├── 02-interactive-execution.md
│   └── 03-multi-kernel-parallel.md
└── references/            # 信源登记（5篇）
    ├── index.md
    ├── client-source.md
    ├── manager-source.md
    ├── session-source.md
    ├── provisioning-source.md
    └── channels-connect-source.md
```

## 概念文档

### 入门篇

| 文档 | 说明 |
|------|------|
| [jupyter_client 简介](concepts/00-introduction.md) | 项目定位、核心能力、依赖、版本信息 |
| [5分钟快速上手](concepts/01-getting-started.md) | 安装、最小可运行示例、常见问题 |
| [架构总览](concepts/02-architecture-overview.md) | 五层分层架构、Manager-Client 分离、数据流 |

### 核心概念篇

| 文档 | 说明 |
|------|------|
| [五通道系统](concepts/03-channels-system.md) | shell/iopub/stdin/hb/control 通道的 Socket 类型与职责 |
| [连接管理与消息协议](concepts/04-connection-and-session.md) | 连接文件、Session、HMAC签名、ZMQ多帧格式 |
| [客户端体系](concepts/05-client-hierarchy.md) | KernelClient/Blocking/Async/Threaded 四种客户端 |
| [内核管理器](concepts/06-kernel-manager.md) | 生命周期管理（启动/关闭/重启/中断） |
| [多内核管理](concepts/07-multi-kernel-manager.md) | MultiKernelManager 多实例管理 |
| [内核供给器框架](concepts/08-kernel-provisioner.md) | Provisioner 抽象、LocalProvisioner、插件机制 |

### 高级扩展篇

| 文档 | 说明 |
|------|------|
| [内核规范管理](concepts/09-kernel-spec.md) | KernelSpec、KernelSpecManager、kernel.json格式 |
| [内核启动与自动重启](concepts/10-kernel-launch-and-restart.md) | 启动全流程、KernelRestarter、心跳监控 |
| [异步与线程模型](concepts/11-async-and-threading.md) | 同步/异步/线程化并发模型 |
| [CLI工具与应用](concepts/12-cli-and-applications.md) | jupyter-kernelspec/run/kernel CLI入口 |

## 示例代码

| 示例 | 说明 |
|------|------|
| [基本代码执行](examples/01-basic-execution.md) | BlockingKernelClient 执行代码、收集输出和错误 |
| [交互式执行与标准输入](examples/02-interactive-execution.md) | execute_interactive、output_hook/stdin_hook |
| [多内核并行执行](examples/03-multi-kernel-parallel.md) | MultiKernelManager/AsyncMultiKernelManager 并行 |

## 核心依赖

| 依赖 | 版本 | 作用 |
|------|------|------|
| jupyter_core | ≥5.1 | Jupyter 核心工具 |
| pyzmq | ≥25.0 | ZeroMQ Python 绑定 |
| tornado | ≥6.4.1 | 异步 I/O 框架 |
| traitlets | ≥5.3 | 配置系统 |
| python-dateutil | ≥2.8.2 | 日期处理 |
| typing-extensions | ≥4.13.0 | 类型注解 |

## 信源

所有概念文档和示例代码的内容均基于源码分析，信源登记见 [references/](references/index.md)。

```{toctree}
:maxdepth: 7

concepts/index
examples/index
references/index
facts
insights
log
```
