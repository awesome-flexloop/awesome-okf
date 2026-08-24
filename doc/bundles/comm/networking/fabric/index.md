---
okf_version: "0.2"
---

# fabric 知识库

本知识包是高层 SSH 命令执行库 [fabric](https://www.fabfile.org)（v4.0.0）的系统化中文教程，基于源码深度阅读生成。fabric 建立在 [paramiko](../paramiko/concepts/00-introduction.md)（SSH 协议底层）和 [pyinvoke](../../../build/tooling/pyinvoke/index.md)（任务执行框架）之上，遵循 [OKF v0.2 规范](concepts/00-introduction.md)。

## 入门与基础（concepts/）

* [fabric 简介](concepts/00-introduction.md) — fabric v4 架构（invoke+paramiko）、安装方法、与 fabric v1 的区别。
* [5分钟快速上手](concepts/01-getting-started.md) — 第一个 fab 任务、Connection 基本用法、Result 对象。

## 核心概念（concepts/）

* [Connection 详解](concepts/02-connection.md) — 构造参数、open/close 生命周期、SSH config 集成、gateway 跳板机。
* [配置体系](concepts/03-configuration.md) — Config 六层合并、SSH config 文件独立体系、环境变量、CLI 选项。
* [命令执行](concepts/04-command-execution.md) — run/sudo/local/shell、PTY、warn/hide/echo、inline_ssh_env。
* [多主机并行](concepts/05-group-parallel.md) — Group/SerialGroup/ThreadingGroup、GroupResult、GroupException 异常处理。

## 高级主题（concepts/）

* [文件传输](concepts/06-file-transfer.md) — Transfer、get/put、SFTP 封装、路径插值、权限保留。
* [隧道与跳板机](concepts/07-tunnels.md) — forward_local/forward_remote、Tunnel/TunnelManager、ProxyJump 多跳代理。
* [高级模式](concepts/08-advanced-patterns.md) — Executor 主机分组、ConnectionCall、OpenSSHAuthStrategy、MockRemote 测试工具。

## 实战示例（examples/）

* [基础部署脚本](examples/basic-deploy.md) — 拉取代码、安装依赖、重启服务的完整部署流程。
* [多服务器组并行操作](examples/multi-server-group.md) — ThreadingGroup 批量执行、部分失败处理、文件批量传输。
* [文件上传下载](examples/file-upload-download.md) — put/get 传输、file-like 对象、路径插值、底层 SFTPClient。
* [跳板机隧道](examples/tunnel-bastion.md) — ProxyJump/ProxyCommand 跳板机、本地/远程端口转发、数据库隧道。

## 信源登记簿（references/）

* [fabric 源码信源登记](references/fabric-source.md) — fabric v4.0.0 源码路径、版本、核心模块清单、公开 API 与依赖关系。

## 信任与生命周期说明

* **status 判定依据**：全部 14 个内容文档（9 个概念 + 4 个示例 + 1 个信源登记）均 `status: stable`。内容基于对 fabric 源码（`external/libs/fabric/fabric/` 目录）的逐模块阅读与事实提取（92 条源码事实），经 R→I→E→V 四阶段流程生成。
* **stale_after 解释**：统一设置为 `2027-12-31`。fabric 4.x API 自 2.x 以来核心类（Connection/Config/Group/Remote/Transfer）保持稳定，4.0 主要是清理和版本号升级；该日期作为针对未来大版本变更的保守重新评估节点。
* **核验链路**：`generated.at` 记录各文档原始生成时刻（2026-08-23）；`verified.at` 记录 V 阶段 Grep 验证事件（2026-08-23），两者分离、可追溯。

本知识包共收录 14 个内容文档（9 个概念 + 4 个示例 + 1 个信源登记），另含 3 个子目录 index.md 与根 index.md、log.md。

```{toctree}
:hidden:

concepts/index
examples/index
references/index
log
```
