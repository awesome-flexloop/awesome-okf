---
type: reference
title: README + AGENTS 信源锚点（20 条）
description: podman-py README.md 4 组事实（PyPI名/install/4 extras/基础示例）+ AGENTS.md 18 条锚点（7大AI陷阱R1-R7+质量双轨80vs85%+Persona+Quick Start+Common local issues+DCO+pre-commit不含pylint）
tags: [podman-py, README, AGENTS-pitfalls, DCO, coverage-dual-track, pylint-not-default]
generated:
  by: process:seven-concepts/sc-20260907-podman-py/e-phase
  at: 2026-09-07
verified:
  by: human:xinzo
  at: 2026-09-07
status: stable
stale_after: 2027-09-07
sources:
  - id: src-readme
    resource: external/dao/action/Containers/podman-py/README.md
    title: podman-py README.md — 项目简介、安装命令、基础示例
  - id: src-agents-full
    resource: external/dao/action/Containers/podman-py/AGENTS.md
    title: podman-py AGENTS.md 全文 — Build Test Quality 表 + Quick Start + Common pitfalls + Essential commands
---

# README + AGENTS 信源锚点（20 条）

## 第一部分：README.md 4 组事实

### RM-1 PyPI 包名（R1 陷阱关联）
- **事实**：`PodmanPy`（Python bindings for Podman's REST API）发布到 **PyPI 名 `podman`**（不是 `podman-py`）。
- **代码**：`pip install podman`
- **关联陷阱**：R1（Wrong repository — Go pkg/bindings ≠ 本 Python 仓库）

### RM-2 安装命令 + 4 组 extras 依赖
| extras | 包含内容 | 安装命令 |
|---|---|---|
| **default**（无 extras） | 核心：requests + urllib3 | `pip install podman` |
| **`[progress]`** | `rich`（用于 `images.pull(progress_bar=True)`） | `pip install 'podman[progress]'` |
| **`[docs]`** | Sphinx + myst-parser（ReadTheDocs 构建） | `pip install 'podman[docs]'` |
| **`[test]`** | pytest + pytest-cov + requests-mock | `pip install 'podman[test]'` |

### RM-3 最低 Python 版本 + 支持版本
- **事实**：`requires-python = ">=3.9"`（pyproject.toml）
- tox envlist 覆盖：`py39,py310,py311,py312,py313`（5 个 CPython 版本，不支持 PyPy 未测试）

### RM-4 README 基础示例代码（7 行骨架）
```python
# README.md 官方首屏示例
import podman

with podman.PodmanClient() as client:
    img = client.images.pull("alpine")
    ctnr = client.containers.run(img, detach=True)
    print(ctnr.status)
    ctnr.stop()
    ctnr.remove()
```

## 第二部分：AGENTS.md 18 条锚点

### Persona 与 Mental Model（3 条）
- **AG-1 Persona**："Pythonic Podman SDK 开发者 — 写薄门面 (thin façade)，不重复实现 daemon 逻辑；优先 API 契约对齐而非行为相似性"
- **AG-2 Mental Model 第 1 层（薄门面）**：所有业务语义在 Podman daemon；podman-py = 「REST 请求构造器 + 响应 DTO」，不要在 Python 层实现业务。
- **AG-3 Mental Model 第 2 层（PyPI 名）**：PyPI `podman` ≠ Go `github.com/containers/podman/pkg/bindings`（R1 重申）。

### Build / Test / Quality 表（AG-4 ~ AG-11，8 条）
| 编号 | 维度 | Makefile 目标 | tox env | 关键参数 |
|---|---|---|---|---|
| AG-4 | 单元测试 | `make unittest` | `tox -e py312`（或其他版本） | `testpaths = podman/tests/unit` |
| AG-5 | 集成测试 | `make integration` | `tox -e py312 -- podman/tests/integration/` | 需要 `PODMAN_BINARY` + `ssh localhost exit` 0 秒通 |
| AG-6 | 覆盖率（宽松端） | `make coverage` | `tox -e coverage` | **`--fail-under=80`**（⚠️ 与 CONTRIBUTING 不一致，见 AG-13） |
| AG-7 | 格式 | `make format` | `ruff format .` | pre-commit 已包含 |
| AG-8 | lint | `make lint` | `ruff check .` + `mypy` | pre-commit 4 项：ruff + mypy + tmt + yaml，**NOT 包含 pylint**（AG-16） |
| AG-9 | DCO 签名 | `make validate` | 无对应 tox env | 依赖 PATH 上 `git-validation` 二进制（不是 pip 包） |
| AG-10 | Docs | `make docs` | 无 tox env（Sphinx 直接读 README → API doc） | ReadTheDocs 自动构建 |
| AG-11 | pnext（前瞻用例） | 无 make target | `tox -e py312 -- --pnext -m pnext` | `@pytest.mark.pnext` 装饰的测试默认跳过 |

### Quick Start + Common local issues（AG-12，1 条）
- **AG-12 Quick Start 集成测试前置 3 步**：
  1. `pip install -e '.[test]'`
  2. **`ssh localhost exit`** 必须 0 秒通（否则 Waiting on podman-forward-*.sock 挂死）
  3. `tox -e py312 -- podman/tests/integration/test_containers.py`

### 质量双轨与 pylint（AG-13 ~ AG-16，4 条）
- **AG-13 80% vs 85% 覆盖率矛盾（R3 陷阱原文）**
  - Makefile/tox.ini：`--fail-under=80`（CI 自动通过线）
  - CONTRIBUTING.md 合并红线：**85%**
  - 冲突裁决：**合并时取严 85%**（人工 review）；tox 只跑 80% 避免历史代码拖累 CI。
- **AG-14 pylint NOT 默认（R2 延伸）**：`.pre-commit-config.yaml` = `ruff` + `mypy` + `tmt` + `yaml` 4 项；**pylint 只有 reviewer 明确要求时才跑**（见 examples 03-testing-governance E3.7）。
- **AG-15 DCO 与 make validate 依赖**：`git-validation` 是独立 Go 二进制，不是 Python 依赖；CI Dockerfile 必须独立装它（否则 validate 目标直接 fail）。
- **AG-16 tox 重建**：环境损坏/包缺失时，先 `tox --recreate` 再 debug，不要手动改 `.tox/` 目录。

### 7 大 AI 陷阱（AG-17 = R1~R7，1 条聚合）
> 原文形式为 AGENTS.md `## Common pitfalls for AI agents` 下的 `1. ... 7.` 数字编号；为便于跨文档引用，本文档统一加前缀 **R1-R7** 作为稳定锚点编号。
- **R1** Wrong repo：Go `containers/podman/pkg/bindings` ≠ 本 PyPI `podman`
- **R2** make/tox dogma：Makefile 内部 calls tox，CONTRIBUTING 以 tox 为权威
- **R3** 80 vs 85% coverage：CI 80 / REVIEW 85（AG-13）
- **R4** API drift：对 libpod 官方 API 文档（不是 Docker API）
- **R5** SSH hanging：`ssh localhost exit` 先 0 秒通；否则 100ms 轮询永远超时
- **R6** Rootful vs Rootless：同一测试两种 daemon mode 结果可能不同（skipif 三元组）
- **R7** 冗余 ignore files：公共规则统一扩展 `.gitignore`，不要复制到 `.vscode/ignore` / `.idea/ignore`

### 文档链接（AG-18，最后 1 条锚点）
| 文档 | URL | 冲突裁决优先级 |
|---|---|---|
| CONTRIBUTING.md | repo 内 | 高于 AGENTS.md 本身 |
| libpod API | https://docs.podman.io/en/latest/_static/api.html | 高于任何其他文档（R4 契约源） |
| ReadTheDocs | https://podman-py.readthedocs.io/ | 参考，API 行为以源码为准 |
| Docker API 文档 | docs.docker.com/engine/api/ | **仅供 docker-py 用户迁移参考**，不是契约 |
