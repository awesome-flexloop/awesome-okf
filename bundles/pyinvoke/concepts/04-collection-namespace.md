---
type: Concept
title: Collection 与命名空间
description: 使用 Collection 组织任务、模块化大型项目、ns.configure() 配置、嵌套集合、from_module 自动加载
tags: [pyinvoke, collection, namespace, ns, from_module, modular]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: pyinvoke-source
    resource: /references/pyinvoke-source.md
---

# Collection 与命名空间

当项目的任务数量增长到一定规模时，把所有任务都堆在一个 `tasks.py` 文件中会变得难以维护。**Collection**（集合）是 Invoke 提供的任务组织机制，支持命名空间（namespace）嵌套、模块化拆分和层级配置。

## 为什么需要 Collection

- **模块化**：将相关任务分组到不同模块/文件中
- **命名空间**：避免任务名冲突，通过点号访问（如 `db.migrate`、`db.backup`）
- **层级配置**：不同命名空间可以有各自的配置
- **自动发现**：从模块自动构建任务集合

## 隐式命名空间（默认行为）

在最简单的场景中，你不需要显式创建 Collection。Invoke 会自动从 `tasks.py` 模块中发现所有被 `@task` 标记的函数，并构建一个默认的 Collection：

```python
# tasks.py
from invoke import task

@task
def build(c):
    c.run("echo building")

@task
def test(c):
    c.run("echo testing")
```

```bash
$ inv --list
Available tasks:

  build
  test
```

这等价于手动创建了一个匿名 Collection 并添加了所有任务。

## 显式命名空间：ns = Collection()

当需要更精细的控制（如添加子集合、设置配置、指定默认任务）时，创建一个名为 `ns` 或 `namespace` 的 Collection 对象。Invoke 会自动检测到它并优先使用，而不是自动扫描任务。

```python
from invoke import Collection, task

@task
def build(c):
    c.run("echo building")

@task
def test(c):
    c.run("echo testing")

ns = Collection(build, test)
```

### 构造函数的多种用法

Collection 构造函数非常灵活，支持多种初始化方式：

**方式 1：先创建再添加**

```python
ns = Collection()
ns.add_task(build)
ns.add_task(test)
```

**方式 2：位置参数传入 Task/Collection**

```python
ns = Collection(build, test)
```

**方式 3：关键字参数指定名称**

```python
ns = Collection(
    build_task=build,  # CLI 名称为 "build-task"
    run_tests=test,    # CLI 名称为 "run-tests"
)
```

**方式 4：指定集合名称（用于子集合）**

```python
docs = Collection('docs')  # 集合名为 "docs"
docs.add_task(build_docs)
```

第一个位置参数如果是字符串，会作为集合的名称。

## add_task() —— 添加任务

`add_task(task, name=None, aliases=None, default=None)` 向集合中添加任务：

```python
from invoke import Collection, task

@task
def build(c):
    """构建项目。"""
    pass

@task(name="compile")
def build_project(c):
    """编译项目。"""
    pass

ns = Collection()
ns.add_task(build)                          # 使用任务自身名称 "build"
ns.add_task(build_project, name="b")        # 覆盖名称为 "b"
ns.add_task(build, aliases=("bld", "bu"))   # 额外添加别名
ns.add_task(build, default=True)            # 设为默认任务
```

参数说明：

| 参数 | 说明 |
|------|------|
| `task` | Task 对象（被 `@task` 装饰的函数） |
| `name` | 绑定的名称，覆盖任务自身的 `name` 属性 |
| `aliases` | 额外的别名元组，追加到任务自身别名之后 |
| `default` | 是否设为集合的默认任务 |

如果添加的名称与已存在的子集合冲突，会抛出 `ValueError`。

## add_collection() —— 添加子集合

`add_collection(coll, name=None, default=None)` 添加子集合，实现命名空间嵌套：

```python
from invoke import Collection, task

# 数据库相关任务
@task
def migrate(c):
    c.run("alembic upgrade head")

@task
def backup(c):
    c.run("pg_dump mydb > backup.sql")

db = Collection('db')
db.add_task(migrate)
db.add_task(backup)

# 文档相关任务
@task
def build(c):
    c.run("sphinx-build docs dist/docs")

docs = Collection('docs')
docs.add_task(build)

# 顶级命名空间
ns = Collection()
ns.add_collection(db)
ns.add_collection(docs)
```

命令行调用：

```bash
inv --list
# Available tasks:
#   db.backup
#   db.migrate
#   docs.build

inv db.migrate
inv db.backup
inv docs.build
```

### add_collection 也接受模块

`add_collection` 可以直接接受 Python 模块对象，内部自动调用 `Collection.from_module()`：

```python
import db_tasks
import docs_tasks

ns = Collection()
ns.add_collection(db_tasks, name="db")
ns.add_collection(docs_tasks, name="docs")
```

### 默认子集合

将子集合设为默认后，可以通过集合名直接调用其默认任务：

```python
ns.add_collection(db, default=True)
# inv db         # 执行 db 的默认任务
```

## Collection.from_module() —— 从模块自动加载

`Collection.from_module(module, name=None, config=None, loaded_from=None, auto_dash_names=None)` 是一个类方法，从 Python 模块自动构建 Collection。这是 Invoke 内部加载 `tasks.py` 时使用的机制。

```python
# tasks/db.py
from invoke import task, Collection

@task
def migrate(c):
    c.run("alembic upgrade head")

@task
def rollback(c):
    c.run("alembic downgrade -1")

# 可以有自己的 ns
ns = Collection(migrate, rollback)
ns.configure({"db": {"url": "postgresql://localhost/mydb"}})
```

```python
# tasks.py
from invoke import Collection
from tasks import db, docs, deploy

ns = Collection.from_module(db)  # 单模块
# 或更常见的是：
ns = Collection()
ns.add_collection(db)
ns.add_collection(docs)
ns.add_collection(deploy)
```

`from_module()` 的行为：

1. 检查模块中是否有名为 `ns` 或 `namespace` 的 Collection 对象
   - 如果有，复制该集合（包含其任务、子集合、配置）
   - 如果没有，自动扫描模块中的所有 Task 对象构建新集合
2. 集合名称默认为模块文件名（如 `db.py` → `"db"`）
3. 模块的 docstring（`__doc__`）会被复制为集合的帮助文本
4. `config` 参数会合并到集合配置之上（覆盖冲突项）

## configure() —— 集合级配置

`configure(options)` 将配置字典合并到集合中，该集合及其子集合中的所有任务都可以访问这些配置。

```python
from invoke import Collection, task

@task
def greet(c):
    print(f"Hello, {c.name}!")

ns = Collection(greet)
ns.configure({"name": "World"})
```

配置会按层级合并——访问子集合中的任务时，父集合的配置会向下合并：

```python
db = Collection('db')
db.configure({"db": {"host": "localhost", "port": 5432}})

ns = Collection()
ns.configure({"run": {"echo": True}})  # 全局配置
ns.add_collection(db)
# 在 db.migrate 中，c.config 包含 run.echo=True 和 db.host="localhost"
```

`configuration(taskpath=None)` 方法返回合并后的配置字典：

```python
config = ns.configuration()              # 集合自身配置
config = ns.configuration("db.migrate")  # 包含子集合层级合并后的配置
```

建议使用唯一的嵌套键名（如 `myapp.sphinx.target` 而非 `target`），以避免与 Invoke 内置配置或其他集合的配置冲突。

## 嵌套集合与点号访问

子集合中的任务通过**点号（`.`）**访问：

```python
ns = Collection()
ns.add_collection(db, name="db")
# 调用方式：inv db.migrate
```

深层嵌套同样支持：

```python
db = Collection('db')
schema = Collection('schema')
schema.add_task(create)  # db.schema.create
db.add_collection(schema)
ns.add_collection(db)
# 调用方式：inv db.schema.create
```

在代码中访问任务：

```python
task = ns["db.migrate"]             # 通过点号路径获取 Task 对象
task, config = ns.task_with_config("db.migrate")  # 同时获取合并后的配置
subcoll = ns.subcollection_from_path("db.schema")  # 获取子集合
```

## task_names 属性

`task_names` 属性返回扁平化的任务名字典，键是主名称，值是别名列表：

```python
print(ns.task_names)
# {
#   'build': ['b'],
#   'db.migrate': [],
#   'db.backup': [],
#   'docs.build': ['docs']  # 默认任务的别名包含集合名
# }
```

这会将整个命名空间树展开为一层，适合用于生成任务列表（如 `inv --list` 输出）。如果子集合有默认任务，集合名本身也会作为该任务的别名出现。

## to_contexts() —— 转换为解析器上下文

`to_contexts(ignore_unknown_help=None)` 将集合中的所有任务转换为 `ParserContext` 对象列表，供 CLI 解析器使用。每个 ParserContext 包含任务名、别名和参数定义。

```python
contexts = ns.to_contexts()
# 返回 List[ParserContext]，用于构建命令行解析器
```

## transform() —— 下划线与短横线转换

`transform(name)` 方法根据 `auto_dash_names` 设置转换名称中的下划线/短横线：

- `auto_dash_names=True`（默认）：将非首尾下划线转为短横线（`run_tests` → `run-tests`）
- `auto_dash_names=False`：将短横线转为下划线

```python
ns = Collection()
print(ns.transform("run_tests"))  # "run-tests"

ns2 = Collection(auto_dash_names=False)
print(ns2.transform("run-tests"))  # "run_tests"
```

此转换会自动应用于任务名、别名和子集合名。首尾的下划线不会被转换（如 `_private_task` 保持不变）。

## 模块化大型项目示例

以下是一个典型的大型项目结构：

```
myproject/
├── tasks/
│   ├── __init__.py    # 主入口，组合所有子模块
│   ├── db.py          # 数据库相关任务
│   ├── docker.py      # Docker 相关任务
│   ├── docs.py        # 文档构建任务
│   └── test.py        # 测试相关任务
└── invoke.yaml        # 项目级配置
```

**tasks/\_\_init\_\_.py：**

```python
from invoke import Collection
from . import db, docker, docs, test

ns = Collection()
ns.add_collection(db)
ns.add_collection(docker)
ns.add_collection(docs)
ns.add_collection(test)

ns.configure({
    "project": {
        "name": "myproject",
        "version": "1.0.0",
    },
    "run": {
        "echo": True,
    },
})
```

**tasks/db.py：**

```python
from invoke import task, Collection

@task
def migrate(c, revision="head"):
    """执行数据库迁移。"""
    c.run(f"alembic upgrade {revision}")

@task
def rollback(c):
    """回滚一次迁移。"""
    c.run("alembic downgrade -1")

@task
def reset(c):
    """重置数据库（危险！）。"""
    c.run("dropdb myproject", warn=True)
    c.run("createdb myproject")
    migrate(c)

ns = Collection()
ns.add_task(migrate)
ns.add_task(rollback)
ns.add_task(reset)
ns.configure({"db": {"name": "myproject"}})
```

命令行使用：

```bash
inv --list              # 列出所有任务
inv db.migrate          # 执行数据库迁移
inv db.migrate --revision=abc123  # 指定版本
inv db.reset            # 重置数据库
inv docker.build        # 构建 Docker 镜像
inv test.unit           # 运行单元测试
```

## auto_dash_names 配置

Collection 的 `auto_dash_names` 参数控制是否自动将下划线转换为短横线：

- 默认 `True`：Python 中的 `run_tests` 映射为 CLI 中的 `run-tests`
- 设为 `False`：保持下划线不变，CLI 中使用 `run_tests`

可以在构造时传入，也可通过配置项 `tasks.auto_dash_names` 全局控制：

```python
ns = Collection(auto_dash_names=False)
```

或在 `invoke.yaml` 中：

```yaml
tasks:
  auto_dash_names: false
```

## serialized() 方法

`serialized()` 返回适合 JSON 序列化的字典表示，用于 `inv --list --format=json` 等场景：

```python
data = ns.serialized()
# {
#   "name": "root",
#   "help": "...",
#   "default": null,
#   "tasks": [...],
#   "collections": [...]
# }
```

## 相关概念

- [Task 基础](/concepts/02-task-basics.md)
- [Context 对象](/concepts/03-context-object.md)
- [5分钟快速上手](/concepts/01-getting-started.md)
- [PyInvoke 简介](/concepts/00-introduction.md)
- [PyInvoke 源码信源登记](/references/pyinvoke-source.md)

[^pyinvoke-source]: PyInvoke 源码信源，见 [pyinvoke-source.md](/references/pyinvoke-source.md)；Collection 类定义于 `invoke/collection.py`。
