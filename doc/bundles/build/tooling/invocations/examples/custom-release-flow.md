---
type: Example
title: 自定义发布流程
description: 基于 packaging.release 模块自定义发布流程，添加前置检查、自定义构建步骤和发布后通知
tags: [invocations, example, release, packaging, custom-workflow]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T14:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T16:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: invocations-source
    resource: /references/invocations-source.md
---

# 自定义发布流程

本示例展示如何基于 `packaging.release` 模块自定义发布流程，在标准流程基础上添加额外步骤。

## 场景

标准发布流程（prepare → publish → push）满足基本需求，但你的项目可能需要：
- 发布前自动运行测试和 lint
- 构建额外的产物（如 Docker 镜像、文档 PDF）
- 发布后发送通知（Slack/邮件）
- 自定义 changelog 格式
- 多包发布（monorepo）

## 自定义发布任务

```python
from invoke import task, Collection
from invocations.packaging import release
from invocations.console import confirm
from invocations.pytest import test as pytest_test
from invocations.checks import blacken, lint

@task
def pre_release_checks(c):
    """发布前检查：确保代码质量过关"""
    print("=== 运行代码格式化检查 ===")
    blacken(c, check=True)
    print("=== 运行 Lint ===")
    lint(c)
    print("=== 运行测试 ===")
    pytest_test(c)
    print("=== 所有前置检查通过 ===")

@task
def build_docker(c, tag=None):
    """构建 Docker 镜像"""
    if tag is None:
        from semantic_version import Version
        pyproject = Path("pyproject.toml")
        import tomllib
        with open(pyproject, "rb") as f:
            data = tomllib.load(f)
        tag = data["project"]["version"]
    c.run(f"docker build -t myproject:{tag} .")
    c.run(f"docker tag myproject:{tag} myproject:latest")

@task
def notify(c, message):
    """发送通知（示例）"""
    # 这里可以集成 Slack、邮件、钉钉等通知
    print(f"[NOTIFY] {message}")

@task
def release_custom(c, dry_run=False, skip_tests=False, docker=False):
    """自定义发布流程：前置检查 → 标准发布 → Docker → 通知"""
    # 1. 前置检查
    if not skip_tests:
        pre_release_checks(c)
    
    # 2. 确认发布
    actions, state = release.status(c)
    if not actions.all_okay:
        if not confirm("发布状态存在未完成项，是否继续 prepare?"):
            raise Exit("已取消发布")
        release.prepare(c, dry_run=dry_run)
    
    # 3. 发布到 PyPI
    release.publish(c, dry_run=dry_run)
    
    # 4. 推送 Git
    release.push(c, dry_run=dry_run)
    
    # 5. 额外步骤：构建 Docker
    if docker:
        build_docker(c)
        if not dry_run:
            c.run("docker push myproject:latest")
    
    # 6. 通知
    version = state.expected_version
    notify(c, f"myproject v{version} 发布成功!")
    print(f"\n🎉 版本 {version} 发布完成!")

ns = Collection(release_custom, pre_release_checks, build_docker, release)
ns.configure({
    "packaging": {
        "wheel": True,
        "changelog_file": "CHANGELOG.rst",
        "package": "myproject",
    },
})
```

## 使用

```bash
# 干跑自定义发布流程
inv release-custom --dry-run

# 完整发布（含测试和 Docker）
inv release-custom --docker

# 跳过测试快速发布（紧急修复）
inv release-custom --skip-tests
```

## 关键模式

### 调用 release 子任务

release 模块的任务是普通 Python 函数，可以直接在自定义任务中调用：

```python
from invocations.packaging.release import status, prepare, publish, push

actions, state = status(c)  # 获取状态
prepare(c, dry_run=True)     # 准备
publish(c, dry_run=True)     # 构建+上传
push(c, dry_run=True)        # 推送
```

注意 `status()` 返回 `(actions, state)` 二元组，其中包含所有状态信息，可以用于条件判断和通知消息。

### 使用 dry_run 参数

所有修改性任务都支持 `dry_run` 参数，在自定义流程中应传递这个参数：

```python
release.prepare(c, dry_run=dry_run)
release.publish(c, dry_run=dry_run)
release.push(c, dry_run=dry_run)
```

### 交互式确认

使用 `console.confirm()` 在关键步骤前请求确认，避免误操作。

## 相关概念

- [包发布生命周期](../concepts/05-packaging-release.md)
- [终端交互工具](../concepts/07-utilities-watchers.md)
- [组合模式：组装自己的任务集合](../concepts/10-composition-patterns.md)

[^invocations-source]: Invocations 源码信源，见 [invocations-source.md](../references/invocations-source.md)。
