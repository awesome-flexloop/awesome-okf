---
type: Example
title: 打包安装验证模式
description: 使用 release.test_install 在临时虚拟环境中验证包的安装、导入和类型检查，防止发布有问题的包
tags: [invocations, example, packaging, test-install, venv, verification]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T14:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T16:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: invocations-source
    resource: /references/invocations-source.md
---

# 打包安装验证模式

本示例展示 release 模块中的 `test_install` 任务如何在发布前验证包的安装质量，以及如何在自定义流程中复用这种验证模式。

## 为什么需要安装验证

`python -m build` 成功不代表包可以正常安装和使用。常见的发布问题：
- `pyproject.toml` 中遗漏了依赖，导致 `pip install` 后 import 失败
- 包数据文件（如 `py.typed`、模板文件）未正确包含在分发包中
- 二进制 wheel 缺少必要的共享库
- 类型存根（`py.typed`）存在但类型检查失败
- README 在 PyPI 上渲染失败（twine check 可捕获）

Invocations 的 `publish` 任务内置了多层防御链：`twine check` → `test_install` → `upload`，确保只有通过验证的包才会发布。

## 使用内置的 test_install

```bash
# 构建并在临时 venv 中测试安装
inv release.build --directory=dist
inv release.test-install --directory=dist

# 详细输出模式
inv release.test-install --directory=dist --verbose

# 跳过 import 测试（只验证安装不报错）
inv release.test-install --directory=dist --skip-import
```

## test_install 的工作流程

```
1. 创建临时目录（tmpdir）
2. 使用 venv 创建虚拟环境
3. 升级 venv 内 pip 到与外部一致的版本
4. pip install <archive>（对每个 .whl 和 .tar.gz 分别测试）
5. python -c 'import <package>'（验证导入成功）
6. 如果存在 py.typed，安装 mypy 并验证 mypy -c 'import <package>'
7. 删除临时 venv 和临时目录
```

关键设计点：
- 每个 archive 在独立的临时 venv 中测试，互不干扰
- wheel 优先测试（sorted by glob，.whl 排在 .tar.gz 前面）
- pip 版本对齐避免旧 pip 的安装问题
- mypy 类型检查只在包标记了 `py.typed` 时执行

## 自定义安装验证

你可以参考 `test_install` 的模式，在自定义任务中添加更全面的安装后验证：

```python
from invoke import task, Collection
from invocations.util import tmpdir
from invocations.packaging.release import build as release_build, get_archives
from pathlib import Path
import venv

@task
def verify_install(c, directory="dist", verbose=False):
    """增强版安装验证：安装 + 导入 + CLI 测试 + 基本功能"""
    archives = get_archives(directory)
    if not archives:
        c.run(f"ls -la {directory}")
        raise Exit(f"在 {directory} 中未找到构建产物")
    
    builder = venv.EnvBuilder(with_pip=True)
    package = _find_package(c)
    failures = []
    
    for archive in archives:
        archive_name = archive.name
        print(f"\n{'='*60}")
        print(f"验证: {archive_name}")
        print(f"{'='*60}")
        
        with tmpdir() as tmp:
            # 创建 venv
            builder.create(tmp)
            envbin = Path(tmp) / "bin"
            pip = envbin / "pip"
            python = envbin / "python"
            
            # 升级 pip
            c.run(f"{pip} install --quiet pip>=23", hide=not verbose)
            
            # 安装包
            result = c.run(f"{pip} install {archive}", warn=True, hide=not verbose)
            if result.failed:
                failures.append(f"{archive_name}: pip install 失败")
                continue
            print("  ✔ pip install 成功")
            
            # 1. 验证导入
            result = c.run(f'{python} -c "import {package}"', warn=True, hide=not verbose)
            if result.failed:
                failures.append(f"{archive_name}: import {package} 失败")
                continue
            print(f"  ✔ import {package} 成功")
            
            # 2. 验证版本号
            result = c.run(
                f'{python} -c "import {package}; print({package}.__version__)"',
                hide=True
            )
            print(f"  ✔ 版本号: {result.stdout.strip()}")
            
            # 3. 验证 CLI 入口点（如果有）
            result = c.run(f"{python} -m {package} --help", warn=True, hide=not verbose)
            if result.ok:
                print(f"  ✔ CLI --help 成功")
            
            # 4. 验证关键依赖可导入
            deps = ["invoke", "blessings"]  # 你的关键依赖列表
            for dep in deps:
                result = c.run(f'{python} -c "import {dep}"', warn=True, hide=True)
                if result.failed:
                    failures.append(f"{archive_name}: 依赖 {dep} 未正确安装")
                else:
                    print(f"  ✔ 依赖 {dep} 可用")
    
    # 汇总
    print(f"\n{'='*60}")
    if failures:
        print(f"❌ 验证失败 ({len(failures)} 个问题):")
        for f in failures:
            print(f"  - {f}")
        raise Exit("安装验证失败!")
    else:
        print(f"✅ 所有 {len(archives)} 个包验证通过!")

def _find_package(c):
    """自动检测包名（复用 release 中的逻辑）"""
    from invocations.packaging.release import _find_package
    return _find_package(c)

ns = Collection(verify_install)
ns.configure({
    "packaging": {"package": "myproject"},
})
```

## 本地快速验证流程

在发布前，建议运行以下完整验证链：

```bash
# 1. 清理并构建
inv release.build --clean --directory=dist

# 2. twine check（验证元数据和 README）
twine check dist/*

# 3. 安装验证
inv release.test-install --directory=dist --verbose

# 4. 干跑上传
inv release.publish --dry-run

# 5. 全部通过后正式发布
inv release
```

## 在 CI 中验证

在 CI 流水线中添加安装验证步骤：

```yaml
# .github/workflows/release.yml 示例
jobs:
  verify-package:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -e '.[dev]'
      - run: inv release.build --clean
      - run: inv release.test-install --directory=dist --verbose
      - run: twine check dist/*
```

## 防御性发布检查清单

参考 release 模块的多层防御设计，你的发布流程应包含：

- [ ] **构建验证**：sdist 和 wheel 都能成功构建
- [ ] **元数据验证**：twine check 通过（README 渲染、元数据完整）
- [ ] **安装验证**：在干净 venv 中 pip install 成功
- [ ] **导入验证**：安装后可以 import 包
- [ ] **CLI 验证**（如果有 CLI）：`--help` 正常工作
- [ ] **类型验证**（如果有 py.typed）：mypy 导入检查通过
- [ ] **功能冒烟测试**：基本功能在安装后可用
- [ ] **dry-run**：发布命令先以 dry-run 模式执行

## 相关概念

- [包发布生命周期](/concepts/05-packaging-release.md)
- [工具函数与文件监控](/concepts/07-utilities-watchers.md)（tmpdir 上下文管理器）
- [自定义发布流程示例](/examples/custom-release-flow.md)

[^invocations-source]: Invocations 源码信源，见 [invocations-source.md](/references/invocations-source.md)。
