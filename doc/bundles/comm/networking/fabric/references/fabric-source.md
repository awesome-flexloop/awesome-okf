---
type: Reference
title: fabric 源码信源登记
description: fabric v4.0.0 源码路径、版本信息、核心模块清单与公开 API
tags: [fabric, source, reference, v4.0.0]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: fabric-github
    resource: https://github.com/fabric/fabric
    title: fabric GitHub 仓库
    author: human:bitprophet
  - id: fabric-docs
    resource: https://www.fabfile.org
    title: fabric 官方文档
---

# fabric 源码信源登记

## 基本信息

| 属性 | 值 |
|------|-----|
| 项目名 | fabric |
| 版本 | **4.0.0**（commit ded51893f02c） |
| 描述 | High level SSH command execution（高层 SSH 命令执行库） |
| 作者 | Jeff Forcier (jeff@bitprophet.org) |
| 许可证 | BSD 2-Clause License |
| Python 要求 | ≥ 3.7（依赖 invoke、paramiko、decorator） |
| 官方文档 | <https://www.fabfile.org> |
| 源码仓库 | <https://github.com/fabric/fabric> |

## 源码位置

fabric 源码位于 SpecWeave 仓库的外部依赖目录：

```
external/libs/fabric/fabric/
```

该目录通过 git submodule 引入，本地不做修改。

## 依赖关系

fabric v4 建立在两个核心库之上：

| 依赖 | 角色 | 知识束 |
|------|------|--------|
| **invoke** (pyinvoke) | 任务执行框架：Context、Config、Runner、Task、Executor、Program CLI | [pyinvoke](../../../../build/tooling/pyinvoke/index.md) |
| **paramiko** | SSH 协议底层：SSHClient、Transport、Channel、SFTPClient、AuthStrategy | [paramiko](../../paramiko/concepts/00-introduction.md) |

架构关系：
- `Connection` **继承** `invoke.Context`（is-a），**组合** `paramiko.SSHClient`（has-a）
- `Config` **继承** `invoke.Config`，增加 SSH 相关配置
- `Remote` **继承** `invoke.Runner`，通过 paramiko Channel 执行远程命令
- `Executor` **继承** `invoke.Executor`，理解主机参数化
- `Task` **继承** `invoke.Task`，增加 hosts 概念
- `OpenSSHAuthStrategy` **继承** `paramiko.auth_strategy.AuthStrategy`

## CLI 入口点

fabric 定义命令行入口 `fab`，由 `main.py` 中的 `program = make_program()` 提供。`Fab` 类继承 `invoke.Program`，配置：

- `name="Fabric"`
- `executor_class=Executor`
- `config_class=Config`
- 任务集合默认名称：`fabfile`（通过 `tasks.collection_name` 配置）

CLI 新增参数（在 invoke 核心参数基础上）：

| 参数 | 类型 | 说明 |
|------|------|------|
| `-H`, `--hosts` | 字符串（逗号分隔） | 目标主机列表 |
| `-i`, `--identity` | list（可多次指定） | SSH 私钥路径 |
| `--list-agent-keys` | bool | 列出 ssh-agent 中的密钥后退出 |
| `--prompt-for-login-password` | bool | 启动时提示输入 SSH 登录密码 |
| `--prompt-for-passphrase` | bool | 启动时提示输入密钥密码短语 |
| `-S`, `--ssh-config` | 字符串 | 运行时 SSH config 文件路径 |
| `-t`, `--connect-timeout` | int | 连接超时（秒） |

## 核心模块清单

| 模块 | 说明 |
|------|------|
| `__init__.py` | 包入口，导出公开 API：Connection、Config、Remote、RemoteShell、Result、Group、SerialGroup、ThreadingGroup、GroupResult、task、Task、Executor；条件导出 OpenSSHAuthStrategy |
| `_version.py` | 版本号：`__version_info__ = (4, 0, 0)` |
| `connection.py` | 核心类 `Connection`（1122 行，最大文件）：继承 invoke.Context，组合 paramiko.SSHClient；包含 host 简写解析、open/close 生命周期、run/sudo/local/shell 命令执行、get/put 文件传输、forward_local/forward_remote 端口转发、gateway 跳板机；`@opens` 装饰器自动建立连接 |
| `config.py` | `Config` 类继承 invoke.Config：扩展 global_defaults（port=22、user、forward_agent、gateway、inline_ssh_env=True、runners、authentication 等）；独立加载 SSH config 文件体系（system/user/runtime 三级路径）；`from_v1()` 迁移构造器 |
| `group.py` | `Group`（继承 list，部分抽象）、`SerialGroup`（串行执行）、`ThreadingGroup`（线程并行执行）、`GroupResult`（dict 子类，succeeded/failed 属性）；统一的 `_do()` 模板方法 |
| `runners.py` | `Remote`（继承 invoke.Runner，通过 SSH channel 执行命令）、`RemoteShell`（继承 Remote，使用 invoke_shell 而非 exec_command）、`Result`（继承 invoke.Result，增加 connection 属性）；PTY/SIGWINCH 处理、inline_env 环境变量前缀 |
| `transfer.py` | `Transfer` 类封装 SFTP 文件传输：`get(remote, local, preserve_mode)` 下载、`put(local, remote, preserve_mode)` 上传；路径插值（host/user/port/basename/dirname）、file-like 对象支持、`Result` 数据类 |
| `tunnels.py` | `TunnelManager`（继承 ExceptionHandlingThread，管理本地监听 socket 和 direct-tcpip 通道）、`Tunnel`（继承 ExceptionHandlingThread，在 channel 和 socket 之间双向 select 转发） |
| `executor.py` | `Executor` 继承 invoke.Executor：`normalize_hosts()` 统一主机参数格式、`expand_calls()` 按主机展开任务调用、`parameterize()` 创建 ConnectionCall、`dedupe()` 禁用以保留每主机独立执行 |
| `tasks.py` | `Task`（继承 invoke.Task，增加 hosts 属性）、`task()` 装饰器（包装 invoke.task，设置 klass=Task）、`ConnectionCall`（继承 invoke.Call，携带 init_kwargs 并在 make_context 中创建 Connection） |
| `auth.py` | `OpenSSHAuthStrategy` 继承 paramiko AuthStrategy：模拟 OpenSSH 客户端认证顺序（config certs → cli certs → agent keys → cli keys → config keys → password）；支持 IdentityFile、ssh-agent、默认密钥路径 |
| `main.py` | CLI 入口：`Fab(Program)` 子类添加 fabric 特有参数、`make_program()` 工厂函数、`program` 全局实例 |
| `exceptions.py` | 异常体系：`NothingToDo`、`GroupException`（包装 GroupResult）、`InvalidV1Env` |
| `util.py` | 工具函数：`get_local_user()` 获取本地用户名、`debug` 日志函数、`win32` 平台标志 |
| `testing/base.py` | 测试工具：`Command`/`ShellCommand` 数据类、`MockChannel`、`Session`（模拟远程会话）、`MockRemote`（patch SSHClient，支持上下文管理器）、`MockSFTP`（已废弃） |
| `testing/fixtures.py` | pytest fixtures：`connection`、`cxn`、`remote`、`remote_with_sftp`、`sftp`、`sftp_objs`、`transfer`、`client` |

## 公开 API 导出（`__init__.py`）

```python
from ._version import __version_info__, __version__
from .connection import Config, Connection
from .runners import Remote, RemoteShell, Result
from .group import Group, SerialGroup, ThreadingGroup, GroupResult
from .tasks import task, Task
from .executor import Executor
# 条件导出（依赖 Paramiko 3.2+）
try:
    from .auth import OpenSSHAuthStrategy
except ImportError:
    pass
```

## 与 fabric v1 的主要区别

| 方面 | fabric v1.x | fabric v2+/v4 |
|------|------------|---------------|
| 架构 | 全局 env 字典 + 操作函数 | 面向对象：Connection/Config/Group |
| 任务框架 | 自定义 | 基于 invoke |
| SSH 底层 | paramiko | paramiko（不变） |
| 配置 | env 字典 | invoke 六层配置 + SSH config 独立体系 |
| 本地命令 | `local()` | `Connection.local()`（委托 invoke） |
| 并行 | `@parallel` 装饰器 | `ThreadingGroup` |
| Python 支持 | Python 2 | Python 3 only |
| `inline_ssh_env` | 无 | 3.0 起默认 True（export 前缀模式） |
