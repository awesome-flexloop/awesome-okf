---
type: Reference
title: Invocations 源码信源登记
description: Invocations v4.1.0 源码路径、版本信息、核心模块清单与公开 API
tags: [invocations, source, reference, v4.1.0]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T14:00:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-24" }
status: stable
stale_after: 2027-12-31
sources:
  - id: invocations-vendor-v4.1.0
    resource: file:///d:/spaces/SpecWeave/external/libs/tools/pyinvoke/invocations/invocations
    title: SpecWeave vendor 本地源码（v4.1.0，editable 安装）
    author: process:seven-concepts-v
  - id: invocations-github
    resource: https://github.com/pyinvoke/invocations
    title: Invocations GitHub 仓库
    author: human:bitprophet
  - id: invocations-docs
    resource: https://invocations.readthedocs.io
    title: Invocations 官方文档
  - id: invocations-pypi
    resource: https://pypi.org/project/invocations/
    title: Invocations on PyPI
---

# Invocations 源码信源登记

## 基本信息

| 属性 | 值 |
|------|-----|
| 项目名 | invocations |
| 版本 | **4.1.0** |
| 描述 | Common/best-practice Invoke tasks and collections（Invoke 最佳实践任务集合） |
| 作者 | Jeff Forcier (jeff@bitprophet.org) |
| 许可证 | BSD-2-Clause |
| Python 要求 | ≥ 3.9 |
| 核心依赖 | invoke ≥ 1.7.2 |
| 其他依赖 | blessings ≥ 1.6, build ≥ 1.3, pip ≥ 25.1, releases ≥ 1.6, semantic_version ≥ 2.4, < 2.7, tabulate ≥ 0.7.5, tqdm ≥ 4.8.1, twine ≥ 1.15, wheel ≥ 0.24.0 |
| 可选依赖 | watchdog（文件监控）, pytest-cov（覆盖率）, flake8（lint）, black（格式化） |
| 官方文档 | <https://invocations.readthedocs.io> |
| 源码仓库 | <https://github.com/pyinvoke/invocations> |
| PyPI | <https://pypi.org/project/invocations/> |

## 源码位置

Invocations 源码位于 SpecWeave 仓库的外部依赖目录：

```
external/libs/tools/pyinvoke/invocations/invocations/
```

该目录通过 git submodule 引入（vendor 区域），本地不做修改。

## 模块清单

| 模块 | 类型 | 说明 |
|------|------|------|
| `__init__.py` | 包入口 | 通过 importlib.metadata 获取版本号，过滤 semantic_version 的 SyntaxWarning |
| `autodoc.py` | Sphinx 扩展 | `TaskDocumenter` 类——让 Sphinx autodoc 能文档化 Invoke Task 对象；`setup(app)` 注册扩展 |
| `checks.py` | 任务集合 | 代码检查任务：`blacken`（black 格式化，别名 format）、`lint`（flake8）、`all_`（默认任务，依次运行 blacken+lint） |
| `ci.py` | 任务集合 | CI 环境任务：`make_sudouser`（创建带密码 sudo 用户）、`sudo_run`（sudo 用户执行命令）、`make_sshable`（localhost SSH 免密）；默认配置用户 invoker/密码 secret |
| `console.py` | 工具函数 | `confirm(question, assume_yes=True)`——Y/n 交互式确认提示，返回 bool |
| `docs.py` | 任务集合 | Sphinx 文档管理：`build`（默认任务，构建文档）、`_clean`/`_browse`/`doctest`/`tree`、`docs`/`www` 多站点子集合、`sites`（双站构建）、`watch_docs`（文件监控自动重建） |
| `environment.py` | 工具函数 | `in_ci()`——检测 CIRCLECI/TRAVIS 环境变量判断是否在 CI 中 |
| `pytest.py` | 任务集合 | Pytest 测试任务：`test`（运行 pytest）、`integration`（集成测试）、`coverage`（覆盖率测试，支持 pytest-cov、codecov、多轮追加） |
| `testing.py` | 任务集合 | 旧版 Spec/Nose 测试任务：`test`、`integration`、`watch_tests`（文件监控自动测试）、`coverage`、`count_errors`（多次运行统计flakiness） |
| `util.py` | 工具函数 | `tmpdir(skip_cleanup=False, explicit=None)`——临时目录上下文管理器 |
| `watch.py` | 工具函数 | 基于 watchdog 的文件监控：`make_handler(ctx, task_, regexes, ignore_regexes)`、`observe(*handlers)`、`watch(c, task_, regexes, ignore_regexes)` |
| `packaging/__init__.py` | 子包入口 | 导出 `vendorize` 任务和 `release` 子集合（`ns = release`） |
| `packaging/release.py` | 任务集合 | Python 包发布全流程：`status`（状态检查）、`all_`/`all`（默认，prepare→publish→push）、`prepare`（changelog/version编辑+commit+tag）、`build`（sdist/wheel构建）、`publish`（构建+twine check+venv安装测试+上传）、`test_install`（临时venv安装验证+mypy类型检查）、`upload`（twine上传+GPG签名）、`push`（git push） |
| `packaging/semantic_version_monkey.py` | 工具 | 为 semantic_version.Version 猴子补丁添加 `clone()`、`next_minor()`、`next_patch()` 方法 |
| `packaging/vendorize.py` | 任务集合 | `vendorize(distribution, version, vendor_dir, ...)`——将第三方包下载复制到 vendor 目录 |

## 公开导出模式

Invocations 的各模块遵循两种导出模式：

1. **纯工具模块**（console/environment/util/watch/autodoc）：直接定义函数/类，不创建 Collection，用户通过 `from invocations.xxx import function_name` 导入具体函数使用
2. **任务集合模块**：
   - **定义了 ns Collection 的模块**（ci.py, docs.py, packaging/release.py）：模块末尾创建 `ns = Collection(...)` 并通过 `ns.configure({...})` 设置默认配置。用户可通过 `from invocations.xxx import ns as xxx_ns` 获取预配置的 Collection，或直接导入具体任务函数
   - **不定义 ns 的模块**（checks.py, pytest.py, testing.py, packaging/vendorize.py）：仅使用 `@task` 装饰器定义任务函数，不创建 Collection。用户通过 `from invocations import xxx`（将模块传给 Collection 构造函数自动收集任务）或 `from invocations.xxx import task_func`（导入单个任务）使用
3. **packaging 子包**（`packaging/__init__.py`）：导出 `vendorize` 任务和 `release` 子模块（`from . import release`），并设置 `ns = release`（即 ns 指向 release 子模块本身）。常用 `from invocations.packaging import release` 获取 release 子模块

[^invocations-github]: Invocations GitHub 仓库：<https://github.com/pyinvoke/invocations>
[^invocations-docs]: Invocations 官方文档：<https://invocations.readthedocs.io>
[^invocations-pypi]: Invocations PyPI 页面：<https://pypi.org/project/invocations/>
