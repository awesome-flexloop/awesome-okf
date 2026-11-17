---
type: concept
title: 单一版本源与版本戳记
description: version.py 如何同时驱动包版本、上游钉扎、两包互钉与运行期 _version.py
tags:
  - mlc-ai
  - versioning
  - pep440
generated: true
verified: false
status: stable
stale_after: "2027-05-01"
sources:
  - "external/dev/libs/mlc-ai/package/packages/mlc-llvm-static/version.py"
  - "external/dev/libs/mlc-ai/package/packages/mlc-llvm-static/scripts/stamp_version.py"
  - "external/dev/libs/mlc-ai/package/packages/mlc-llvm-static/pyproject.toml"
  - "external/dev/libs/mlc-ai/package/packages/mlc-z3-static/version.py"
  - "external/dev/libs/mlc-ai/package/packages/mlc-doxygen-bin/version.py"
---

# 单一版本源与版本戳记

## 一个文件，四个消费者

`version.py` 是每个包的版本真源。以 `mlc-llvm-static` 为例（F-019）：

```python
__version__ = "23.1.1"
LLVM_VERSION = "23.1.1"
LLVM_ARCHIVE_SHA256 = "ebe9be46fe8756d58c5b198ffad0fa2a766257add81a4dc52179bfacc7888ee6"
```

它被四个地方消费：

| 消费者 | 消费方式 | 用途 |
|---|---|---|
| `pyproject.toml` | `[tool.scikit-build.metadata.version]` 的 regex provider 指向 `version.py` | 填充 wheel 元数据 `Version`（动态字段） |
| `prepare_llvm.py` | `runpy.run_path(version.py)` | 拼下载 URL、构造 `staticlib.json` 的 `llvm_version` |
| `stamp_version.py` | 读取 + 正则改写 | 注入发布后缀并同步两包互钉 |
| `write_version_module()` | 生成 `python/mlc_llvm_static/_version.py` | 运行期可读的 `__version__` / `LLVM_VERSION` |

关键点：`_version.py` **不入库**。它由构建期生成，并被 `sdist.exclude` 排除（F-030）。这样源码树里 import `mlc_llvm_static` 会失败——这正是 `build_wheels.py` 要用 `importlib.util.spec_from_file_location` 按路径加载 `_llvm_config.py` 的原因（F-087 相关，见 `load_llvm_config()` 的注释）。

## 版本必须"基于上游"

`stamp_version.py` 的核心不变量（F-022）：

```python
version = Version(requested or current["__version__"])
if version.base_version != upstream:
    raise ValueError(f"Package version {version} must be based on {UPSTREAM_KEY} {upstream}")
```

`base_version` 会剥掉预发布/后发布段，因此：

| `version.py` 中的 `__version__` | `base_version` | 与 `LLVM_VERSION=23.1.1` 是否合法 |
|---|---|---|
| `23.1.1` | `23.1.1` | ✅ |
| `23.1.1.post1` | `23.1.1` | ✅ |
| `23.1.1rc0` | `23.1.1` | ✅ |
| `23.1.1.dev0` | `23.1.1` | ✅ |
| `23.1.2` | `23.1.2` | ❌ 抛错 |

这条规则把"包版本"和"上游 release"锁在一起，防止出现"包版本 1.2.3 但里面装的是 LLVM 23.1.1"这种无法推理的制品。

## 两包互钉的自动同步

`mlc-llvm-static` 与 `mlc-llvm-static-extra-targets` 必须精确同版本。这种关系写死在两处 `pyproject.toml`：

```toml
# packages/mlc-llvm-static/pyproject.toml
[project.optional-dependencies]
all = ["mlc-llvm-static-extra-targets==23.1.1"]

# packages/mlc-llvm-static/extra-targets/pyproject.toml
dependencies = ["mlc-llvm-static==23.1.1"]
```

`stamp_version.py` 用一条正则同时改写两处（F-023）：

```python
for metadata in (project / "pyproject.toml", project / "extra-targets/pyproject.toml"):
    text, count = re.subn(r'(mlc-llvm-static(?:-extra-targets)?==)[^"\]]+',
                          lambda match: match[1] + str(version), ...)
    if count != 1:
        raise ValueError("Expected exactly one exact-version SDK requirement in {metadata}")
```

`count != 1` 的校验很重要：如果将来有人在 `pyproject.toml` 里再加一条 `mlc-llvm-static==` 依赖（例如测试依赖），脚本会直接报错而不是静默只改一处。

### 为什么是 `==` 而不是 `>=`

两个 wheel 共享同一个安装前缀下的 `static/lib` 目录，且各自带 `base.json` / `extra.json` 记录同一 `build_id`。若允许版本区间，用户可能装上 23.1.1 的基础包与 23.1.2 的 add-on——CMake 侧会以 `build_id` 不一致触发 `FATAL_ERROR`（F-080），但那已经是安装后的运行时失败，不如在依赖解析阶段就阻止。

## 后缀如何进入发布流程

`mlc_llvm_static_wheel.yml` 的两个位置会调用它：

```yaml
# checks 作业
- name: Resolve and stamp package versions
  env:
    VERSION_SUFFIX: ${{ inputs.version_suffix }}
  run: python packages/mlc-llvm-static/scripts/stamp_version.py --suffix "$VERSION_SUFFIX"

# build_wheels 作业（每个平台重跑一次，保证检出树一致）
- name: Stamp both package versions
  run: python packages/mlc-llvm-static/scripts/stamp_version.py "$PACKAGE_VERSION"
```

第一次由后缀推导出版本并写入 `GITHUB_OUTPUT`（F-024），第二次把该版本作为**显式参数**在构建机上重放。这样即使某台构建机的 `version.py` 被本地修改，也会被覆盖回同一版本。

版本映射示例（该包 README 的表格）：

| `version_suffix` | 两个包版本 |
|---|---|
| 空（默认） | `23.1.1` |
| `rc0` | `23.1.1rc0` |
| `dev0` | `23.1.1.dev0` |
| `post0` | `23.1.1.post0` |

注意 PEP 440 归一化：`23.1.1.rc0` 会被规范化为 `23.1.1rc0`，因此安装时要用后者：

```bash
python -m pip install 'mlc-llvm-static[all]==23.1.1rc0'
```

## 三个包的版本字段对照

| 包 | 版本常量 | 上游标识 | 归档校验 |
|---|---|---|---|
| `mlc-llvm-static` | `LLVM_VERSION` | 由版本号派生 tag `llvmorg-<VER>` | `LLVM_ARCHIVE_SHA256` |
| `mlc-z3-static` | `Z3_VERSION` | `Z3_TAG = f"z3-{Z3_VERSION}"` + `Z3_COMMIT` | `Z3_ARCHIVE_SHA256` |
| `mlc-doxygen-bin` | `DOXYGEN_VERSION` | `DOXYGEN_TAG = "Release_" + version.replace(".", "_")` | `DOXYGEN_ARCHIVE_SHA256` |

差异的原因在各自上游的发布习惯：LLVM 用 `llvmorg-23.1.1` 标签；Z3 用 `z3-5.3.1` 标签但归档 URL 直接用 commit（更抗标签移动）；Doxygen 用下划线形式的 `Release_1_18_0`。

Z3 多一个 `Z3_COMMIT` 字段（F-020），是该包 README 明确要求的：归档 URL 由 commit 派生，因此提交哈希必须与版本一起钉死。

## 升级一个上游版本的完整动作

以 LLVM 为例（该包 README「Bumping the version」段）：

1. 编辑 `version.py` 的三个字段：`LLVM_VERSION`、`__version__`（等于或基于前者）、`LLVM_ARCHIVE_SHA256`。
2. 运行 `python scripts/stamp_version.py`，同步两份 `pyproject.toml` 的互钉版本。
3. 提交。构建时 `prepare_llvm.py` 会用新 URL 下载、用新 SHA-256 校验。
4. 首次构建必然全量编译（缓存键含版本与 SHA，F-136）。

Z3 的升级多一步：需要同时更新 `Z3_COMMIT`，其值可用 README 给出的命令取得：

```bash
gh api repos/Z3Prover/z3/commits/z3-<Z3_VERSION> --jq .sha
```

## 自检方式

```bash
# 1) 版本与上游常量一致或仅差 PEP 440 后缀
python - <<'PY'
import runpy
for pkg, upstream in (("mlc-llvm-static", "LLVM_VERSION"),
                      ("mlc-z3-static", "Z3_VERSION"),
                      ("mlc-doxygen-bin", "DOXYGEN_VERSION")):
    v = runpy.run_path(f"packages/{pkg}/version.py")
    from packaging.version import Version
    ok = Version(v["__version__"]).base_version == v[upstream]
    print(pkg, v["__version__"], v[upstream], "OK" if ok else "MISMATCH")
PY

# 2) 两包互钉在同一版本
grep -n "mlc-llvm-static" packages/mlc-llvm-static/pyproject.toml \
  packages/mlc-llvm-static/extra-targets/pyproject.toml

# 3) stamp 脚本幂等（重复运行结果不变）
python packages/mlc-llvm-static/scripts/stamp_version.py
python packages/mlc-llvm-static/scripts/stamp_version.py
git diff --stat packages/mlc-llvm-static
```

## 陷阱

- **不要手工改 `pyproject.toml` 里的 `==23.1.1`**：下一次 `stamp_version.py` 会覆盖它；若正则匹配次数不为 1，构建直接失败。
- **不要在源码树里 `import mlc_llvm_static`**：`_version.py` 不存在会 ImportError。要读版本请 `runpy.run_path("version.py")`。
- **不要给 `__version__` 手工加 `.rc0` 之外的写法**（如 `23.1.1-rc0`）：`Version()` 会抛 `InvalidVersion`。
- **`Z3_TAG` / `DOXYGEN_TAG` 是派生值**，不要单独写死，否则 tag 与版本会漂移。

## 延伸阅读

- 上游钉扎与供应链：[上游源码钉扎与供应链校验](04-source-pinning-and-provenance.md)
- 发布流水线的版本传递：[CI 工作流与 SDK 缓存](13-ci-workflows-and-caching.md)
