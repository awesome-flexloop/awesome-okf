---
okf_version: "0.2"
---

# scrapli2 知识库

本知识包是 [scrapli2](https://github.com/scrapli/scrapli)（0.0.0-dev，libscrapli 0.0.1-rc.35）的系统化中文教程。scrapli2 是网络设备自动化库的大版本重写版，采用 **Zig + Python ctypes 混合架构**——核心协议引擎用 Zig 编写并编译为共享库，Python 层提供薄绑定。所有内容均溯源至 scrapli2 源码（`external/libs/scrapli/scrapli/` 目录），遵循 [OKF v0.2 规范](concepts/00-introduction.md)。

> **重要**：这是 scrapli2 重写版，不是旧版纯 Python scrapli。旧版的 `Scrapli`/`AsyncScrapli`/`NetworkDriver`/`Channel` 等类在本版本中不存在，主驱动类为 `Cli` 和 `Netconf`。

## 入门与基础（concepts/）

* [scrapli2 简介](concepts/00-introduction.md) — Zig+Python 混合架构、与 paramiko/asyncssh/netmiko 对比、安装方法
* [5分钟快速上手](concepts/01-getting-started.md) — 第一个 Cli 连接、平台参数、发送命令、Result 对象

## 核心概念（concepts/）

* [传输层](concepts/02-transport-layer.md) — 四种 Transport：BIN（系统ssh）、SSH2（libssh2）、Telnet、Test
* [认证与会话配置](concepts/03-auth-session.md) — AuthOptions、SessionOptions、LookupKeyValue、超时与录制
* [Cli 驱动详解](concepts/04-cli-driver.md) — open/close 生命周期、send_input/send_inputs、模式管理、read_with_callbacks
* [异步模式](concepts/05-async-mode.md) — open_async/send_input_async、async with、asyncio 并发多设备
* [平台定义系统](concepts/06-platform-definitions.md) — YAML 声明式定义、44 个内置平台、模式层级、自定义定义
* [NETCONF 驱动](concepts/07-netconf.md) — Netconf 类、get-config/edit-config/commit/lock、数据存储枚举
* [高级模式](concepts/08-advanced-patterns.md) — 回调读取、提示输入、TextFSM/Genie 解析、异常处理、FFI 深入
* [测试体系](concepts/09-testing-system.md) — golden 文件测试法、functional/unit 结构、dummy_ssh_server、TEST Transport 回放
* [平台定义目录](concepts/10-platform-catalog.md) — 44 个平台 YAML 分类、共性字段、复杂度谱系、definition_options 钩子
* [迁移指南](concepts/11-migration.md) — 旧版 scrapli → scrapli2 变化总览、Python/Go 差异、PyPI 双包
* [官方示例体系](concepts/12-repository-examples.md) — containerlab 共享拓扑、16 个示例主题矩阵、渐进式学习路径

## 实战示例（examples/）

* [基础连接与命令发送](examples/basic-connect.md) — Cli 连接 Cisco IOS-XE、SSH2/Telnet 传输
* [单条与批量命令发送](examples/send-commands.md) — send_input/send_inputs/send_inputs_from_file、结构化解析
* [异步并行连接多设备](examples/async-parallel.md) — asyncio.gather 并发、Semaphore 限流、异步 NETCONF
* [自定义平台定义与高级用法](examples/custom-driver.md) — 自定义 YAML、LoadedDefinition、回调读取、会话录制
* [代理跳转连接](examples/proxy-jump.md) — bin（ssh_config）与 ssh2（proxy_jump_* 参数）两种 ProxyJump 方式
* [结构化输出解析](examples/output-parsing.md) — textfsm_parse 单条/多条解析、ntc-templates 平台映射
* [会话录制](examples/session-recorder.md) — SessionOptions(recorder_path=...) 录制底层 session 读取

## 信源登记簿（references/）

* [scrapli2 源码信源登记](references/scrapli-source.md) — 版本信息、Zig+Python 混合架构、核心模块清单、公开 API 导出

## 跨束参考

* [paramiko 知识库](../paramiko/index.md) — 纯 Python SSH2 协议库，对比 BIN 传输模式
* [asyncssh 知识库](../asyncssh/index.md) — 基于 asyncio 的异步 SSH 库，对比异步 API 设计

## 信任与生命周期说明

* **status 判定依据**：全部 21 个内容文档（13 个概念 + 7 个示例 + 1 个信源登记）均 `status: stable`。内容基于对 scrapli2 源码（`external/libs/scrapli/scrapli/` 目录）的逐模块阅读与事实提取（133 条源码事实），经 R→I→E→V 四阶段流程生成；2026-08-28 扩展批次（scrapli-full-coverage-wiki）进一步覆盖仓库全部实质子文件夹（examples/、tests/、docs/、scrapli/definitions/、scrapli/lib/、.github/），新增 109 条事实，扩展为 13 概念 + 7 示例 + 1 信源。
* **stale_after 解释**：统一设置为 `2027-06-30`。scrapli2 仍处于 0.0.0-dev 开发阶段，API 可能在正式发布前发生变化；该日期作为保守的重新评估节点。
* **核验链路**：`generated.at` 记录各文档原始生成时刻（2026-08-23；扩展批次为 2026-08-28）；`verified.at` 记录 V 阶段 Grep 验证事件（2026-08-23；扩展批次为 2026-08-28），两者分离、可追溯。
* **架构形态确认**：Zig 核心（libscrapli 共享库）+ Python ctypes 薄绑定，双驱动（Cli/Netconf）×双 API（同步/异步）正交设计，四种可插拔 Transport，YAML 声明式平台定义。

本知识包共收录 21 个内容文档（13 个概念 + 7 个示例 + 1 个信源登记），另含 3 个子目录 index.md 与根 index.md、log.md。

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
log
```
