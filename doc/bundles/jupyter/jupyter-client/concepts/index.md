# 概念文档索引

本目录包含 jupyter_client 的 13 篇概念文档，按入门→核心→高级的递进关系组织。

## 入门篇

| 序号 | 文档 | 说明 |
|------|------|------|
| 00 | [jupyter_client 简介](00-introduction.md) | 项目定位、核心能力、依赖、版本信息 |
| 01 | [5分钟快速上手](01-getting-started.md) | 安装、最小可运行示例、常见问题 |
| 02 | [架构总览](02-architecture-overview.md) | 五层分层架构、Manager-Client 分离、数据流 |

## 核心概念篇

| 序号 | 文档 | 说明 |
|------|------|------|
| 03 | [五通道系统](03-channels-system.md) | shell/iopub/stdin/hb/control 通道的 Socket 类型与职责 |
| 04 | [连接管理与消息协议](04-connection-and-session.md) | 连接文件、Session、HMAC签名、序列化、ZMQ多帧格式 |
| 05 | [客户端体系](05-client-hierarchy.md) | KernelClient/Blocking/Async/Threaded 四种客户端对比 |
| 06 | [内核管理器](06-kernel-manager.md) | 生命周期管理（启动/关闭/重启/中断）、pending状态保护 |
| 07 | [多内核管理](07-multi-kernel-manager.md) | MultiKernelManager 多内核实例管理、委托模式 |
| 08 | [内核供给器框架](08-kernel-provisioner.md) | KernelProvisionerBase、LocalProvisioner、插件机制 |

## 高级扩展篇

| 序号 | 文档 | 说明 |
|------|------|------|
| 09 | [内核规范管理](09-kernel-spec.md) | KernelSpec、KernelSpecManager、kernel.json格式 |
| 10 | [内核启动与自动重启](10-kernel-launch-and-restart.md) | 启动全流程、KernelRestarter、心跳监控、重启风暴防护 |
| 11 | [异步与线程模型](11-async-and-threading.md) | 同步/异步/线程化并发模型、ZMQ线程安全规则 |
| 12 | [CLI工具与应用](12-cli-and-applications.md) | jupyter-kernelspec/run/kernel 三个CLI入口 |
