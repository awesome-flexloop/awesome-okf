---
type: Concept
title: CI 环境自动化
description: 使用 ci 模块在持续集成环境中创建 sudo 用户、执行特权命令、设置 SSH 免密登录
tags: [invocations, ci, continuous-integration, sudo, ssh, circleci]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T14:00:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-24" }
status: stable
stale_after: 2027-12-31
sources:
  - id: invocations-source
    resource: /references/invocations-source.md
---

# CI 环境自动化

`invocations.ci` 模块提供持续集成（CI）环境下的辅助任务，主要解决 CI 中测试 sudo 相关功能的问题。

## 为什么需要这个模块

大多数 CI 环境（如 CircleCI）的默认用户拥有**无密码 sudo**权限。这导致：
- 测试需要密码输入的 sudo 功能时会产生假阳性（false-positive）
- 无法测试真实的 sudo 密码提示流程

ci 模块的解决方案是：**创建一个需要密码才能 sudo 的专用测试用户**，然后以此用户身份运行测试套件。

## 快速使用

```python
# tasks.py
from invoke import Collection
from invocations.ci import ns as ci_ns

ns = Collection(ci_ns)
# 可覆盖默认配置
ns.configure({
    "ci": {
        "sudo": {
            "user": "testuser",
            "password": "mypassword",
            "groups": ["sudo", "docker"],
        }
    }
})
```

## 核心任务

### make_sudouser：创建 sudo 测试用户

```bash
inv make-sudouser
```

该任务：
1. 使用默认 CI 用户的无密码 sudo 权限执行 `useradd` 创建新用户
2. 通过 `--create-home` 创建用户主目录（放置配置文件、密钥等）
3. 通过 `--groups` 将用户加入 sudo 组（默认 `["sudo", "circleci"]`）
4. 使用 `chpasswd` 非交互式设置用户密码

执行后，新用户拥有需要密码的 sudo 权限，可以真实测试 sudo 密码提示场景。

### sudo_run：以 sudo 用户执行命令

```bash
# 以测试用户身份运行命令
inv sudo-run --command="inv coverage"
inv sudo-run --command="inv integration"
```

`sudo_run` 使用 `sudo su <user> -c "export PATH=$PATH && <command>"` 模式切换用户执行命令。

> **实现细节**：由于 CircleCI 的 sudoers 配置，`sudo -u` 会要求输入密码，而 `sudo su` 可以绕过。但 `su` 会重置 PATH，所以需要显式 `export PATH=$PATH` 来保留环境变量。

### make_sshable：设置 SSH 免密登录

```bash
inv make-sshable
```

该任务配置 localhost 的 SSH 免密登录：
1. 创建 `~/.ssh` 目录并设置权限 0700
2. 生成 RSA 密钥对（无密码短语）
3. 将公钥添加到 `authorized_keys`

用于测试 SSH 相关功能（如远程执行、文件传输等）。任务内部通过 `sudo_run` 以测试用户身份执行操作。

## 默认配置

```python
ns.configure({
    "ci": {
        "sudo": {
            "user": "invoker",          # 测试用户名
            "password": "secret",        # sudo 密码
            "groups": ["sudo", "circleci"],  # 用户组
        }
    }
})
```

## 典型 CI 工作流

```python
from invoke import task, Collection
from invocations.ci import make_sudouser, sudo_run, make_sshable
from invocations.pytest import test, integration, coverage

@task
def setup_ci(c):
    """CI 环境准备"""
    make_sudouser(c)
    make_sshable(c)

@task
def ci_test(c):
    """CI 中以测试用户运行测试"""
    sudo_run(c, "inv test")

@task
def ci_coverage(c):
    """CI 中以测试用户运行覆盖率"""
    sudo_run(c, "inv coverage")

ns = Collection(setup_ci, ci_test, ci_coverage, test, coverage)
```

对应的 CircleCI 配置示例：

```yaml
# .circleci/config.yml
version: 2.1
jobs:
  test:
    docker:
      - image: cimg/python:3.12
    steps:
      - checkout
      - run: pip install -e '.[dev]'
      - run: inv setup-ci
      - run: inv ci-test
      - run: inv ci-coverage
```

## environment.in_ci()：CI 环境检测

`invocations.environment` 模块提供 `in_ci()` 工具函数：

```python
from invocations.environment import in_ci

if in_ci():
    print("在 CI 环境中")
else:
    print("在本地环境中")
```

`in_ci()` 检查以下环境变量是否存在且非空：
- `CIRCLECI`（CircleCI）
- `TRAVIS`（Travis CI）

可在自定义任务中用于区分本地和 CI 行为。

## 注意事项

- ci 模块主要面向 CircleCI 设计，但可以通过配置 `ci.sudo.groups` 适配其他 CI 环境（如使用 `wheel` 组而非 `sudo` 组的系统）
- 默认密码 `"secret"` 仅用于测试，**不要在生产环境中使用**
- `make_sshable` 生成的密钥无密码短语，仅适合 CI 测试环境
- `sudo_run` 的 PATH 保留方式是 workaround，某些环境可能需要额外配置
- 如果你的 CI 不是 CircleCI，可能需要调整 groups 配置

## 相关概念

- [Pytest 测试任务](03-testing-pytest.md)
- [工具函数与文件监控](07-utilities-watchers.md)
- [组合模式：组装自己的任务集合](10-composition-patterns.md)

[^invocations-source]: Invocations 源码信源，见 [invocations-source.md](../references/invocations-source.md)。
