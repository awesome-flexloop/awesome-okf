---
type: spec
title: "SWE-ReX 架构洞察"
---

# SWE-ReX 架构洞察

> 基于 `spec/facts.md` 的 F-001 ~ F-114。每条洞察含：陈述、证据、反常识、行动。

## I-01 两级正交抽象：Deployment 决定“在哪”，Runtime 决定“怎么执行”

**陈述**：SWE-ReX 把“环境生命周期”和“命令执行接口”拆成两个独立层。`AbstractDeployment` 只负责 `start/stop/is_alive/runtime`；`AbstractRuntime` 只负责 session、命令、文件、上传。任何部署最终都交出一个实现 `AbstractRuntime` 的对象。

**证据**：F-017、F-020、F-025、F-033、F-039、F-097。Docker/Modal/Fargate/Daytona 的 `start()` 内部都构造 `RemoteRuntime`；`LocalDeployment` 直接构造 `LocalRuntime`；两者接口相同（F-098）。

**反常识**：远程执行不是另一套 API。容器内跑的是 `server.py` + `LocalRuntime`，容器外的 `RemoteRuntime` 只是把同一组方法映射成 HTTP。真正被替换的是“传输”，不是“语义”。

**行动**：给新平台写接入时，只实现 `AbstractDeployment` 的四个成员并在 `start()` 里交出 `RemoteRuntime`；不要改 agent 侧调用。排查问题时先分清是部署层（启动/网络/端口）还是运行时层（session/命令）。

## I-02 会话的本质是一个受控伪终端状态机，而不是 `subprocess.run`

**陈述**：`LocalRuntime` 有两条执行路径：`execute()` 走 `subprocess.run`（一次性、无状态），`run_in_session()` 走 `BashSession`（持久 shell、状态保留）。`BashSession` 用 pexpect 驱动 bash，用固定 PS1 哨兵判断命令结束，再用旁路 `echo EXITCODESTART$?EXITCODEEND` 提取退出码。

**证据**：F-042、F-052、F-053、F-060、F-100。`BashAction` 的 `check` 三态（raise/silent/ignore）与 `expect` 字段（F-042）；`_run_normal()` 的三步流程（F-053）；bashlex 失败时的唯一字符串回退（F-054）。

**反常识**：难点不是“把命令发进去”，而是“知道命令何时结束、退出码是多少”。交互式程序没有退出码、分页器不会返回 PS1、bashlex 会误解析——这些都不是异常边角，而是主流程必须处理的常态。

**行动**：需要环境变量/`cd`/交互式工具时用 session；一次性命令用 `execute`。给 session 命令设 `timeout`；交互式程序用 `expect` 指定提示符；卡住时用 `BashInterruptAction`（SIGINT → Ctrl-Z → `kill -9 %1`）。

## I-03 协议只有 10 个端点，但错误语义是协议的一等公民

**陈述**：HTTP 层是薄薄一层 JSON-RPC 风格映射：10 个路由对应 Runtime 的 9 个方法加一个根路径。真正的设计点在错误传输：server 捕获所有非 HTTP 异常，序列化为 `_ExceptionTransfer` 并以 511 返回；客户端按 `class_path` 动态导入并重建原异常类型。

**证据**：F-047、F-065、F-072、F-076、F-077、F-084。`_ExceptionTransfer` 含 message/class_path/traceback/extra_info（F-047）；511 处理（F-076）；客户端反射重建与回退（F-065）。

**反常识**：远程调用通常把异常压平成字符串，SWE-ReX 反其道而行——让 `SessionDoesNotExistError`、`CommandTimeoutError` 在客户端仍是原类型，调用方可以 `except`。代价是异常类必须可导入，否则退化为 `SwerexException`。

**行动**：客户端捕获异常时按本地类型处理；自定义异常要保证模块可导入。不要把 511 当成普通 5xx 重试。

## I-04 幂等机制是“单槽缓存”，只适合重试最近一次请求

**陈述**：`ResponseManager` 只保存一个 `last_processed_request_id` 和对应响应；`RemoteRuntime._request()` 为每个请求生成 UUID 并放在 `X-Request-ID`；server 命中相同 ID 时直接返回缓存响应。

**证据**：F-064、F-074、F-075。类 docstring 明确写“多并发客户端时幂等性不保证”（F-075）。

**反常识**：这不是通用幂等键存储，而是针对“网络抖动导致同一请求重发”的单槽优化。两个并发请求会互相覆盖槽位；重试更早的请求不会命中。

**行动**：只在单客户端、顺序重试的场景依赖它；多 agent 并发时不要假设请求去重。需要严格幂等时在业务层自己做键与结果存储。

## I-05 部署矩阵的差异在“资源编排”，不在“执行语义”

**陈述**：7 种部署配置共享同一个 Runtime 契约，差异集中在镜像来源、端口暴露方式、token 生成、启动超时、云资源创建与清理。执行命令的代码始终是容器内的 `LocalRuntime`。

**证据**：F-021、F-023、F-025、F-027、F-029、F-030、F-031、F-035。Docker 用 `-p port:8000` + `RemoteRuntime(host, port)`（F-020）；Modal 用 tunnel URL（F-025）；Fargate 用公网 IP + 8880（F-028/F-030）；Daytona 用 preview link 且 `port=None`（F-031）。

**反常识**：平台接入的主要工作量是“把 server 跑起来并让客户端可达”，而不是实现一套新的命令执行器。`swerex-remote || pipx run swe-rex` 的 fallback 出现在 Docker/Modal/Fargate/Daytona 四处，说明镜像里不一定预装 SWE-ReX 是常态。

**行动**：选型时按隔离强度、启动延迟、成本、网络可达性选部署；调试时先看 `is_alive` 与容器日志，再怀疑 agent。自建镜像时预装 `swe-rex` 可省掉 pipx fallback 的启动时间与网络依赖。

## I-06 代码、打包元数据与文档存在可观测漂移，信源必须钉到 commit

**陈述**：当前快照 `__version__ = "1.4.0"`，但 `CHANGELOG.md` 最新只到 1.2.1；`DaytonaDeployment` 已存在且 README 提供 `[daytona]` 安装，但 mkdocs 导航与 `docs/api/deployments/` 没有 Daytona 页面；源码使用 `aiohttp` 与 `typing_extensions`，`pyproject.toml` 运行时依赖未声明；`requests` 声明但在 `src/` 无调用。

**证据**：F-006、F-007、F-008、F-014、F-015、F-016、F-106。

**反常识**：官方文档不是单一真相源。版本号、CHANGELOG、导航、依赖列表由不同流程维护，任何一个都可能滞后。只读 README 会漏掉 Daytona；只读 CHANGELOG 会以为项目停在 1.2.1。

**行动**：引用行为时以固定 commit 的源码 + `pyproject.toml` 为准，文档只作导览；升级时先跑 `pip check`/导入测试，确认隐式依赖是否被上游带入。本束所有事实固定在 commit `5c995c3`。

## 知识地图与学习路径

```text
入门（先跑起来）
  00 项目总览 → 01 架构分层 → 02 会话模型
      ↓
核心（理解协议与实现）
  03 HTTP 协议 → 04 部署矩阵 → 05 运行时与执行语义
      ↓
进阶（改造与排障）
  06 配置与扩展 → 07 失败模式与测试 → 08 源码地图
      ↓
应用（接到自己的 agent）
  09 作为 Agent 执行后端 → examples/01~05
```

**三条阅读路线**：

1. 只想用：`00 → 01 → examples/01 → examples/02`。
2. 要接新平台：`01 → 04 → 06 → 08`。
3. 要排障/改协议：`02 → 03 → 05 → 07 → 08`。

## 相关文档

- [事实清单](../spec/facts.md)
- [源码地图](/references/source-code-map.md)
- [验证报告](/references/verification.md)
