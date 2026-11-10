---
type: Reference
title: "SWE-ReX 官方文档信源登记"
description: "README、docs/architecture、usage、installation、mkdocs 导航与 PyPI 安装说明的事实登记；标注文档与源码快照的四处漂移"
tags: [swe-rex, documentation, architecture, installation, mkdocs]
generated: { by: "seven-concepts-cmd/R", at: "2026-11-10T17:36:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-10T17:45:00+08:00" }
status: stable
stale_after: 2027-03-31
sources:
  - id: readme
    resource: /references/official-docs-source.md
    title: "README 与 docs/ 事实登记"
  - id: docs-site
    resource: https://swe-rex.com/latest/
    title: "SWE-ReX 官方文档站"
---

# 官方文档信源登记

## 信源清单

| 文件 | 行数 | 覆盖内容 | 事实 |
|---|---:|---|---|
| `README.md` | 74 | 定位、三项能力、谱系、安装 extras、生态项目 | F-094 ~ F-096 |
| `docs/architecture.md` | 30 | 五步调用链、Local/Remote 同构、异常透明传输 | F-097 ~ F-098 |
| `docs/usage.md` | 101 | 本地 hello world、Docker 切换、Modal 示例、日志解读 | F-099 ~ F-104 |
| `docs/installation.md` | 15 | 稳定版/开发版安装、pre-commit | F-105 |
| `mkdocs.yml` | 80 | 站点导航：6 个部署类、4 个运行时类、Server | F-106 |
| `docs/SECURITY.md` | 7 | 漏洞报告联系人 | F-107 |
| `docs/examples.py` | 23 | 本地 runtime 手工脚本 | F-108 |

## README 的关键表述

1. 定位：`runtime interface for interacting with sandboxed shell environments`（第12行）。
2. 并行：`Running 100 agents in parallel? No problem either!`（第15行）。
3. 三项能力（第19-21行）：识别命令结束并提取输出/退出码；支持 `ipython`、`gdb` 等交互式工具；并行多个 shell session。
4. 谱系（第25行）：来自 SWE-agent 与 SWE-agent enigma 的实践。
5. 价值（第28-30行）：大规模并行、广泛平台（含非 Linux/无 Docker）、agent 逻辑与基础设施解耦。
6. 演示（第32行）：SWE-agent 在 30 个 SWE-bench 实例上并行。
7. 安装（第41-49行）：`swe-rex`、`[modal]`、`[fargate]`、`[daytona]`、`[dev]`。

> README 第15行的“100 agents”与第32行的“30 instances”是产品表述与演示规模，不是代码中的硬限制；代码层面没有并发上限常量。

## 架构文档的五步链路

`docs/architecture.md` 第3-6行与第17-23行给出：

```text
Deployment.start()
  → 启动 docker container / AWS instance / ...
  → 返回 RemoteRuntime
  → 容器内 FastAPI Server
  → 转发给 LocalRuntime
  → 实际执行命令
```

第18-20行明确：`LocalRuntime` 与 `RemoteRuntime` 接口完全相同、可互换；`LocalRuntime` 的异常会透明传输到 `RemoteRuntime`。

## 教程文档的可执行片段

`docs/usage.md` 第16-39行的 `run_some_stuff(deployment)` 是全文唯一的“跨部署复用”示例：

```python
await deployment.start()
runtime = deployment.runtime
print(await runtime.execute(Command(command=["echo", "Hello, world!"])))
await runtime.create_session(CreateBashSessionRequest())
print(await runtime.run_in_session(BashAction(command="export MYVAR='test'")))
print(await runtime.run_in_session(BashAction(command="echo $MYVAR")))
await deployment.stop()
```

第51-57行仅替换 `LocalDeployment()` 为 `DockerDeployment(image="python:3.12")`，复用同一函数。第67行日志显示容器端口映射 `-p 59647:8000` 与 `swerex-remote --auth-token ... || (... pipx run ...)`。第79-80行解释 pipx 与 `RemoteRuntime` 的角色。

## 文档与源码的漂移（P0 核验）

| # | 文档表述 | 源码/元数据 | 判定 |
|---|---|---|---|
| D-01 | `docs/installation.md` 只列 `[modal]`、`[fargate]`、`[dev]` | `pyproject.toml` 第67-69行还有 `daytona`；README 第47行也列了 `[daytona]` | 安装页滞后 |
| D-02 | `mkdocs.yml` 第66-71行部署导航 6 项，无 Daytona | `deployment/daytona.py` 存在，`DaytonaDeploymentConfig` 在 `config.py:198` | 导航/API 页缺失 |
| D-03 | `CHANGELOG.md` 最新 1.2.1 | `__version__ = "1.4.0"`（`__init__.py:1`），tag `v1.4.0` | 变更日志滞后 2 个 minor |
| D-04 | `pyproject.toml` 运行时依赖 8 项 | `remote.py:12` 导入 `aiohttp`；10 个文件导入 `typing_extensions` | 隐式依赖未声明 |
| D-05 | `pyproject.toml` 声明 `requests` | `src/` 无 `requests.` 调用；`tests/test_server.py:1` 使用 | 依赖用途与声明位置错位 |

> 以上漂移不改变核心行为结论，但会影响“按文档装依赖”的可复现性。复现时以 `pyproject.toml` + 实际导入为准。

## 相关文档

- [源码信源登记](/references/source-code-map.md)
- [验证报告](/references/verification.md)
- [项目总览](/concepts/00-project-overview.md)
