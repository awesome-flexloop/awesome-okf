---
type: concept
title: CI 工作流与 SDK 缓存
description: 五平台矩阵、路径过滤、配方指纹缓存键与可信发布链
tags:
  - mlc-ai
  - ci
  - github-actions
  - caching
  - pypi
generated: true
verified: false
status: stable
stale_after: "2027-05-01"
sources:
  - "external/dev/libs/mlc-ai/package/.github/workflows/mlc_llvm_static_wheel.yml"
  - "external/dev/libs/mlc-ai/package/.github/workflows/mlc_z3_static_wheel.yml"
  - "external/dev/libs/mlc-ai/package/.github/workflows/mlc_doxygen_bin_wheel.yml"
  - "external/dev/libs/mlc-ai/package/packages/mlc-llvm-static/scripts/cache_key.py"
  - "external/dev/libs/mlc-ai/package/.github/actions/detect-env-vars/action.yml"
---

# CI 工作流与 SDK 缓存

## 三个 PyPI 包的 workflow 骨架

`mlc_llvm_static_wheel.yml` 有四个作业，是三者中最复杂的：

```text
checks ──► build_wheels（5 平台矩阵）──► distributions ──► publish_pypi（可选）
```

`mlc_z3_static_wheel.yml` 是三个：

```text
build_wheels（6 平台矩阵）──┐
                            ├──► publish（可选）
build_sdist ───────────────┘
```

`mlc_doxygen_bin_wheel.yml` 同构，但矩阵少 Windows ARM64。

差异不是随意的，而是由各包的能力边界决定：

| 包 | 平台数 | 为什么 |
|---|---|---|
| llvm | 5 | Linux x86_64/aarch64、macOS arm64、Windows AMD64/ARM64；macOS x86_64 未列 |
| z3 | 6 | 多了 macOS x86_64；Windows 两个架构都支持 |
| doxygen | 5 | 无 Windows ARM64（iconv 约束，见 [Doxygen 包](11-doxygen-bin-package.md)） |

## checks 作业：先验证"可构建"，再铺矩阵

```yaml
checks:
  runs-on: ubuntu-latest
  outputs:
    matrix: ${{ steps.platforms.outputs.matrix }}
    version: ${{ steps.version.outputs.version }}
  steps:
    - uses: actions/checkout@v5
    - uses: actions/setup-python@v6
      with: { python-version: "3.11" }
    - run: python -m pip install pytest packaging
    - name: Resolve and stamp package versions
      id: version
      env: { VERSION_SUFFIX: "${{ inputs.version_suffix }}" }
      run: >-
        python packages/mlc-llvm-static/scripts/stamp_version.py
        --suffix "$VERSION_SUFFIX"
    - run: python -m pytest packages/mlc-llvm-static/tests/python -q
    - name: Define validation platforms
      id: platforms
      run: |
        python - <<'PY'
        import json, os
        rows = [...]
        with open(os.environ["GITHUB_OUTPUT"], "a") as output:
            output.write("matrix=" + json.dumps(dict(include=rows)) + "\n")
        PY
```

三个要点：

1. **矩阵在运行时生成**（内联 Python 写 `GITHUB_OUTPUT`）。好处是矩阵与 `distributions` 作业共享同一份数据（后者用 `PLATFORM_MATRIX` 环境变量重建期望文件名），不会出现"矩阵改了但校验没改"。
2. **单测先跑**：`pytest packages/mlc-llvm-static/tests/python -q` 在铺开五平台之前拦住逻辑错误。LLVM 构建是小时级，早失败省下的成本很大。
3. **版本在 checks 里定稿**，通过 `outputs.version` 传给所有构建作业。

### 矩阵内容

```python
rows = [
    dict(name="Linux x86_64", os="ubuntu-latest", arch="x64", tag="manylinux_2_28_x86_64", image="quay.io/pypa/manylinux_2_28_x86_64:latest"),
    dict(name="Linux aarch64", os="ubuntu-24.04-arm", arch="arm64", tag="manylinux_2_28_aarch64", image="quay.io/pypa/manylinux_2_28_aarch64:latest"),
    dict(name="macOS arm64", os="macos-15", arch="arm64", tag="macosx_14_0_arm64"),
    dict(name="Windows AMD64", os="windows-2022", arch="x64", tag="win_amd64", compiler="clang-cl"),
    dict(name="Windows ARM64", os="windows-11-vs2026-arm", arch="arm64", tag="win_arm64", compiler="clang-cl"),
]
```

注意 `compiler="clang-cl"` 只在 Windows 出现，并通过 `env: CC/CXX` 生效。动机写在该 workflow 的注释里：

> MSVC's ARM64 optimizer exhausts its heap on the AMDGPU asm writer, and MSVC objects carry about twice the sections and symbols, which makes the AMD64 wheels much larger.

即两个独立原因：ARM64 上 MSVC 优化器会堆溢出；AMD64 上 MSVC 对象体积约为 clang-cl 的两倍。

`ubuntu-24.04-arm` 与 `windows-11-vs2026-arm` 都是**原生 ARM runner**，而不是交叉编译。这样避免 vcpkg/工具链的交叉配置复杂度。

## 环境探测 action

```yaml
name: Detect build environment
description: Default CMake build parallelism to the available CPU count.
runs:
  using: composite
  steps:
    - shell: python
      run: |
        import os
        try:
            cpu_count = len(os.sched_getaffinity(0))
        except (AttributeError, OSError):
            cpu_count = os.cpu_count() or 1
        parallel = os.environ.get("CMAKE_BUILD_PARALLEL_LEVEL") or str(cpu_count)
        with open(os.environ["GITHUB_ENV"], "a") as output:
            output.write(f"CMAKE_BUILD_PARALLEL_LEVEL={parallel}\n")
```

优先用 `sched_getaffinity`（尊重 cgroup/CPU 亲和性），失败再退回 `os.cpu_count()`。已经设置了就尊重现值。

## 缓存：把"编译配方"做成键

这是全仓库最值得学的 CI 技巧。`cache_key.py`（F-136）：

```python
recipe = [{name: {key: spec[key] for key in ("version", "sha256")}
           for name, spec in prepare_llvm.SOURCES.items()}, prepare_llvm.DEFAULT_TARGETS]
for module, names in (
    (prepare_llvm, ("configure", "install", "build_dependencies", "build_llvm")),
    (split_sdk, ("read_components", "closure", "partitions", "cmake_value", "distribution_options", "record_build")),
):
    recipe.extend(inspect.getsource(getattr(module, name)) for name in names)
recipe.append((Path(prepare_llvm.__file__).parent / "sdk_build_options.cmake").read_text())
compilers = {name: os.environ[name] for name in ("CC", "CXX") if os.environ.get(name)}
if compilers:
    recipe.append(compilers)
key = hashlib.sha256(json.dumps(recipe, sort_keys=True).encode()).hexdigest()
print("key=" + key)
```

覆盖范围：

| 输入 | 是否影响键 | 说明 |
|---|---|---|
| 三个上游的 `version` + `sha256` | ✅ | 换版本必然重编 |
| `DEFAULT_TARGETS` | ✅ | `all` 改成别的会重编 |
| `prepare_llvm` 的四个函数源码 | ✅ | 含注释改动（`inspect.getsource` 取原文） |
| `split_sdk` 的六个函数源码 | ✅ | 图生成逻辑影响编译配置 |
| `sdk_build_options.cmake` 全文 | ✅ | 段粒度钩子 |
| `CC` / `CXX` | ✅（若设置） | Windows 的 clang-cl 与 MSVC 必须区分 |
| `build_wheels.py` | ❌ | 打包编排改动不该触发重编 |
| `compress_wheel.py` / `compact_coff.py` | ❌ | 后处理改动不触发重编 |
| 镜像 URL | ❌ | 只影响下载来源 |

设计意图很清楚：**只把"会改变编译产物"的输入纳入键**。这样改前端、改打包、改验证都能复用已编译 SDK。

### 缓存的使用

```yaml
- name: Fingerprint compiled SDK recipe
  id: recipe
  env:
    CC: ${{ matrix.compiler }}
    CXX: ${{ matrix.compiler }}
  run: python packages/mlc-llvm-static/scripts/cache_key.py >> "$GITHUB_OUTPUT"

- name: Restore compiled All-target SDK
  id: sdk_cache
  uses: actions/cache/restore@v5
  with:
    path: packages/mlc-llvm-static/.sdk-cache
    key: llvm-all-sdk-${{ matrix.tag }}-${{ steps.recipe.outputs.key }}
```

构建侧用三个环境变量接住：

```yaml
env:
  MLC_LLVM_STATIC_ALLOW_SOURCE_BUILD: "1"
  MLC_LLVM_STATIC_USE_CACHE: "1"
  MLC_LLVM_STATIC_CLEAN_BUILD: "1"
```

- `USE_CACHE=1` 让 `prepare_llvm.py` 从 `.sdk-cache/all-sdk.zip` 恢复；
- `CLEAN_BUILD=1` 在分片前删除源码构建树（只在构建目录确实是 `work/source-build` 时才删）。

### "失败也保存"的取舍

```yaml
- name: Save compiled SDK even if packaging or validation failed
  if: always() && steps.sdk_cache.outputs.cache-hit != 'true' && hashFiles('packages/mlc-llvm-static/.sdk-cache/all-sdk.zip') != ''
  uses: actions/cache/save@v5
```

`always()` 是必要的：如果编译成功但打包/验证失败，那次几小时的编译结果仍然有价值，下次重跑能直接复用。`hashFiles(...)` 守卫防止保存空缓存。

## 分发校验作业

```yaml
- name: Check complete wheel set
  run: |
    python - <<'PY'
    import json, os
    from pathlib import Path
    wheels = sorted(Path("dist").glob("*.whl"))
    expected = {f"{family}-{os.environ['PACKAGE_VERSION']}-py3-none-{row['tag']}.whl"
                for row in json.loads(os.environ["PLATFORM_MATRIX"])["include"]
                for family in ("mlc_llvm_static", "mlc_llvm_static_extra_targets")}
    if {path.name for path in wheels} != expected:
        raise SystemExit("Release wheels do not match all platforms and package version")
    PY
```

这段用**文件名集合相等**（而不是"包含"）做断言。它能同时抓三类问题：少了某个平台、多了不该有的平台、版本号没同步。

随后：

```yaml
- run: python -m pip install twine && python -m twine check --strict dist/*.whl
- name: Summarize wheel sizes
  run: | ... 写 markdown 表到 GITHUB_STEP_SUMMARY
```

`twine check --strict` 校验 README 渲染与元数据；体积表方便人眼判断是否接近 100 MB 预算。

## 发布：Trusted Publishing + 构建溯源

```yaml
publish_pypi:
  needs: distributions
  if: ${{ inputs.publish }}
  strategy:
    matrix:
      include: ${{ fromJSON(...) }}
  environment:
    name: ${{ matrix.environment }}
    url: https://pypi.org/p/${{ matrix.project }}
  permissions:
    contents: read
    id-token: write
    attestations: write
  steps:
    - uses: actions/download-artifact@v7
      with:
        name: pypi-${{ matrix.project }}
        path: dist
    - uses: actions/attest-build-provenance@v3
      with:
        subject-path: "dist/*"
    - uses: pypa/gh-action-pypi-publish@release/v1
      with:
        packages-dir: dist
```

三个安全属性：

| 属性 | 机制 |
|---|---|
| 无长期令牌 | OIDC trusted publishing，`id-token: write`，不需要 `PYPI_TOKEN` 密钥 |
| 构建溯源 | `attest-build-provenance` 生成 SLSA 风格的出处证明 |
| 爆炸半径隔离 | 两个项目用不同 environment（`pypi` / `pypi-extra-targets`），可分别配置审批人 |

该包 README 解释了为什么必须两个 environment：PyPI 要求 pending publisher 使用**不同身份**，同名会被拒。

### 两个项目分开发布的意义

`publish_packages` 输入允许只发其中一个：

- 若基础包上传成功、add-on 上传失败，可以只重跑 add-on，不必重编 LLVM；
- 发布作业只下载已构建并已校验的 artifact，不重新构建（该包 README 明确：「Separate jobs then upload each project's validated wheels without rebuilding」）。

但要注意顺序风险：该包 README 提醒「Wait for both jobs to succeed before using the All profile from the index」——如果只有 base 上架，用户 `pip install 'mlc-llvm-static[all]'` 会因 add-on 缺失而失败。

## 三个包的 workflow 差异速览

| 维度 | llvm | z3 | doxygen |
|---|---|---|---|
| 前置校验作业 | ✅ `checks` | ❌ 直接铺矩阵 | ❌ |
| 单测前置 | ✅ | ❌（靠 cibuildwheel 的 test-command） | ❌ |
| 独立 sdist 作业 | ❌（只发 wheel） | ✅ | ✅ |
| 平台矩阵 | 5 | 6 | 5 |
| Windows ARM64 | ✅ | ✅ | ❌ |
| PyPI 项目数 | 2 | 1 | 1 |
| 可信发布 environment | 2 个 | 1 个（`pypi`） | 1 个（`pypi`） |

LLVM 之所以要多一层 `checks`，是因为它有两个 PyPI 项目、五平台、小时级构建，任何早期可发现的错误都值得提前拦截。

## 自检方式

```bash
# 1) 本地复算缓存键（与 CI 一致需要有 CC/CXX 环境）
python packages/mlc-llvm-static/scripts/cache_key.py

# 2) 只改打包脚本时键不变（验证"打包不进键"）
md5sum packages/mlc-llvm-static/scripts/compress_wheel.py
python packages/mlc-llvm-static/scripts/cache_key.py
# 修改 compress_wheel.py 再跑一次，key 应相同

# 3) workflow 语法
python -c "import yaml,glob; [yaml.safe_load(open(p,encoding='utf-8')) for p in glob.glob('.github/workflows/*')]; print('ok')"

# 4) 矩阵与文件名模板一致
grep -n "py3-none" .github/workflows/mlc_llvm_static_wheel.yml
```

## 陷阱

- **改 `prepare_llvm.py` 的注释也会让缓存失效**：`inspect.getsource` 取原文。这是保守取舍，不是 bug。
- **不要在 Linux 上省略 `PATH=/opt/python/cp311-cp311/bin`**：manylinux 容器里有多个 Python，默认那个未必装好了 `build`/`scikit-build-core`。
- **`twine check` 不能替代安装测试**：它只校验元数据与 README 渲染。
- **缓存键不含镜像 tag**：镜像内容变化不会让缓存失效，但 `matrix.tag` 在键里，平台变化会。
- **`if: always()` 保存缓存不会覆盖已命中的缓存**：`cache-hit != 'true'` 守卫在。
- **不要在两个 environment 之外发布两个项目**：PyPI 会拒绝同名 pending publisher。

## 延伸阅读

- nightly 流水线的独立编排：[nightly 与稳定版 wheel 流水线](12-nightly-and-stable-wheels.md)
- 缓存的物理形态与恢复逻辑：[LLVM SDK 构建配方](05-llvm-sdk-build-recipe.md)
- 验证作业在本地如何复现：[验证体系](14-verification-strategy.md)
