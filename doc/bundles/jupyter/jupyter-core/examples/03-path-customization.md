---
okf_version: "0.2"
type: example
title: "路径定制与环境变量"
description: "通过代码示例学习如何使用环境变量自定义 Jupyter 目录、利用虚拟环境路径隔离、自定义配置加载路径，以及多环境配置隔离。"
tags: [jupyter, core, example, paths, environment-variables, configuration, virtualenv]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T12:30:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T12:30:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: paths-py
    resource: "../../../../../external/libs/jupyter/jupyter_core/jupyter_core/paths.py"
    title: "jupyter_core/paths.py"
---

# 路径定制与环境变量

本示例展示如何通过环境变量和 Python API 自定义 jupyter_core 的路径行为，包括目录重定向、虚拟环境隔离、运行时安全等场景。

## 示例 1：通过环境变量自定义 Jupyter 目录

在导入 jupyter_core 之前设置环境变量，可以完全控制各类目录的位置。

```python
"""通过环境变量自定义 Jupyter 目录位置"""

import os
import tempfile
from pathlib import Path

# --- 创建临时目录作为演示 ---
with tempfile.TemporaryDirectory() as tmpdir:
    tmp = Path(tmpdir)
    custom_config = str(tmp / "my-config")
    custom_data = str(tmp / "my-data")
    custom_runtime = str(tmp / "my-runtime")

    # 在导入 jupyter_core.paths 之前设置环境变量
    os.environ["JUPYTER_CONFIG_DIR"] = custom_config
    os.environ["JUPYTER_DATA_DIR"] = custom_data
    os.environ["JUPYTER_RUNTIME_DIR"] = custom_runtime

    # 导入 paths 模块（必须在设置环境变量之后）
    from jupyter_core.paths import (
        jupyter_config_dir,
        jupyter_data_dir,
        jupyter_runtime_dir,
    )

    # 验证目录已被重定向
    config_dir = jupyter_config_dir()
    data_dir = jupyter_data_dir()
    runtime_dir = jupyter_runtime_dir()

    print("=" * 50)
    print("环境变量重定向后的目录")
    print("=" * 50)
    print(f"配置目录:  {config_dir}")
    print(f"  预期: {custom_config}")
    print(f"  ✓ 匹配" if config_dir == custom_config else f"  ✗ 不匹配")

    print(f"\n数据目录:  {data_dir}")
    print(f"  预期: {custom_data}")
    print(f"  ✓ 匹配" if data_dir == custom_data else f"  ✗ 不匹配")

    print(f"\n运行时目录: {runtime_dir}")
    print(f"  预期: {custom_runtime}")
    print(f"  ✓ 匹配" if runtime_dir == custom_runtime else f"  ✗ 不匹配")
```

## 示例 2：附加自定义搜索路径

通过 `JUPYTER_PATH` 和 `JUPYTER_CONFIG_PATH` 环境变量附加额外的搜索路径。

```python
"""附加自定义搜索路径"""

import os
import tempfile
from pathlib import Path

with tempfile.TemporaryDirectory() as tmpdir:
    tmp = Path(tmpdir)

    # 创建自定义搜索路径
    extra_data = str(tmp / "extra-data")
    extra_config = str(tmp / "extra-config")
    os.makedirs(extra_data)
    os.makedirs(extra_config)

    # 设置附加路径环境变量（使用 os.pathsep 分隔多个路径）
    os.environ["JUPYTER_PATH"] = extra_data + os.pathsep
    os.environ["JUPYTER_CONFIG_PATH"] = extra_config + os.pathsep

    # 清理之前的导入缓存（演示需要）
    import importlib
    from jupyter_core import paths as paths_module
    importlib.reload(paths_module)

    from jupyter_core.paths import jupyter_path, jupyter_config_path

    print("=" * 50)
    print("附加搜索路径后的数据搜索路径")
    print("=" * 50)
    data_paths = jupyter_path()
    print(f"第一个路径（最高优先级）: {data_paths[0]}")
    assert data_paths[0] == extra_data, "JUPYTER_PATH 中的路径应位于最前面"
    print("✓ 自定义数据路径位于搜索路径最前面")

    print("\n配置搜索路径:")
    config_paths = jupyter_config_path()
    print(f"第一个路径（最高优先级）: {config_paths[0]}")
    assert config_paths[0] == extra_config, "JUPYTER_CONFIG_PATH 中的路径应位于最前面"
    print("✓ 自定义配置路径位于搜索路径最前面")
```

## 示例 3：虚拟环境/conda 环境路径行为

在虚拟环境或 conda 环境中，jupyter_core 会自动将环境内的路径优先于用户目录，实现包隔离。

```python
"""检测当前环境是否为虚拟环境/conda环境，并观察路径优先级"""

import os
import sys

from jupyter_core.paths import (
    jupyter_path,
    jupyter_config_path,
    prefer_environment_over_user,
)

print("=" * 50)
print("虚拟环境检测")
print("=" * 50)

# 检测是否在虚拟环境中
in_venv = sys.prefix != sys.base_prefix
in_conda = "CONDA_PREFIX" in os.environ and os.environ.get("CONDA_DEFAULT_ENV", "base") != "base"

print(f"sys.prefix:       {sys.prefix}")
print(f"sys.base_prefix:  {sys.base_prefix}")
print(f"在虚拟环境中:     {'是' if in_venv else '否'}")
print(f"在非base conda环境: {'是' if in_conda else '否'}")
print(f"环境路径优先:     {'是' if prefer_environment_over_user() else '否'}")

# 观察路径顺序
print("\n" + "=" * 50)
print("路径优先级分析")
print("=" * 50)

env_data_path = str(Path(sys.prefix) / "share" / "jupyter")
env_config_path = str(Path(sys.prefix) / "etc" / "jupyter")

data_paths = jupyter_path()
config_paths = jupyter_config_path()

# 检查 env 路径和 user 路径的相对位置
user_data_idx = None
env_data_idx = None
for idx, p in enumerate(data_paths):
    if str(Path(p)) == env_data_path:
        env_data_idx = idx
    if p.endswith(os.sep + "jupyter") and ".local" in p or ".jupyter" in p:
        if "share" in p and user_data_idx is None:
            if p.startswith(str(Path.home())):
                user_data_idx = idx
                break

if prefer_environment_over_user():
    print("环境优先模式: sys.prefix 路径应在用户目录之前")
else:
    print("用户优先模式: 用户目录应在 sys.prefix 路径之前")

print(f"\n数据搜索路径（前3个）:")
for i, p in enumerate(data_paths[:3]):
    print(f"  {i + 1}. {p}")

print(f"\n配置搜索路径（前3个）:")
for i, p in enumerate(config_paths[:3]):
    print(f"  {i + 1}. {p}")
```

注意：上面代码需要在顶部导入 `Path`：

```python
from pathlib import Path
```

## 示例 4：确保运行时目录安全权限

运行时目录（存放内核连接文件等敏感信息）应具有严格的权限设置。`JupyterApp` 自动创建 runtime_dir 时设置 0o700 权限。

```python
"""运行时目录安全权限设置"""

import os
import stat
import tempfile
from pathlib import Path

from jupyter_core.paths import jupyter_runtime_dir, secure_write
from jupyter_core.utils import ensure_dir_exists

# --- 确保运行时目录存在且权限正确 ---
runtime_dir = jupyter_runtime_dir()
ensure_dir_exists(runtime_dir, mode=0o700)

print("=" * 50)
print("运行时目录安全检查")
print("=" * 50)
print(f"运行时目录: {runtime_dir}")
print(f"目录存在:   {'✓' if Path(runtime_dir).is_dir() else '✗'}")

# 检查目录权限（Unix 系统）
if os.name != "nt":
    dir_mode = stat.S_IMODE(os.stat(runtime_dir).st_mode)
    print(f"目录权限:   {oct(dir_mode)}")
    if dir_mode == 0o700:
        print("✓ 权限正确（仅所有者可读写执行）")
    else:
        print(f"⚠ 权限不是 0o700，建议设置: chmod 700 {runtime_dir}")

# --- 在运行时目录中安全写入文件 ---
conn_file = str(Path(runtime_dir) / "kernel-secure-demo.json")
with secure_write(conn_file) as f:
    f.write('{"key": "secret-connection-info"}')

# 验证文件权限
if os.name != "nt":
    file_mode = stat.S_IMODE(os.stat(conn_file).st_mode)
    print(f"\n连接文件权限: {oct(file_mode)}")
    assert file_mode == 0o600, f"文件权限应为 0o600，实际 {oct(file_mode)}"
    print("✓ 文件权限正确（仅所有者可读写）")

# 清理测试文件
try:
    os.unlink(conn_file)
except OSError:
    pass
```

## 示例 5：多环境 Jupyter 配置隔离

在不同项目中使用完全隔离的 Jupyter 配置，通过 `JUPYTER_NO_CONFIG` 或自定义目录实现。

```python
"""多环境 Jupyter 配置隔离方案"""

import os
import tempfile
from pathlib import Path

from jupyter_core.paths import jupyter_config_dir, jupyter_config_path


def setup_isolated_env(project_dir):
    """为指定项目设置隔离的 Jupyter 环境。

    在项目目录下创建独立的 .jupyter 配置和数据目录，
    并通过环境变量指向这些目录。
    """
    project = Path(project_dir)
    jupyter_dir = project / ".jupyter"
    data_dir = project / ".jupyter-data"
    runtime_dir = project / ".jupyter-runtime"

    # 创建目录
    jupyter_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)
    runtime_dir.mkdir(parents=True, exist_ok=True)

    # 设置环境变量
    os.environ["JUPYTER_CONFIG_DIR"] = str(jupyter_dir)
    os.environ["JUPYTER_DATA_DIR"] = str(data_dir)
    os.environ["JUPYTER_RUNTIME_DIR"] = str(runtime_dir)

    return jupyter_dir, data_dir, runtime_dir


# --- 演示项目隔离 ---
with tempfile.TemporaryDirectory() as tmpdir:
    print("=" * 50)
    print("项目A 隔离环境")
    print("=" * 50)
    project_a = Path(tmpdir) / "project-a"
    project_a.mkdir()
    cfg_a, data_a, rt_a = setup_isolated_env(str(project_a))

    # 导入 paths 模块（在实际使用中应在程序启动时设置环境变量）
    import importlib
    from jupyter_core import paths
    importlib.reload(paths)

    print(f"配置目录: {jupyter_config_dir()}")
    print(f"  包含在项目目录中: {'✓' if str(project_a) in jupyter_config_dir() else '✗'}")

    print("\n" + "=" * 50)
    print("使用 JUPYTER_NO_CONFIG 实现完全干净环境")
    print("=" * 50)

    # 使用 JUPYTER_NO_CONFIG 创建临时干净环境（适合 CI/测试）
    os.environ.pop("JUPYTER_CONFIG_DIR", None)
    os.environ.pop("JUPYTER_DATA_DIR", None)
    os.environ.pop("JUPYTER_RUNTIME_DIR", None)
    os.environ["JUPYTER_NO_CONFIG"] = "1"

    importlib.reload(paths)

    no_cfg_dir = jupyter_config_dir()
    no_cfg_paths = jupyter_config_path()
    print(f"NO_CONFIG 模式配置目录: {no_cfg_dir}")
    print(f"  是临时目录: {'✓' if 'jupyter-clean-cfg' in no_cfg_dir or 'tmp' in no_cfg_dir.lower() else '✗'}")
    print(f"配置搜索路径数量: {len(no_cfg_paths)}")
    print(f"  仅包含临时目录: {'✓' if len(no_cfg_paths) == 1 else '✗'}")

    # 清理
    del os.environ["JUPYTER_NO_CONFIG"]
```

注意：上面示例代码需要在顶部补充导入：

```python
from jupyter_core.paths import jupyter_config_dir, jupyter_data_dir, jupyter_runtime_dir
```

---

**下一步阅读：**
- [路径系统详解](../concepts/03-path-system.md) — 深入理解路径优先级和安全机制
- [环境变量参考](../concepts/08-environment-variables.md) — 所有环境变量的完整参考
