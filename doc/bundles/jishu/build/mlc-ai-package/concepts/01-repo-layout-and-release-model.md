---
type: concept
title: 仓库布局与发布模型
description: packages/ 标准布局、每包自包含的理由、PR/手动/夜间三类触发的语义
tags:
  - mlc-ai
  - packaging
  - layout
  - release
generated: true
verified: false
status: stable
stale_after: "2027-05-01"
sources:
  - "external/dev/libs/mlc-ai/package/README.md"
  - "external/dev/libs/mlc-ai/package/packages/mlc-ai/README.md"
  - "external/dev/libs/mlc-ai/package/.gitmodules"
---

# 仓库布局与发布模型

## 顶层结构

```text
package/
├── packages/
│   ├── mlc-llvm-static/      标准布局 + extra-targets 子分发
│   ├── mlc-z3-static/        标准布局
│   ├── mlc-doxygen-bin/      标准布局
│   └── mlc-ai/               例外：构建脚本 + conda 环境 + tlcpack 子模块
├── docker/                   构建环境镜像（Dockerfile + install 脚本）
├── .github/
│   ├── actions/detect-env-vars/   composite action：按 CPU 数设 CMAKE_BUILD_PARALLEL_LEVEL
│   └── workflows/                每包一个发布 workflow + 夜间清理 + 镜像构建
├── README.md
└── .gitmodules               仅 3rdparty/tlcpack 一个子模块
```

根下没有统一的 `src/` 或 `pyproject.toml`：仓库本身不可安装，只是四个独立 Python 项目的宿主（F-001、F-002）。

## 标准包布局

根 README 的「Package layout」段给出统一模板，这是理解全部脚本的骨架：

```text
packages/<pkg>/
  pyproject.toml   scikit-build-core 构建；版本读自 version.py；
                   含 test extra、pytest testpaths、cibuildwheel 配置
  version.py       包版本与上游钉扎（release、commit、archive SHA-256）的唯一来源
  CMakeLists.txt   运行 scripts/prepare_<upstream>.py，把 staging 输出装进 wheel
  README.md
  LICENSE
  scripts/
    prepare_<upstream>.py   下载、校验、构建、staging
    stamp_version.py        给 version.py 打发布后缀（如 .post1）
    copy_wheel.py           cibuildwheel 的 repair 命令（原样保留 wheel）
    cibuildwheel_run.sh     通过 uv 运行固定版本 cibuildwheel
    wheel_manylinux_2_28.sh / wheel_macos.sh / wheel_windows.ps1
                            本机三平台发布 wheel 构建
  python/<module>/  Python 包；_version.py 构建期生成并 gitignore
  tests/python/     针对已安装 wheel 的 pytest 套件
```

`mlc-llvm-static` 在此之上多两个扩展：`extra-targets/`（第二个分发）与 `verify/`（C++ 验证探针）。

### 为什么辅助脚本"复制"而不"共享"

F-018 给出了明确理由：**每个包要从自己的 sdist 构建**。如果 `prepare_*.py` 从仓库根共享，那么 `pip install --no-binary mlc-z3-static mlc-z3-static` 下载到的 sdist 里就不含那个共享文件，构建直接失败。

这是一个容易被"DRY 直觉"否决的设计，但它是分布式的硬约束：sdist 是自包含的归档，跨包 `import` 在安装场景下不存在。四份 `cibuildwheel_run.sh`、四份 `copy_wheel.py` 的重复是代价，也是正确性来源。

### 识别哪些是"生成物，不入库"

| 生成物 | 生成者 | 是否入库 |
|---|---|---|
| `python/<module>/_version.py` | `prepare_*.py` 的 `write_version_module()` | 否（sdist 显式排除） |
| `python/mlc_llvm_static/static/`、`licenses/` | `prepare_llvm.py` / `split_sdk.py` | 否 |
| `staticlib.json` / `base.json` / `extra.json` | 构建期 | 否 |
| `python/mlc_doxygen_bin/bin/`、`doxygen.json` | `prepare_doxygen.py` | 否 |
| `.sdk-cache/all-sdk.zip` | `build_wheels.py`（`MLC_LLVM_STATIC_USE_CACHE=1`） | 否 |

这条边界由 `pyproject.toml` 的 `sdist.exclude` 强制（F-030、F-114），不是靠 `.gitignore` 的自觉。

## 发布模型：三类触发

根 README「When workflows run」段定义了三种语义，它们在四个包上保持一致：

### 1. Pull request —— 只在不影响文档时构建，永不发布

```yaml
pull_request:
  paths:
    - "packages/mlc-llvm-static/**"
    - "!packages/mlc-llvm-static/**/*.md"
    - ".github/workflows/mlc_llvm_static_wheel.yml"
```

要点：

- **路径过滤到包级**：改 z3 不会触发 LLVM 的六平台构建（后者是小时级成本）。
- **Markdown 取反**：只改 README 不构建。这是省 CI 的关键一行——因为 `paths` 里同时写了父目录通配和 Markdown 取反。
- **PR 不发布**：发布作业的 `if: inputs.publish` 在 PR 事件下恒为假；`mlc-ai` 的 nightly 流水线则用 `github.ref == 'refs/heads/main'` 守卫上传步骤。

### 2. 手动运行（workflow_dispatch）—— 可控发布

LLVM 的输入项（F-142 相关）：

| 输入 | 作用 |
|---|---|
| `version_suffix` | 追加 PEP 440 后缀（`rc0` → `23.1.1rc0`，`dev0` → `23.1.1.dev0`，`post0` → `23.1.1.post0`） |
| `publish` | 是否发布到 PyPI，默认关闭 |
| `repository_url` | 自定义 PyPI 兼容仓库，空表示正式 PyPI |
| `publish_packages` | `both` / 仅基础包 / 仅 add-on（用于"一边上传失败后补发"） |

`mlc-ai` 的输入只有 `tag`：留空构建 nightly，给值构建稳定版。

### 3. 计划任务（schedule）—— 只有 mlc-ai 有

| workflow | cron | 语义 |
|---|---|---|
| `wheel_manylinux.yaml` | `0 6 * * *` | 构建 nightly（Linux，5 个 GPU 变体） |
| `wheel_win.yaml` | `0 6 * * *` | 构建 nightly（Windows） |
| `wheel_applesiliconmac.yaml` | `0 8 * * *` | 构建 nightly（macOS arm64） |
| `prune_nightly.yaml` | `0 11 * * *` | 清理旧 nightly 并刷新 `mlc.ai/wheels` 索引 |

三个 PyPI 包（llvm/z3/doxygen）**没有定时构建**：它们的版本由上游 release 驱动，发布是人工决策。

## `mlc-ai` 为什么是例外

该包目录里没有 `pyproject.toml`，也没有 `version.py`：

```text
packages/mlc-ai/
  scripts/            sync、build、upload、prune
  conda/              conda 构建环境
  conda/tvm-unity/    被 CI 搬到 3rdparty/tlcpack/conda 的环境定义
  3rdparty/tlcpack/   tlcpack 子模块（conda recipes）
```

原因是构建对象不同：它构建的是**上游项目的源码**，而上游在构建时才 `git clone`，其 `pyproject.toml` 来自被克隆的仓库。因此这里只保留"如何克隆、如何改包名、如何进容器编译、如何上传"的编排脚本。

这也解释了 `.gitmodules` 为什么只有一个 `3rdparty/tlcpack`（F-011）：conda recipe 需要一个稳定来源，而 `mlc-ai/relax` 与 `mlc-ai/mlc-llm` 故意不入子模块——它们必须能在构建期切到任意 tag 或 `origin/mlc` 最新提交。

## 自检方式

```bash
# 1) 确认每个包的 sdist 排除项覆盖了所有生成物
grep -n "sdist.exclude" -A 20 packages/*/pyproject.toml

# 2) 确认没有跨包 import（除 tests 外）
grep -rn "^from packages\|^import packages" packages/ || echo "无跨包导入"

# 3) 确认 PR 触发的路径过滤仍在
grep -n "paths:" -A 4 .github/workflows/*.yml .github/workflows/*.yaml
```

## 常见误解

- **"根目录没有 pyproject.toml，所以这不是一个 Python 项目"**——对，也不是错：仓库是四个独立 Python 项目的宿主，每个 `packages/*` 才是一个可构建单元。
- **"PR 会发布测试版"**——不会。PR 运行永远不发布；要发布必须手动勾选 `publish`。
- **"改 README 也会跑 CI"**——不会，Markdown 被显式排除在触发路径之外。
- **"`mlc-ai` 也是一个 wheel 名"**——它确实是包名（`mlc-ai-nightly-cu128` 等），但它是被构建出来的产物名，不是本仓库里的 Python 包。

## 延伸阅读

- 版本与钉扎：[单一版本源与版本戳记](02-single-version-source.md)
- 外层构建后端：[scikit-build-core 与内层 CMake 流水线](03-scikit-build-inner-cmake-pipeline.md)
- nightly 流水线细节：[nightly 与稳定版 wheel 流水线](12-nightly-and-stable-wheels.md)
