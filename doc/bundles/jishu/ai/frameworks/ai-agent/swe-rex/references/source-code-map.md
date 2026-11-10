---
type: Reference
title: "SWE-ReX 源码信源登记（commit 5c995c3）"
description: "SWE-ReX v1.4.0+18 源码快照的模块、符号、行号与事实编号登记；29 个 Python 文件、3,715 行、10 个 HTTP 路由、7 个部署配置、3 个运行时实现"
tags: [swe-rex, source-code, facts, python, fastapi, pexpect]
generated: { by: "seven-concepts-cmd/R", at: "2026-11-10T17:35:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-10T17:45:00+08:00" }
status: stable
stale_after: 2027-03-31
sources:
  - id: upstream-repo
    resource: https://github.com/SWE-agent/SWE-ReX
    title: "SWE-agent/SWE-ReX 官方仓库"
  - id: local-snapshot
    resource: /references/source-code-map.md
    title: "本束源码事实登记"
---

# SWE-ReX 源码信源登记

## 信源固定信息

| 项 | 值 |
|---|---|
| 上游仓库 | `https://github.com/SWE-agent/SWE-ReX` |
| 本地快照 | `external/dao/SWE-agent/SWE-ReX/`（env-bound，不入库） |
| 版本标签 | `v1.4.0`（2025-08-13） |
| 快照描述 | `v1.4.0-18-g5c995c3` |
| 固定 commit | `5c995c365dfb1fd5bc56fda688be5d8538f9931f`（2026-03-02） |
| 包版本 | `1.4.0`（`src/swerex/__init__.py` 第1行） |
| 采集日期 | 2026-11-10 |

> 信源稳定性说明：`external/` 被主仓 `.gitignore` 第12行忽略，属于开发者机器路径（env-bound）。本束通过“上游 URL + release tag + commit hash”固定版本；所有行号均相对该 commit。复现方式：`git clone https://github.com/SWE-agent/SWE-ReX && git checkout 5c995c3`。

## 规模计数（脚本口径）

| 指标 | 值 | 口径 |
|---|---:|---|
| Python 文件 | 29 | `Get-ChildItem src -Recurse -File -Filter *.py` |
| Python 总行 | 3,715 | `(Get-Content).Count` 求和 |
| Python 非空行 | 3,052 | 去空行后计数 |
| `.py` + `.md` 总行 | 5,328 | 排除 `.git/` |
| 测试文件 | 13 | `tests/*.py` |
| 测试用例 | 89 | `^\s*(async )?def test_` |
| HTTP 路由 | 10 | `^@app\.(get|post)` |
| 部署配置类 | 7 | `deployment/config.py` 中 `class .*Config(BaseModel)` |
| 运行时配置类 | 3 | `runtime/config.py` 中 `class .*Config(BaseModel)` |
| 异常类 | 12 | `exceptions.py` 中 `^class ` |
| 文档 Markdown | 20 | `docs/**/*.md` |

## 模块地图

```text
src/swerex/
├── __init__.py            # 版本、包名、远程可执行文件名
├── __main__.py            # python -m swerex → server.main
├── exceptions.py          # 12 个异常类
├── server.py              # FastAPI 应用、认证、幂等、异常传输、10 路由、CLI
├── deployment/
│   ├── abstract.py        # AbstractDeployment（start/stop/is_alive/runtime/add_hook）
│   ├── config.py          # 7 个部署配置 + 联合类型 + get_deployment
│   ├── local.py           # LocalDeployment → LocalRuntime
│   ├── docker.py          # Docker/Podman 容器部署
│   ├── modal.py           # Modal Sandbox 部署
│   ├── fargate.py         # AWS ECS Fargate 部署
│   ├── daytona.py         # Daytona Sandbox 部署
│   ├── remote.py          # RemoteDeployment → RemoteRuntime
│   ├── dummy.py           # DummyDeployment → DummyRuntime
│   └── hooks/             # DeploymentHook + SetStatusDeploymentHook
├── runtime/
│   ├── abstract.py        # Runtime 抽象 + Pydantic 请求/响应模型
│   ├── config.py          # 3 个运行时配置
│   ├── local.py           # LocalRuntime + BashSession（pexpect）
│   ├── remote.py          # RemoteRuntime（aiohttp）
│   └── dummy.py           # DummyRuntime（预置输出）
└── utils/
    ├── aws.py             # Fargate 资源创建/查询（10 函数）
    ├── aws_teardown.py    # AWS 资源清理（7 函数）
    ├── free_port.py       # 端口分配 + 进程内去重
    ├── log.py             # rich 日志 + emoji + 环境变量
    └── wait.py            # _wait_until_alive 轮询
```

## 符号与行号索引（节选）

| 符号 | 位置 | 事实 |
|---|---|---|
| `AbstractDeployment` | `deployment/abstract.py:11` | F-017 |
| `DockerDeployment.start` | `deployment/docker.py:233` | F-020 |
| `DockerDeployment._get_swerex_start_cmd` | `deployment/docker.py:120` | F-021 |
| `ModalDeployment.start` | `deployment/modal.py:208` | F-025 |
| `FargateDeployment.start` | `deployment/fargate.py:123` | F-030 |
| `DaytonaDeployment.start` | `deployment/daytona.py:97` | F-031 |
| `DeploymentConfig` | `deployment/config.py:211` | F-035 |
| `AbstractRuntime` | `runtime/abstract.py:234` | F-039 |
| `BashAction` | `runtime/abstract.py:51` | F-042 |
| `Command` | `runtime/abstract.py:143` | F-045 |
| `BashSession.start` | `runtime/local.py:157` | F-052 |
| `BashSession._run_normal` | `runtime/local.py:274` | F-053 |
| `BashSession.interrupt` | `runtime/local.py:186` | F-056 |
| `_split_bash_command` | `runtime/local.py:59` | F-057 |
| `LocalRuntime.execute` | `runtime/local.py:419` | F-060 |
| `RemoteRuntime._request` | `runtime/remote.py:165` | F-064 |
| `RemoteRuntime._handle_transfer_exception` | `runtime/remote.py:84` | F-065 |
| `ResponseManager` | `server.py:42` | F-075 |
| `exception_handler` | `server.py:105` | F-076 |
| `main` | `server.py:193` | F-079 |

完整事实清单（F-001 ~ F-114）见 [spec/facts.md](/spec/facts.md)，其中每条均带文件路径与行号。

## 数据契约（Pydantic 模型）

| 模型 | 关键字段 | 位置 |
|---|---|---|
| `IsAliveResponse` | `is_alive`, `message`, `__bool__` | `runtime/abstract.py:8` |
| `CreateBashSessionRequest` | `startup_source`, `session`, `session_type`, `startup_timeout` | `runtime/abstract.py:23` |
| `BashAction` | `command`, `session`, `timeout`, `is_interactive_*`, `check`, `expect` | `runtime/abstract.py:51` |
| `BashObservation` | `output`, `exit_code`, `failure_reason`, `expect_string` | `runtime/abstract.py:109` |
| `Command` / `CommandResponse` | `command`, `shell`, `check`, `env`, `cwd`, `merge_output_streams` / `stdout`, `stderr`, `exit_code` | `runtime/abstract.py:143/179` |
| `Read/Write/Upload` | `path`, `encoding`, `errors`, `content`, `source_path`, `target_path` | `runtime/abstract.py:185-221` |
| `_ExceptionTransfer` | `message`, `class_path`, `traceback`, `extra_info` | `runtime/abstract.py:224` |

## 相关文档

- [官方文档信源](/references/official-docs-source.md)
- [验证报告](/references/verification.md)
- [源码地图概念篇](/concepts/08-source-map.md)
