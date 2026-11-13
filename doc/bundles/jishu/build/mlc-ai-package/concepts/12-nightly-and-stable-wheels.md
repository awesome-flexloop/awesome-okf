---
type: concept
title: nightly 与稳定版 wheel 流水线
description: mlc-ai/mlc-llm 的克隆-改名-容器编译-发布-清理闭环
tags:
  - mlc-ai
  - nightly
  - manylinux
  - auditwheel
  - release
generated: true
verified: false
status: stable
stale_after: "2027-05-01"
sources:
  - "external/dev/libs/mlc-ai/package/packages/mlc-ai/README.md"
  - "external/dev/libs/mlc-ai/package/packages/mlc-ai/scripts/sync_package.py"
  - "external/dev/libs/mlc-ai/package/packages/mlc-ai/scripts/build_mlc_ai_wheel_manylinux.sh"
  - "external/dev/libs/mlc-ai/package/packages/mlc-ai/scripts/wheel_prune_and_sync.py"
  - "external/dev/libs/mlc-ai/package/.github/workflows/wheel_manylinux.yaml"
---

# nightly 与稳定版 wheel 流水线

## 与另外三个包的根本差异

`mlc-llvm-static` / `mlc-z3-static` / `mlc-doxygen-bin` 打包的是**第三方原生库**，输入是固定的上游归档；`mlc-ai` 打包的是**自家上游项目的完整运行时**，输入是一个会移动的 git 仓库。

因此它不做"钉扎 + 下载"，而做"克隆 + 检出 + 改名 + 容器编译 + 上传 + 清理"。目录里没有 `pyproject.toml`（F-120）。

## 三个构建目标

| 目标 | 产出包名（nightly） | 产出包名（stable） |
|---|---|---|
| TVM（`mlc-ai/relax`，克隆为 `tvm/`） | `mlc-ai-nightly-*` | `mlc-ai-*` |
| MLC-LLM（`mlc-ai/mlc-llm`） | `mlc-llm-nightly-*` | `mlc-llm-*` |

后缀由 `name_with_gpu()` 决定（F-123）：

```python
def name_with_gpu(args, package_name):
    if args.gpu == "none":
        return package_name + "-cpu"
    elif args.gpu.startswith("rocm"):
        return package_name + "-rocm" + "".join(args.gpu[5:].split("."))
    else:
        return package_name + "-cu" + "".join(args.gpu[5:].split("."))
```

映射示例：

| `--gpu` | 后缀 |
|---|---|
| `none` | `-cpu` |
| `cuda-12.8` | `-cu128` |
| `cuda-13.0` | `-cu130` |
| `rocm-6.1` | `-rocm61` |
| `rocm-6.2` | `-rocm62` |

改写只发生一次，且只改 `pyproject.toml` 里 `name = "..."` 那一行：

```python
rewrites = [
    (r'(?m)(?<=(?<![^\n])name = ")[^\n"]+(?=")', name_with_gpu(args, args.package_name)),
]
update(os.path.join(args.package, "pyproject.toml"), rewrites, args.dry_run)
```

正则里的 `(?m)` 与行首锚点约束避免误改 `readme = "..."` 之类的字段。

## 稳定版的安全闸：tag 必须显式给出

```python
if "nightly" not in args.package_name:
    if not __stable_build__:
        raise RuntimeError(
            "Stable build requires the MLC_STABLE_BUILD_VER environment variable "
            "to be set to the tag to build (e.g. v0.20.0)."
        )
    checkout_source(args.package, __stable_build__)
else:
    checkout_source(args.package, args.revision)
```

注释解释了一个 CI 细节：

> `not` (rather than `is None`) so an unset OR empty-string env var both error out. CI sets `env: X: ${{ ... }}`, which yields `""` (not unset) when the expression is empty.

这是一个真实踩过的坑：GitHub Actions 里未赋值的表达式会变成空串而非"未设置"，用 `is None` 判断会漏掉。

## 递归子模块：为什么必须 `--recursive`

```python
run_cmd(["git", "checkout", "-f", tag])
run_cmd(["git", "submodule", "update", "--init", "--recursive"])
```

注释给出了具体链路：

> mlc-llm pins 3rdparty/tvm, which pins its own 3rdparty/tvm-ffi. A plain `submodule update` moves 3rdparty/tvm to the tag but leaves the nested tvm-ffi at whatever the initial clone had, so tvm gets built against a mismatched tvm-ffi.

即：`mlc-llm` → `3rdparty/tvm` → `3rdparty/tvm-ffi` 是三层嵌套。非递归更新会让最内层停在初始克隆的版本，导致 TVM 与 TVM-FFI 版本错配——这类错配的报错通常在链接期，极难定位。

## GPU 变体与镜像

`wheel_manylinux.yaml` 的矩阵（F-124）：

```yaml
matrix:
  config:
    - gpu: 'none'      image: 'mlcaidev/package-cpu:655adb5'
    - gpu: 'cuda-12.8' image: 'mlcaidev/package-cu128:655adb5'
    - gpu: 'cuda-13.0' image: 'mlcaidev/package-cu130:655adb5'
    - gpu: 'rocm-6.1'  image: 'mlcaidev/package-rocm61:655adb5'
    - gpu: 'rocm-6.2'  image: 'mlcaidev/package-rocm62:655adb5'
```

镜像由 `.github/workflows/build_docker_package.yaml` 手动构建并推送到 Docker Hub（F-134），标签是提交短哈希（`git log -1 --format='%h'`）。因此镜像 tag `655adb5` 对应仓库的某个提交——镜像内容与仓库版本可追溯。

`Dockerfile.package-cpu` 的基底是 `quay.io/pypa/manylinux_2_28_x86_64`，依次安装 core、cmake、llvm、vulkan sdk、patchelf、conda、Python 3.13、auditwheel、Rust，并设 `AUDITWHEEL_PLAT=manylinux_2_28_x86_64`（F-135）。

注意它装的是 **Python 3.13**（conda 环境 `py313`），与 PyPI 三个包用 3.11 不同：前者构建的是最终运行时（需要较新 Python），后者只是用某个解释器驱动打包。

### 自托管 runner 的清理

```yaml
- name: Checkout source
  env:
    IMAGE: ${{ matrix.config.image }}
  run: |
    "$GITHUB_WORKSPACE/docker/bash.sh" --no-gpu $IMAGE ./scripts/cleanup_workspace.sh
    git clone https://github.com/mlc-ai/relax tvm --recursive
    git clone https://github.com/mlc-ai/mlc-llm mlc-llm --recursive
```

注释解释了必要性：

> Self-hosted runners persist the workspace between runs; a prior or cancelled build leaves root-owned files under tvm/ and mlc-llm/ that actions/checkout's git clean cannot remove. Delete them as root (inside the build image) before cloning.

容器内以 root 删除，然后回到宿主执行 `git clone`——顺序不能反。

## 容器内构建

`build_mlc_ai_wheel_manylinux.sh` 的关键行（F-128、F-129）：

```bash
source /opt/rh/gcc-toolset-13/enable   # 与 mlc-z3-static 的 manylinux 构建保持一致
...
pip install --no-deps ./3rdparty/tvm-ffi
pip wheel --no-deps -w dist . -v
mkdir -p repaired_wheels
auditwheel repair ${AUDITWHEEL_OPTS} dist/mlc_ai*.whl
```

### 为什么先装 in-tree 的 tvm-ffi

注释说明：`apache-tvm-ffi`（pip 包）可能落后于正在构建的 revision，所以从仓库内子模块安装；随后 `pip wheel --no-deps` 避免 pip 去 PyPI 重新解析 `apache-tvm-ffi` 与其他依赖。

### auditwheel 的排除项

```bash
AUDITWHEEL_OPTS="--exclude libtinfo --exclude libtvm_ffi ${AUDITWHEEL_OPTS}"
if [[ ${GPU} == rocm* ]]; then
    AUDITWHEEL_OPTS="--exclude libamdhip64 --exclude libhsa-runtime64 --exclude librocm_smi64 --exclude librccl --exclude libhipblas --exclude libhipblaslt ${AUDITWHEEL_OPTS}"
elif [[ ${GPU} == cuda* ]]; then
    AUDITWHEEL_OPTS="--exclude libcuda --exclude libcudart --exclude libnvrtc --exclude libcublas --exclude libcublasLt ${AUDITWHEEL_OPTS}"
fi
```

排除逻辑的含义是"这些库由用户环境提供，不要打进 wheel"：

| 类别 | 排除的库 |
|---|---|
| 通用 | `libtinfo`（终端能力库，发行版提供）、`libtvm_ffi`（由独立 pip 包提供） |
| CUDA | `libcuda`（驱动）、`libcudart`/`libnvrtc`/`libcublas`/`libcublasLt`（CUDA 运行时） |
| ROCm | `libamdhip64`/`libhsa-runtime64`/`librocm_smi64`/`librccl`/`libhipblas`/`libhipblaslt` |

这与"原生 SDK wheel"的策略正好相反：那边追求自包含，这边追求"不重复分发驱动与大型运行时"。

### CMake 配置的写法

```bash
echo set\(HIDE_PRIVATE_SYMBOLS ON\) >>config.cmake
echo set\(USE_RPC ON\) >>config.cmake
echo set\(USE_VULKAN ON\) >>config.cmake
echo set\(USE_Z3 OFF\) >>config.cmake
```

TVM 的构建通过一个追加式的 `config.cmake` 驱动。要点：

- `HIDE_PRIVATE_SYMBOLS ON`：隐藏内部符号，减少多扩展共存时的符号冲突；
- `USE_RPC ON`、`USE_VULKAN ON`：默认开启的能力；
- `USE_Z3 OFF`：不引入 Z3 依赖（与 `mlc-z3-static` 的存在并不矛盾——需要 Z3 的用户可自行开启）。

CUDA 分支还会按版本探测 `nvshmem`：

```bash
for cuda_version in 12; do
    if [ -d "/usr/include/nvshmem_${cuda_version}" ]; then
        mkdir -p /workspace/nvshmem
        ...
        echo set\(USE_NVSHMEM /workspace/nvshmem\) >>config.cmake
        break
    fi
done
```

CUDA 架构列表由共享函数给出（F-130）：

```bash
function cuda_archs_for() {
    local archs="80;89;90a"
    if [[ ${gpu} == cuda-12.8 || ${gpu} == cuda-13.0 ]]; then archs="${archs};120"; fi
    if [[ ${gpu} == cuda-13.0 ]]; then archs="${archs};110"; fi
    echo "${archs}"
}
```

`80`=A100、`89`=L40S/4090、`90a`=H100、`120`=Blackwell 消费级、`110`=Blackwell 数据中心。只对 13.0 加 `110`，说明该架构需要更新的 CUDA 工具链。

## 发布：GitHub Release 而非 PyPI

```yaml
- name: Wheel-Deploy
  if: github.ref == 'refs/heads/main'
  uses: softprops/action-gh-release@v3
  with:
    files: |
      packages/mlc-ai/tvm/repaired_wheels/*.whl
      packages/mlc-ai/mlc-llm/repaired_wheels/*.whl
    tag_name: v0.9.dev0
    prerelease: true
```

所有 nightly 都挂在同一个 `v0.9.dev0` prerelease 上，靠文件名区分版本。稳定版也是走这条通路（只是包名不带 `-nightly`）。

为什么不用 PyPI？因为 nightly 每天产生数十个 wheel，PyPI 不适合这种高频覆盖式发布；GitHub Release 更适合"同一 tag 下大量资产"的模型。

## 清理与索引：`wheel_prune_and_sync.py`

### 分组算法

`extract_group_key_order(name)`（F-131）把 wheel 文件名拆成"组键 + 排序键"：

```python
pkg_name = arr[0]
group_key = [arr[0]] + arr[2:]      # 包名 + 平台/ABI 等后续字段
ver = arr[1]
...
if dev_pos != -1:
    group_key.append("nightly")     # 所有 nightly 同组
    order = pub_ver + [int(ver[dev_pos + 4:])]
else:
    group_key.append(ver)           # 稳定版按版本各自成组
    order = [0]
```

效果：

- 同一包、同一平台、同一 ABI 的所有 nightly 归为一组，只保留最新的 N 个；
- 每个稳定版自成一组建，永不被 nightly 清理挤掉。

`--keep-top` 默认 1，即每组只留最新一条。

### 顺序：先改页面，再删资产

```python
# NOTE: important to update html first before deletion
# so that the wheel page always points to correct asset
update_wheel_page(keep_list, args.site_path, args.dry_run)
delete_assets(remove_list, args.dry_run)
```

`update_wheel_page()` 生成极简 HTML：

```python
new_html = '<!DOCTYPE html>\n<html>\n<body>\n'
for asset in keep_list:
    new_html += '<a href="%s">%s</a><br>\n' % (asset.browser_download_url, asset.name)
new_html += '</body>\n</html>'
```

然后 `git fetch` → `git checkout -B main origin/main` → 内容有变则提交并推送。

`list_wheels()` 还会用 `url_is_valid()` 做 HEAD 探测（最多重试 5 次），过滤掉"资产存在但 URL 已失效"的条目。

### 上传重试

`wheel_upload.py` 的顺序是"先删同名再上传"，失败按指数退避 + 随机抖动（F-133）：

```python
backoff = min(backoff * backoff_scale, max_backoff)   # max 600 秒
retry_gap = backoff * (random.random() + 0.5)
```

随机抖动是为了避免多个并行 job 同时重试造成新的竞争。

## 自检方式

```bash
# 1) 稳定版缺少 tag 时必须失败
MLC_STABLE_BUILD_VER= python packages/mlc-ai/scripts/sync_package.py \
  --package tvm --package-name mlc-ai --skip-checkout --dry-run 2>&1 | tail -2

# 2) GPU 后缀映射
python - <<'PY'
import sys; sys.path.insert(0, "packages/mlc-ai/scripts")
from sync_package import name_with_gpu
class A: pass
for gpu in ("none", "cuda-12.8", "cuda-13.0", "rocm-6.1", "rocm-6.2"):
    a = A(); a.gpu = gpu
    print(gpu, "→", name_with_gpu(a, "mlc-ai-nightly"))
PY

# 3) 分组是否把稳定版单独成组
python - <<'PY'
import sys; sys.path.insert(0, "packages/mlc-ai/scripts")
from wheel_prune_and_sync import extract_group_key_order as k
for n in ("mlc_ai_nightly_cu128-0.20.dev123-cp311-cp311-linux_x86_64.whl",
          "mlc_ai_cu128-0.20.0-cp311-cp311-linux_x86_64.whl"):
    print(k(n)[0])
PY

# 4) 清理演练（不写任何东西）
python packages/mlc-ai/scripts/wheel_prune_and_sync.py --dry-run --site-path /tmp/wheels
```

## 陷阱

- **`--skip-checkout` 只用于 nightly**：稳定版必须检出 tag，跳过会构建当前检出而不是目标版本。
- **`MLC_STABLE_BUILD_VER=""` 与未设置等价**：用 `not` 判断而非 `is None`。
- **嵌套子模块必须 `--recursive`**：否则 tvm-ffi 会停在初始版本。
- **`prune` 的顺序不能反**：先删资产会让页面短暂指向 404。
- **`group_key` 包含平台/ABI 字段**：分组粒度是"每包每平台"，不是"每包"。
- **镜像 tag 是提交短哈希**：换镜像等于换构建环境，`AUDITWHEEL_PLAT` 也随之变化。
- **不要在 PR 上期待上传**：`github.ref == 'refs/heads/main'` 守卫会跳过。

## 延伸阅读

- CI 的整体编排：[CI 工作流与 SDK 缓存](13-ci-workflows-and-caching.md)
- 消费这些 wheel 的发布记录与索引：[仓库布局与发布模型](01-repo-layout-and-release-model.md)
- 容器镜像与环境：[CI 工作流与 SDK 缓存](13-ci-workflows-and-caching.md)
- GPU 变体与参数速查：[环境变量与输入参数](../references/01-env-vars-and-inputs.md)
