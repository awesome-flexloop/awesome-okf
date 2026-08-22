---
type: Concept
title: 快速开始
description: 从零安装 Cookiecutter、生成第一个 Jupyter Server 扩展项目、开发安装、测试运行的完整步骤。
tags: [getting-started, quickstart, installation, setup]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T13:10:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T13:10:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: readme
    resource: /references/cookiecutter-json.md
    title: cookiecutter.json 参数全参考
---

## 前置条件

- Python 3.8 或更高版本
- pip 包管理器
- 网络连接（首次使用时 Cookiecutter 需要从 GitHub 下载模板）

## 第一步：安装 Cookiecutter

```bash
pip install cookiecutter
```

Cookiecutter 是一个跨语言的项目模板引擎，通过 `pip install cookiecutter` 一行命令即可安装。

## 第二步：生成项目

在你希望创建项目的目录下执行：

```bash
cookiecutter https://github.com/jupyter-server/extension-cookiecutter
```

Cookiecutter 会下载模板并逐一向你提问：

```
author_name [My Name]: Your Name
author_email [me@me.com]: you@example.com
package_name [my_server_extension]: my_extension
project_short_description [A Jupyter Server extension.]: My first Jupyter Server extension.
has_binder [n]: n
repository [https://github.com/github_username/my_server_extension]: https://github.com/yourname/my_extension
```

每个参数方括号中显示的是默认值，直接按 Enter 接受默认值，或输入自定义值。

参数说明：

| 参数 | 说明 | 示例 |
|------|------|------|
| `author_name` | 你的姓名或组织名 | `Jane Developer` |
| `author_email` | 你的邮箱 | `jane@example.com` |
| `package_name` | Python 包名（可用下划线或连字符） | `my_extension` |
| `project_short_description` | 一句话描述项目 | `A cool Jupyter extension.` |
| `has_binder` | 是否包含 Binder 配置（y/n） | `n` |
| `repository` | 项目仓库 URL | `https://github.com/yourname/my_extension` |

执行完成后，当前目录下会生成一个以 `package_name` 命名的新目录。

## 第三步：开发模式安装

进入生成的项目目录，以可编辑模式安装：

```bash
cd my_extension
pip install -e ".[test]"
```

- `-e`（editable）：可编辑模式，修改源码后无需重新安装
- `".[test]"`：同时安装测试依赖（pytest + pytest-jupyter）

安装成功后，Jupyter Server 会自动发现并启用扩展。可以通过以下命令验证：

```bash
jupyter server extension list
```

输出中应该包含你的扩展，状态显示为 OK：

```
Config dir: ...
...
my_extension  enabled
- Validating...
  my_extension  OK
```

如果显示 `disabled`，可以手动启用：

```bash
jupyter server extension enable my_extension
```

## 第四步：运行测试

模板预置了一个测试用例，验证 `/ping` 端点正常工作：

```bash
pytest
```

预期输出：

```
============================= test session starts ==============================
collected 1 item

my_extension/tests/test_handlers.py .                                   [100%]

============================== 1 passed in Xs ===============================
```

## 第五步：启动 Jupyter Server 试玩

启动 Jupyter Server：

```bash
jupyter server --autoreload
```

`--autoreload` 参数启用自动重载模式，修改 Python 代码后 Jupyter Server 会自动重新加载扩展，无需手动重启。

服务器启动后，在另一个终端中测试 API 端点（需要替换 token）：

```bash
# 从服务器启动日志中复制 token
TOKEN="your-server-token"

curl http://localhost:8888/my-extension/ping?token=$TOKEN
```

或者在浏览器中访问 Jupyter Server 的 API 文档页面（通常是 `http://localhost:8888/api`），或通过 JupyterLab 打开。

预期响应：

```json
{"ping_response": "pong"}
```

## 第六步：开始开发

现在你可以开始修改模板代码来实现自己的扩展了。最常见的修改点：

1. **修改或添加 API 端点**：编辑 `handlers.py` 添加新的 Handler 类
2. **注册新路由**：在 `extension.py` 的 `handlers` 列表中添加 URL 映射
3. **添加配置项**：在 `extension.py` 中定义新的 traitlets 配置属性
4. **添加测试**：在 `tests/` 目录下添加新的测试文件

## 卸载扩展

```bash
pip uninstall my_extension
```

## 常见问题

### 扩展安装后不显示？

检查扩展是否被正确发现：
```bash
jupyter server extension list
```
如果没有列出，检查 pyproject.toml 中的 `shared-data` 配置是否正确安装了 jupyter-config 文件。

### 测试报错 "jp_fetch not found"？

确保安装了测试依赖：
```bash
pip install -e ".[test]"
```
这会安装 `pytest-jupyter[server]`，提供 `jp_fetch` fixture。

### 修改代码后 API 不更新？

如果没有使用 `--autoreload` 模式，需要重启 Jupyter Server 才能加载代码更改。开发时建议始终使用 `jupyter server --autoreload`。

## 相关概念

- [Cookiecutter 模板引擎基础](/concepts/02-cookiecutter-basics.md)
- [项目结构详解](/concepts/03-project-structure.md)
- [ExtensionApp 开发](/concepts/04-extension-app.md)
