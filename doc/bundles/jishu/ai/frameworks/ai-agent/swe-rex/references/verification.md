---
type: Reference
title: "SWE-ReX 验证报告（V-01 ~ V-12）"
description: "对 18 篇内容文档的独立验证：计数复核、API 存在性、链接与 frontmatter、toctree 覆盖、文档漂移与测试覆盖空白；记录一处行数口径错误的修复"
tags: [swe-rex, verification, quality-gate, counts, api-validation]
generated: { by: "seven-concepts-cmd/V", at: "2026-11-10T18:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-10T18:05:00+08:00" }
status: stable
stale_after: 2027-03-31
sources:
  - id: repo-facts
    resource: /references/source-code-map.md
    title: "F-001 ~ F-114"
  - id: docs-facts
    resource: /references/official-docs-source.md
    title: "官方文档信源"
---

# SWE-ReX 验证报告（V-01 ~ V-12）

> 验证对象：本 bundle 的 10 篇概念、5 篇示例、3 份信源（共 18 篇内容文档）。
> 验证方式：独立 Python 脚本 + 源码 AST + Markdown 链接解析；与 R 阶段的人工采集分离。

## V-01 信源固定

| 检查 | 结果 |
|---|---|
| `git describe --tags --always` | `v1.4.0-18-g5c995c3` |
| HEAD commit | `5c995c365dfb1fd5bc56fda688be5d8538f9931f` |
| 包版本 | `1.4.0` |
| 是否符合“非浮动分支” | 是（按 commit 固定；`external/` 为 env-bound，已在信源登记中披露） |

## V-02 规模计数复核

| 指标 | R 阶段 | V 阶段（独立脚本） | 一致 |
|---|---:|---:|---|
| Python 文件 | 29 | 29 | 是 |
| Python 总行 | 3,715 | 3,715 | 是 |
| Python 非空行 | 3,052 | 3,052 | 是 |
| 测试文件 | 13 | 13 | 是 |
| 测试用例 | 89 | 89 | 是 |
| `.py` + `.md` 行数 | 5,328 | 5,328 | 是 |

口径：行数用 `(Get-Content).Count`（含空行）；测试用例正则 `^\s*(async )?def test_`。

## V-03 路由计数

`Select-String '^@app\.(get|post)'` 命中 10 条：

```text
GET  /
GET  /is_alive
POST /create_session
POST /run_in_session
POST /close_session
POST /execute
POST /read_file
POST /write_file
POST /upload
POST /close
```

与 F-077、`concepts/03-http-protocol.md` 的路由表一致。

## V-04 配置与异常计数

| 项 | 计数 | 明细 |
|---|---:|---|
| 部署配置类 | 7 | Local/Docker/Modal/Fargate/Remote/Dummy/Daytona |
| 运行时配置类 | 3 | Local/Remote/Dummy |
| 异常类 | 12 | `SwerexException` 等 |

与 F-035、F-071、F-084 一致。

## V-05 模块行数复核与修复

初次写入 `concepts/08-source-map.md` 时，模块行数为人工估算，V 阶段用 `Get-Content` 逐文件复核，发现 15 处偏差：

| 文件 | 初稿 | 实际 |
|---|---:|---:|
| `server.py` | 220 | 221 |
| `deployment/local.py` | 70 | 73 |
| `deployment/docker.py` | 331 | 334 |
| `deployment/modal.py` | 292 | 295 |
| `deployment/fargate.py` | 184 | 187 |
| `deployment/daytona.py` | 166 | 170 |
| `deployment/dummy.py` | 51 | 49 |
| `runtime/config.py` | 62 | 61 |
| `runtime/remote.py` | 266 | 265 |
| `runtime/dummy.py` | 96 | 94 |
| `utils/aws.py` | 273 | 289 |
| `utils/aws_teardown.py` | 230 | 327 |
| `utils/free_port.py` | 28 | 25 |
| `utils/log.py` | 65 | 68 |
| `utils/wait.py` | 37 | 34 |

已全部修正为实际值。这正是“目测数数会错”的实证：15/23 个模块行数首次写错。

## V-06 API 存在性（AST 核验）

用 `ast.parse` 收集 `src/` 下所有类与函数，逐个检查文档引用的符号：

| 类别 | 检查数 | 缺失 |
|---|---:|---|
| 类（部署/运行时/模型/异常/配置） | 42 | 0 |
| 方法/函数（含 `BashSession._run_normal` 等） | 17 | 0 |
| 异常类 | 12 | 0 |

重点核对：

- `NonZeroExitCodeError` 位于 `swerex.exceptions`，不在 `swerex.runtime.abstract`（已在示例四修正导入）。
- `_ExceptionTransfer` 以下划线开头但确实存在（`runtime/abstract.py:224`）。
- `DaytonaDeployment`/`DaytonaDeploymentConfig` 存在，尽管官方导航未收录。

## V-07 链接检查

脚本解析所有 `](/...)` 与 `](*.md)` 链接：

| 项 | 结果 |
|---|---|
| 内部链接总数 | 96 |
| 断裂 | 0（`verification.md` 写入前有 5 处指向本文件，属预期） |
| `../` 相对链接 | 0（`spec/insights.md` 除外；spec 为 R/I 产物，不计入 OKF 内容文档） |

## V-08 Frontmatter

18 篇内容文档全部包含：`type`、`title`、`description`、`tags`、`generated`、`verified`、`status`、`stale_after`、`sources`。

`spec/facts.md` 与 `spec/insights.md` 只保留 `type`/`title`，它们是过程产物，不参与 OKF 内容文档校验。

## V-09 Toctree 覆盖

| index | 条目数 | 覆盖 |
|---|---:|---|
| 根 `index.md` | 4 | concepts/index、examples/index、references/index、log |
| `concepts/index.md` | 10 | 00 ~ 09 全部 |
| `examples/index.md` | 5 | 01 ~ 05 全部 |
| `references/index.md` | 3 | source-code-map、official-docs-source、verification |

## V-10 文档与源码漂移（P0）

| # | 漂移 | 证据 | 影响 |
|---|---|---|---|
| D-01 | CHANGELOG 最新 1.2.1 vs 版本 1.4.0 | F-008 | 不能用 CHANGELOG 判断版本 |
| D-02 | mkdocs 导航缺 Daytona | F-106 | 官方文档站无 Daytona API 页 |
| D-03 | `docs/installation.md` 缺 `[daytona]` | F-105、F-096 | 安装页滞后 |
| D-04 | `aiohttp`/`typing_extensions` 未声明 | F-014、F-015 | 精简环境可能缺包 |
| D-05 | `requests` 仅测试使用 | F-016 | 运行时镜像可省 |

## V-11 测试覆盖空白

1. 云部署（Modal/Fargate）默认需要凭证，CI 全绿不等于云路径已验证。
2. 同一 session 的并发写入无测试。
3. 超大命令输出无测试。
4. Windows 原生不支持 `BashSession`（依赖 `/usr/bin/env bash` 与 pexpect）。
5. 无 Daytona 专用测试文件。
6. 无命令注入/路径穿越负向测试。

## V-12 编码与门禁

| 检查 | 命令 | 结果 |
|---|---|---|
| UTF-8 | `python scripts/check-utf8.py` | 通过：13,214 个文件均为有效 UTF-8 |
| bundles 索引 | `python scripts/check-bundles-index.py` | 通过：9 域 / 64 组 / 731 束，五面一致 |
| toctree | `python scripts/check-toctrees.py` | 通过：全部 index 引用有效，所有内容文档可达 |

## 结论

- 事实层：F-001 ~ F-114 均可定位到源码/文档行号。
- 文档层：18 篇内容文档结构完整、链接可解析、toctree 全覆盖。
- 风险层：已披露 5 处文档漂移与 6 项测试空白；不影响核心架构结论。
- 修正记录：模块行数 15 处、示例导入 1 处。

## 相关文档

- [源码信源登记](/references/source-code-map.md)
- [官方文档信源](/references/official-docs-source.md)
- [项目总览](/concepts/00-project-overview.md)
