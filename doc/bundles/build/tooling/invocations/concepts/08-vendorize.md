---
type: Concept
title: 依赖 Vendorize 管理
description: 使用 vendorize 任务将第三方 Python 包下载复制到项目 vendor 目录，实现依赖内嵌
tags: [invocations, vendorize, vendoring, dependencies, packaging]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T14:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T16:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: invocations-source
    resource: /references/invocations-source.md
---

# 依赖 Vendorize 管理

`invocations.packaging.vendorize` 模块提供将第三方 Python 包"内嵌"（vendor）到项目中的自动化任务。Vendorizing 是将依赖包的源码直接复制到项目目录树中的做法，常见于需要控制依赖版本、避免安装冲突或保证离线可用性的项目。

## 什么是 Vendorizing

Vendorizing（"贩卖"依赖）指将第三方库的源码复制到你自己的项目中，作为项目源码的一部分分发，而不是通过 pip 等包管理器在安装时解析依赖。

**优点**：
- 完全控制依赖版本，不受上游 breaking changes 影响
- 避免依赖冲突（你的项目和其他依赖需要同一包的不同版本）
- 离线可用，不需要网络安装
- 可以对依赖做针对性修改（monkey patch）

**缺点**：
- 增加项目体积
- 需要手动更新安全补丁
- 可能造成许可证合规问题（需保留依赖的许可证）

## 使用方法

```python
# tasks.py
from invoke import Collection
from invocations.packaging.vendorize import vendorize

ns = Collection(vendorize)
```

## vendorize 任务

```bash
# 从 PyPI vendorize 一个包
inv vendorize --distribution=lexicon --version=0.1.2 --vendor-dir=myproject/vendor

# 当包名和目录名不同时
inv vendorize --distribution=PyYAML --version=6.0 --vendor-dir=myproject/vendor --package=yaml

# 从 Git 仓库 vendorize
inv vendorize --distribution=my-package --version=main --vendor-dir=vendor --git-url=https://github.com/example/repo.git

# 复制许可证文件
inv vendorize --distribution=some-package --version=1.0 --vendor-dir=vendor --license=LICENSE
```

### 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|:----:|------|
| `distribution` | str | ✅ | PyPI 上的分发包名 |
| `version` | str | ✅ | 版本号（PyPI）或 Git 标识符（branch/tag/SHA） |
| `vendor_dir` | str | ✅ | 目标 vendor 目录路径 |
| `package` | str | ❌ | 解压后的包目录名（与 distribution 不同时需要指定） |
| `git_url` | str | ❌ | Git 仓库 URL（指定后从 Git 获取而非 PyPI） |
| `license` | str | ❌ | 许可证文件在源码中的相对路径，指定后会复制到 vendor 目录 |

## 工作流程

`vendorize` 任务的执行步骤：

1. **创建临时目录**：使用 `tmpdir()` 上下文管理器创建临时工作目录
2. **下载并解压**（PyPI 模式）：
   - `chdir` 到临时目录
   - 执行 `pip install --download=. --build=build --no-use-wheel <distribution>==<version>` 下载 sdist（注意：这是旧版 pip 的下载模式）
   - 识别下载的归档文件格式（zip/tgz/tar.gz）
   - 解压归档文件
3. **定位包目录**：在解压后的源码中找到目标包目录
4. **清理目标**：如果 vendor 目录中已存在同名包，先删除
5. **复制**：使用 `shutil.copytree` 将包目录复制到 vendor 目录
6. **许可证**：如果指定了 `license` 参数，额外复制许可证文件
7. **自动清理**：退出 `tmpdir` 上下文时自动删除临时目录

## Git 模式（未完全实现）

`_unpack` 函数中预留了 Git 模式的框架（`if git_url: pass`），但当前实现主要支持 PyPI sdist 模式。Git 模式的预期行为是：
- `git clone` 到临时目录
- `git checkout <version>`
- 如果 version 不像 SHA，获取该分支的 HEAD SHA 作为 real_version

## 实际案例

Invoke 自身就使用了 vendorizing 模式——`invoke/vendor/` 目录内嵌了三个依赖：
- `fluidity`（状态机库）
- `lexicon`（属性字典）
- `yaml`（PyYAML 的完整副本）

这种做法使得 Invoke 的核心功能零外部依赖即可运行。

## Vendorizing 后的使用

Vendor 目录中的包需要通过路径调整来导入。常见做法：

```python
# myproject/vendor/__init__.py 或通过 sys.path 调整
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

# 然后直接导入 vendor 包
from myproject.vendor import lexicon
```

或者在每个 vendor 包中放置说明文件，指导如何将 vendor 目录加入 sys.path。

## 注意事项

- `vendorize` 使用的是旧版 pip 的 `--download`/`--build`/`--no-use-wheel` 参数，新版 pip 可能已移除这些选项，可能需要适配
- 只下载 sdist（不下载 wheel），因为需要源码而非编译产物
- Vendorizing 不自动处理嵌套依赖——你需要手动 vendorize 所有传递依赖
- 记得在项目文档中声明 vendor 包及其版本和许可证
- 定期检查 vendor 包的安全更新

## 相关概念

- [包发布生命周期](05-packaging-release.md)
- [工具函数与文件监控](07-utilities-watchers.md)（tmpdir 被 vendorize 使用）
- [组合模式：组装自己的任务集合](10-composition-patterns.md)

[^invocations-source]: Invocations 源码信源，见 [invocations-source.md](../references/invocations-source.md)。
