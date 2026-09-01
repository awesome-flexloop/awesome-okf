---
type: Reference
title: "测试源码解析"
description: "tests/test_nbviewer.py冒烟测试：BeautifulSoup解析首页、参数化链接检查、无重试助手、无conftest.py"
tags: [nbviewer, deploy, testing, pytest, beautifulsoup, smoke-test]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T12:00:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: test-file
    resource: "../../../../../external/libs/jupyter/nbviewer.org-deploy/tests/test_nbviewer.py"
    title: "tests/test_nbviewer.py"
  - id: pyproject
    resource: "../../../../../external/libs/jupyter/nbviewer.org-deploy/pyproject.toml"
    title: "pyproject.toml"
---

# 测试源码解析

本信源登记 nbviewer.org-deploy 项目的测试结构和内容。

## 测试文件结构

**重要事实**：`tests/` 目录下**只有一个测试文件**，不存在其他测试文件。

```
tests/
└── test_nbviewer.py    # 唯一的测试文件
```

**不存在的文件**：
- ❌ `tests/conftest.py`
- ❌ `tests/test_app.py`
- ❌ `tests/test_statuspage.py`
- ❌ 任何重试助手（retry helper）或指数退避工具

## pytest 配置

来自 `pyproject.toml`：

```toml
[tool.pytest.ini_options]
addopts = "-v"
testpaths = ["tests"]
```

| 配置项 | 值 | 说明 |
|--------|---|------|
| `addopts` | `"-v"` | 详细输出模式 |
| `testpaths` | `["tests"]` | 测试搜索目录 |

## test_nbviewer.py 完整源码

```python
import pytest
import requests
from bs4 import BeautifulSoup

NBVIEWER = "https://nbviewer.org"

frontpage_request = requests.get(NBVIEWER)
frontpage = BeautifulSoup(frontpage_request.text, "html.parser")
frontpage_links = frontpage.find_all("a", class_="thumbnail")
frontpage_urls = [a["href"] for a in frontpage_links]


def test_main_page():
    frontpage_request.raise_for_status()
    assert frontpage_request.status_code == 200
    assert len(frontpage_urls) > 5


@pytest.mark.parametrize("path", frontpage_urls)
def test_front_page(path):
    url = f"{NBVIEWER}{path}"
    r = requests.get(url)
    assert r.status_code == 200
```

## 测试逻辑详解

### 模块级执行（导入时执行）

测试文件在**模块导入时**就执行HTTP请求和HTML解析：

```python
frontpage_request = requests.get(NBVIEWER)                              # 请求首页
frontpage = BeautifulSoup(frontpage_request.text, "html.parser")        # 解析HTML
frontpage_links = frontpage.find_all("a", class_="thumbnail")           # 找所有缩略图链接
frontpage_urls = [a["href"] for a in frontpage_links]                   # 提取href属性
```

这意味着：
1. 测试收集阶段就会请求 nbviewer.org 首页
2. 如果首页不可达，pytest 在收集阶段就会失败
3. 首页缩略图链接的数量和目标**动态变化**（基于线上实际内容）
4. `frontpage_request` 和 `frontpage_urls` 是模块级变量，所有测试函数共享

### test_main_page

验证首页基本可用性：

| 断言 | 说明 |
|------|------|
| `frontpage_request.raise_for_status()` | HTTP请求未返回错误状态码 |
| `assert frontpage_request.status_code == 200` | 首页返回200 |
| `assert len(frontpage_urls) > 5` | 首页至少有5个以上示例notebook链接 |

### test_front_page（参数化）

使用 `@pytest.mark.parametrize` 对首页的每个缩略图链接进行测试：

1. 拼接完整URL：`f"{NBVIEWER}{path}"`
2. 发送GET请求
3. 断言返回状态码200

**注意**：
- 没有重试逻辑（no retry with exponential backoff）
- 没有超时设置
- 没有fixture（conftest.py不存在）
- 参数化数据在导入时确定，不会在每个测试函数中重新请求首页

## 测试依赖

测试需要以下Python包：

| 包 | 用途 |
|---|------|
| `pytest` | 测试框架 |
| `requests` | HTTP客户端 |
| `beautifulsoup4` | HTML解析 |

这些包都在 `requirements.in`/`requirements.txt` 中。

## CI中的执行

在 GitHub Actions `cd.yml` 工作流中，测试在部署完成后执行：

```yaml
- name: test
  run: |
    pytest
```

即：部署脚本执行成功后，对**线上** nbviewer.org 运行冒烟测试，验证部署后的服务可用性。

## 测试特点总结

| 特点 | 实际情况 |
|------|---------|
| 测试类型 | 冒烟测试（smoke test），验证线上服务可用性 |
| 测试目标 | https://nbviewer.org（生产环境） |
| 测试文件数量 | 1个（test_nbviewer.py） |
| 测试函数数量 | 2个（test_main_page + 参数化的test_front_page） |
| 参数化 | 是，基于首页动态链接 |
| HTML解析 | BeautifulSoup，查找 `a.thumbnail` 元素 |
| 重试机制 | ❌ 无 |
| conftest.py | ❌ 不存在 |
| Fixtures | ❌ 不使用pytest fixture |
| 本地测试 | 可以，`pytest tests/` |
| 网络依赖 | 必须能访问 nbviewer.org |

## 相关信源

- [CI/CD工作流源码](cicd-source.md)
- [测试与密钥管理](../concepts/08-testing-and-secrets.md)
