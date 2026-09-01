---
type: Example
title: Python API 使用
description: 在 Python 代码中调用 Copier、集成到自动化工具、错误处理、自定义工作流
tags: [copier, python-api, integration, automation, programmatic, example]
generated: { by: "reference_agent/trae-glm", at: "2026-08-22T11:30:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: copier-src
    resource: /references/copier-source.md
    title: "Copier 源码"
---

# Python API 使用

本示例展示如何在 Python 代码中直接调用 Copier 的 API，将其集成到自定义工具、CI/CD 管道或 IDE 插件中。[^copier-src]

## 1. 便捷函数 API

最简单的用法是调用三个便捷函数：`run_copy()`、`run_recopy()`、`run_update()`。

### run_copy：创建项目

```python
from pathlib import Path
from copier import run_copy

# 基本用法：从本地模板创建项目
run_copy(
    src_path="./my-template",
    dst_path="./output/my-project",
)

# 带参数的完整用法
run_copy(
    src_path="gh:myorg/python-template",
    dst_path="./my-project",
    data={
        "project_name": "demo-app",
        "author_name": "Bot",
        "python_version": "3.12",
    },
    vcs_ref="v2.0.0",           # 指定模板版本
    defaults=True,              # 使用默认答案
    overwrite=True,             # 覆盖已有文件
    quiet=False,                # 显示输出
    pretend=False,              # 实际执行
    unsafe=False,               # 不允许不安全特性
    exclude=["*.tmp"],          # 额外排除模式
    skip_if_exists=[".env"],    # 存在时跳过
    cleanup_on_error=True,      # 出错时清理
)
```

### run_update：更新项目

```python
from copier import run_update

# 更新当前目录的项目
run_update(
    dst_path=".",
    defaults=True,
    skip_answered=True,
    conflict="inline",
    context_lines=3,
    unsafe=True,
)

# 更新指定目录
run_update(
    dst_path="./my-project",
    vcs_ref="v3.0.0",          # 更新到特定版本
    overwrite=True,
    defaults=True,
)
```

### run_recopy：重新复制

```python
from copier import run_recopy

# 保留答案，丢弃本地修改
run_recopy(
    dst_path="./my-project",
    defaults=True,
    overwrite=True,
    skip_answered=True,
)
```

### get_update_data：检查更新

```python
from copier._main import get_update_data

available, current, latest = get_update_data(
    dst_path="./my-project",
    use_prereleases=False,
)

if available:
    print(f"可更新：{current} → {latest}")
else:
    print("已是最新版本")
```

## 2. 使用 Worker 类进行精细控制

对于需要更多控制的场景，直接使用 `Worker` 类：

```python
from pathlib import Path
from copier._main import Worker

with Worker(
    src_path="./template",
    dst_path=Path("./output"),
    data={"name": "test"},
    defaults=True,
    overwrite=True,
    quiet=True,
    conflict="inline",
    context_lines=5,
    exclude=["*.log"],
    skip_if_exists=["local_config.yml"],
    use_prereleases=False,
    cleanup_on_error=True,
) as worker:
    # 可以在执行前检查模板信息
    print(f"模板版本: {worker.template.version}")
    print(f"模板提交: {worker.template.commit_hash}")
    print(f"问题列表: {list(worker.template.questions_data.keys())}")

    # 执行复制
    worker.run_copy()
```

### Worker 属性访问

Worker 创建后（进入上下文管理器后），可以访问：

```python
with Worker(src_path="./template", dst_path=Path("./output")) as worker:
    # 模板信息
    print(worker.template.url)           # 模板 URL
    print(worker.template.local_abspath) # 本地克隆路径
    print(worker.template.commit)        # Git describe
    print(worker.template.version)       # PEP440 版本
    print(worker.template.tasks)         # 任务列表
    print(worker.template.exclude)       # 排除模式
    print(worker.template.jinja_extensions)  # Jinja2 扩展

    # 子项目信息
    print(worker.subproject.local_abspath)   # 目标路径
    print(worker.subproject.last_answers)    # 上次答案
    print(worker.subproject.vcs)             # VCS 类型

    # Jinja2 环境
    print(worker.jinja_env)              # SandboxedEnvironment
```

## 3. 错误处理

### 捕获特定异常

```python
from copier import run_copy
from copier.errors import (
    UnsafeTemplateError,
    UserMessageError,
    TaskError,
    ForbiddenPathError,
    CopierAnswersInterrupt,
    ExtensionNotFoundError,
)

try:
    run_copy(
        src_path="gh:user/template",
        dst_path="./output",
        defaults=True,
    )
except UnsafeTemplateError as e:
    print(f"模板使用了不安全特性: {e}")
    print("请使用 --trust 参数确认信任此模板")
except TaskError as e:
    print(f"任务执行失败: {e.cmd}")
    print(f"返回码: {e.returncode}")
    print(f"stdout: {e.output}")
    print(f"stderr: {e.stderr}")
except UserMessageError as e:
    print(f"用户错误: {e.message}")
except ForbiddenPathError as e:
    print(f"路径越界: {e}")
except ExtensionNotFoundError as e:
    print(f"缺少 Jinja2 扩展: {e}")
```

### 处理 Ctrl+C 中断

```python
from copier._main import Worker
from copier.errors import CopierAnswersInterrupt

try:
    with Worker(src_path="./template", dst_path=Path("./output")) as w:
        w.run_copy()
except CopierAnswersInterrupt as e:
    print(f"用户中断于问题: {e.last_question.var_name}")
    print(f"已收集的答案: {e.answers.user}")
    # 可以保存部分答案
    import yaml
    with open("partial-answers.yml", "w") as f:
        yaml.dump(dict(e.answers.user), f)
```

## 4. 构建自定义 CLI 工具

将 Copier 包装为组织专用的项目创建工具：

```python
#!/usr/bin/env python
"""组织项目初始化工具。"""
import typer
from copier import run_copy
from pathlib import Path

app = typer.Typer(help="组织项目初始化工具")

ORG_TEMPLATE = "gh:myorg/python-template"
STABLE_VERSION = "v2.1.0"

@app.command()
def create(
    name: str = typer.Option(..., help="项目名称"),
    output: Path = typer.Option(None, help="输出目录"),
    version: str = typer.Option(STABLE_VERSION, help="模板版本"),
    docker: bool = typer.Option(False, help="包含 Docker 支持"),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="交互模式"),
):
    """从组织模板创建新项目。"""
    dst = output or Path(f"./{name}")

    run_copy(
        src_path=ORG_TEMPLATE,
        dst_path=str(dst),
        vcs_ref=version,
        data={
            "project_name": name,
            "use_docker": docker,
            "org_name": "MyOrg",
        },
        defaults=not interactive,
        overwrite=True,
        unsafe=True,  # 信任组织模板
        quiet=not interactive,
    )

    typer.echo(f"✅ 项目 {name} 创建于 {dst}")
    typer.echo(f"   cd {name} && pip install -e '.[dev]'")

@app.command()
def update(
    path: Path = typer.Option(".", help="项目目录"),
    version: str = typer.Option(None, help="目标版本（默认最新）"),
):
    """更新项目到最新模板版本。"""
    from copier import run_update

    run_update(
        dst_path=str(path),
        vcs_ref=version,
        defaults=True,
        skip_answered=True,
        unsafe=True,
        conflict="inline",
    )
    typer.echo("✅ 项目更新完成")

if __name__ == "__main__":
    app()
```

## 5. CI/CD 集成

### GitHub Actions 中使用

```python
"""CI 中自动更新模板的脚本。"""
import os
import sys
from copier import run_update
from copier._main import get_update_data

def ci_update():
    """在 CI 环境中非交互更新项目。"""
    dst = os.environ.get("GITHUB_WORKSPACE", ".")

    # 检查更新
    available, current, latest = get_update_data(dst)
    if not available:
        print("::notice::Project is already up to date")
        return 0

    print(f"::notice::Updating from {current} to {latest}")

    try:
        run_update(
            dst_path=dst,
            defaults=True,
            skip_answered=True,
            overwrite=True,
            unsafe=True,
            quiet=True,
            conflict="rej",  # CI 中使用 rej 文件便于审查
        )
        print(f"::notice::Updated to {latest}")
        return 0
    except Exception as e:
        print(f"::error::Update failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(ci_update())
```

## 6. 批量生成多个项目

```python
"""从同一模板批量生成多个项目。"""
from copier import run_copy
from pathlib import Path

projects = [
    {"name": "service-a", "port": 8001, "type": "api"},
    {"name": "service-b", "port": 8002, "type": "api"},
    {"name": "worker", "port": 0, "type": "worker"},
    {"name": "frontend", "port": 3000, "type": "web"},
]

template = "gh:myorg/microservice-template"

for p in projects:
    dst = Path(f"./services/{p['name']}")
    print(f"Generating {p['name']}...")
    run_copy(
        src_path=template,
        dst_path=str(dst),
        data={
            "service_name": p["name"],
            "service_port": str(p["port"]),
            "service_type": p["type"],
        },
        defaults=True,
        overwrite=True,
        quiet=True,
        unsafe=True,
        vcs_ref="stable",
    )
    print(f"  → {dst}")
```

## 7. 与 VcsRef 枚举配合使用

```python
from copier import run_update, VcsRef

# 使用 :current: 特殊值（保持当前版本，不升级）
run_update(
    dst_path=".",
    vcs_ref=VcsRef.CURRENT,  # 特殊值 ":current:"
    defaults=True,
    overwrite=True,
)
```

## 8. 使用 Phase 枚举追踪阶段

```python
from copier import Phase

# 在自定义代码中追踪渲染阶段
with Phase.use(Phase.RENDER):
    print(f"Current phase: {Phase.current()}")  # Phase.RENDER
```

Phase 可用于自定义 Jinja2 扩展中判断当前上下文，或在任务脚本中通过环境变量 `COPIER_PHASE` 访问。

## 相关概念

* [Worker 与生命周期](../concepts/05-worker-and-lifecycle.md)
* [CLI 命令参考](../concepts/08-cli-reference.md)
* [高级模式与 API 集成](../concepts/10-advanced-patterns.md)
* [安全与信任机制](../concepts/09-security-and-safety.md)
* [错误体系](../concepts/10-advanced-patterns.md#错误处理)

[^copier-src]: Copier 源码，见本 bundle 信源登记 [references/copier-source.md](../references/copier-source.md)。
