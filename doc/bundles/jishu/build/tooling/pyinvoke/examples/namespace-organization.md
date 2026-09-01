---
type: Example
title: 命名空间组织大型项目
description: 使用 Collection 和嵌套模块组织大型项目的任务，含模块化目录结构示例
tags: [pyinvoke, collection, namespace, from_module, modular, nested, example]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: pyinvoke-src
    resource: /references/pyinvoke-source.md
    title: "PyInvoke 源码"
---

# 命名空间组织大型项目

当项目任务数量增多时，单文件 `tasks.py` 会变得难以维护。本示例展示如何使用 `Collection` 和 `Collection.from_module()` 将任务拆分到多个模块中，通过命名空间嵌套组织大型项目。[^pyinvoke-src]

## 1. 目录结构

将任务拆分为一个 Python 包，按功能领域划分子模块：

```
myproject/
├── tasks/                  # 任务包（替代单文件 tasks.py）
│   ├── __init__.py         # 命名空间入口，组装所有子集合
│   ├── build.py            # 构建相关任务
│   ├── deploy.py           # 部署相关任务
│   └── test.py             # 测试相关任务
└── src/                    # 项目源代码
    └── ...
```

## 2. 编写子模块任务

每个子模块独立定义各自领域的任务，使用 `@task` 装饰器标记：

```python
# tasks/build.py
from invoke import task


@task
def compile(c):
    """编译源代码。"""
    c.run("echo '编译 TypeScript → JavaScript'")
    c.run("echo '编译 Cython 扩展'")


@task
def bundle(c, minify=False):
    """打包产物，可选压缩。"""
    cmd = "echo '打包应用产物'"
    if minify:
        cmd += " && echo '压缩混淆 JavaScript/CSS'"
    c.run(cmd)


@task(default=True)
def all(c, minify=False):
    """执行完整构建流程（compile + bundle）。"""
    c.run("inv build.compile")
    c.run(f"inv build.bundle --minify={minify}")
```

```python
# tasks/deploy.py
from invoke import task, Collection


@task
def staging(c):
    """部署到预发布环境。"""
    c.run("echo '部署到 staging 服务器...'")
    c.run("echo '运行冒烟测试...'")


@task
def production(c, dry_run=False):
    """部署到生产环境。"""
    if dry_run:
        c.run("echo '[DRY RUN] 模拟部署到生产环境'")
    else:
        c.run("echo '部署到生产环境...'")
        c.run("echo '发送部署通知'")


@task
def rollback(c, version=None):
    """回滚到指定版本。"""
    ver = version or "上一版本"
    c.run(f"echo '回滚到 {ver}'")
```

```python
# tasks/test.py
from invoke import task


@task
def unit(c, coverage=False):
    """运行单元测试。"""
    cmd = "echo '运行单元测试...'"
    if coverage:
        cmd += " && echo '生成覆盖率报告'"
    c.run(cmd)


@task
def integration(c):
    """运行集成测试。"""
    c.run("echo '运行集成测试...'")
    c.run("echo '验证 API 契约'")


@task
def e2e(c, browser="chrome"):
    """运行端到端测试。"""
    c.run(f"echo '在 {browser} 中运行 E2E 测试...'")
```

代码要点：

- `build.py` 中 `@task(default=True)` 将 `all` 标记为 `build` 命名空间的默认任务——直接调用 `inv build` 等价于 `inv build.all`。
- 每个模块只关注自己领域的任务，互不耦合。

## 3. 组装命名空间入口

在 `tasks/__init__.py` 中，使用 `Collection.from_module()` 自动从子模块发现任务并创建子集合，再通过 `add_collection()` 组装到根命名空间：

```python
# tasks/__init__.py
from invoke import Collection

# 使用 Collection.from_module() 从子模块自动构建子集合
from . import build, deploy, test

# 创建根命名空间
ns = Collection()

# 添加子集合——自动从模块发现 @task 标记的函数
ns.add_collection(Collection.from_module(build))
ns.add_collection(Collection.from_module(deploy))
ns.add_collection(Collection.from_module(test))

# 命名空间级配置——所有任务都可以通过 c.config 访问
ns.configure({
    'build': {
        'output_dir': 'dist/',
        'source_map': True,
    },
    'deploy': {
        'staging_host': 'staging.example.com',
        'production_host': 'app.example.com',
    },
    'run': {
        'echo': True,  # 默认回显执行的命令
    },
})
```

## 4. 执行命令

完成上述配置后，Invoke 会自动发现 `tasks/` 包作为任务入口（与 `tasks.py` 等效），可以通过点号（`.`）访问命名空间下的任务：

### 列出所有任务（扁平格式）

```bash
$ inv --list

Available tasks:

  build.all           执行完整构建流程（compile + bundle）。
  build.bundle        打包产物，可选压缩。
  build.compile       编译源代码。
  deploy.production   部署到生产环境。
  deploy.rollback     回滚到指定版本。
  deploy.staging      部署到预发布环境。
  test.e2e            运行端到端测试。
  test.integration    运行集成测试。
  test.unit           运行单元测试。
```

### 嵌套格式查看（更直观）

```bash
$ inv --list --list-format=nested

Available tasks:

  build:
    all         执行完整构建流程（compile + bundle）。
    bundle      打包产物，可选压缩。
    compile     编译源代码。
  deploy:
    production  部署到生产环境。
    rollback    回滚到指定版本。
    staging     部署到预发布环境。
  test:
    e2e         运行端到端测试。
    integration 运行集成测试。
    unit        运行单元测试。
```

### 执行命名空间任务

```bash
# 编译代码
$ inv build.compile
echo '编译 TypeScript → JavaScript'
编译 TypeScript → JavaScript
echo '编译 Cython 扩展'
编译 Cython 扩展

# 打包（带压缩）
$ inv build.bundle --minify
echo '打包应用产物'
打包应用产物
echo '压缩混淆 JavaScript/CSS'
压缩混淆 JavaScript/CSS

# 执行 build 命名空间的默认任务
$ inv build
echo '编译 TypeScript → JavaScript'
编译 TypeScript → JavaScript
echo '编译 Cython 扩展'
编译 Cython 扩展
echo '打包应用产物'
打包应用产物

# 部署到预发布
$ inv deploy.staging
echo '部署到 staging 服务器...'
部署到 staging 服务器...
echo '运行冒烟测试...'
运行冒烟测试...

# 单元测试 + 覆盖率
$ inv test.unit --coverage
echo '运行单元测试...'
运行单元测试...
echo '生成覆盖率报告'
生成覆盖率报告
```

## 5. 深度嵌套命名空间

对于更复杂的项目，可以嵌套多层命名空间。例如在 `db` 子集合下再分 `migrate` 和 `seed`：

```
tasks/
├── __init__.py
├── build.py
├── db/
│   ├── __init__.py
│   ├── migrate.py
│   └── seed.py
├── deploy.py
└── test.py
```

```python
# tasks/db/__init__.py
from invoke import Collection
from . import migrate, seed

ns = Collection()
ns.add_collection(Collection.from_module(migrate))
ns.add_collection(Collection.from_module(seed))
```

```python
# tasks/db/migrate.py
from invoke import task


@task
def up(c, target=None):
    """执行数据库迁移（升级）。"""
    if target:
        c.run(f"echo '迁移到版本 {target}'")
    else:
        c.run("echo '执行所有待执行迁移'")


@task
def down(c, steps=1):
    """回滚数据库迁移。"""
    c.run(f"echo '回滚 {steps} 个迁移'")
```

```python
# tasks/db/seed.py
from invoke import task


@task
def dev(c):
    """填充开发环境种子数据。"""
    c.run("echo '插入开发测试数据'")


@task
def test(c):
    """填充测试环境种子数据。"""
    c.run("echo '插入测试夹具数据'")
```

更新根命名空间入口：

```python
# tasks/__init__.py（更新版）
from invoke import Collection
from . import build, deploy, test, db

ns = Collection()
ns.add_collection(Collection.from_module(build))
ns.add_collection(Collection.from_module(deploy))
ns.add_collection(Collection.from_module(test))
ns.add_collection(Collection.from_module(db))  # db 本身是一个包含子集合的命名空间

ns.configure({
    'build': {'output_dir': 'dist/', 'source_map': True},
    'deploy': {
        'staging_host': 'staging.example.com',
        'production_host': 'app.example.com',
    },
    'run': {'echo': True},
})
```

执行深度嵌套任务：

```bash
# 三级命名空间：db.migrate.up
$ inv db.migrate.up
echo '执行所有待执行迁移'
执行所有待执行迁移

$ inv db.migrate.up --target=005
echo '迁移到版本 005'
迁移到版本 005

$ inv db.seed.dev
echo '插入开发测试数据'
插入开发测试数据
```

## 6. 手动构建 Collection（不使用 from_module）

如果需要更精细地控制哪些任务暴露、如何命名，可以手动添加任务而非依赖自动发现：

```python
# tasks/__init__.py（手动构建版本）
from invoke import Collection
from .build import compile as build_compile, bundle as build_bundle
from .deploy import production as deploy_prod, staging as deploy_staging
from .test import unit as test_unit, integration as test_integration

ns = Collection()

build_ns = Collection('build')
build_ns.add_task(build_compile)
build_ns.add_task(build_bundle)
build_ns.configure({'output_dir': 'dist/'})

deploy_ns = Collection('deploy')
deploy_ns.add_task(deploy_prod, name='prod')  # 重命名：deploy.prod
deploy_ns.add_task(deploy_staging, name='stage')  # 重命名：deploy.stage

test_ns = Collection('test')
test_ns.add_task(test_unit)
test_ns.add_task(test_integration)

ns.add_collection(build_ns)
ns.add_collection(deploy_ns)
ns.add_collection(test_ns)
```

这种方式允许你控制任务在 CLI 中的名称（如将 `production` 暴露为 `deploy.prod`），并精确控制配置范围。

## 相关概念

* [Collection 与命名空间（§4）](../concepts/04-collection-namespace.md)
* [配置系统（§5）](../concepts/05-configuration.md)
* [Task 基础（§2）](../concepts/02-task-basics.md)
* [任务加载机制（§1）](../concepts/01-getting-started.md)

[^pyinvoke-src]: PyInvoke 源码，见本 bundle 信源登记 [references/pyinvoke-source.md](../references/pyinvoke-source.md)。
