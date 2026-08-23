---
type: Example
title: "自定义 TOML 配置"
description: "为复杂 Python 包编写 TOML 配置，包括子模块、排除项、RST 指令处理器、叙述文档和 Logo 设置"
tags: [config, toml, directives, submodules, exclude, advanced]
generated: { by: "reference_agent/trae-soLO", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: config-src
    resource: "/references/config-source.md"
    title: "Papyri 配置系统源码信源"
  - id: papyri-src
    resource: "/references/papyri-source.md"
    title: "Papyri Python 核心包源码信源"
---

# 自定义 TOML 配置

本示例演示如何为复杂的 Python 包编写完整的 TOML 配置文件。

## 示例1：完整配置文件

以下是一个典型的科学计算库配置模板（基于 numpy.toml 模式）：

```toml
[meta]
github_slug = 'your-org/your-package'
tag = '{{version}}'
pypi = 'your-package'

[global]
module = 'your_package'

# 需要额外分析的子模块
submodules = [
    'your_package.submodule_a',
    'your_package.submodule_b',
]

# 排除不需要文档化的限定名
exclude = [
    'your_package:internal_helper',
    'your_package:_private_func',
    'your_package.submodule_a:debug_util',
]

# 是否执行 doctest 代码示例
execute_doctests = true
exec_failure = 'raise'  # 'raise' 或 'ignore'

# Logo 路径（相对于配置文件或绝对路径）
logo = "../docs/_static/logo.png"

# 叙述文档目录（RST 文件）
docs_path = "~/projects/your-package/docs/"

# 示例文件目录
examples_folder = '~/projects/your-package/examples/'
```

## 示例2：注册 RST 指令处理器

当目标包的 docstring 使用了非标准 RST 指令时，必须注册处理器。否则序列化时会报错。

```toml
[global]
module = 'your_package'

[global.directives]
# 丢弃测试设置指令（不影响文档语义）
testsetup = 'papyri.directives:drop'
testcleanup = 'papyri.directives:drop'

# 将 IPython 代码块保留为代码
ipython = 'papyri.directives:code_handler'

# 自定义指令处理器
# 格式：指令名 = '模块路径:处理函数'
plot = 'your_package._papyri_directives:plot_handler'
versionadded = 'your_package._papyri_directives:version_handler'
deprecated = 'your_package._papyri_directives:deprecated_handler'
```

### 编写自定义处理器

在你的包中创建处理器模块 `your_package/_papyri_directives.py`：

```python
"""papyri 自定义 RST 指令处理器。"""
from papyri.nodes import Admonition, Paragraph, Text, Code


def plot_handler(directive_node):
    """处理 .. plot:: 指令，生成图像节点。"""
    # 提取指令体中的代码
    body_text = _extract_body_text(directive_node)
    # 返回一个代码块节点（实际场景中可能需要执行并生成图像）
    return Code(
        children=(Text(body_text),),
        language="python",
        execution_status=None,
        out=None,
    )


def version_handler(directive_node):
    """处理 .. versionadded:: / .. versionchanged:: 指令。"""
    version_arg = _extract_argument(directive_node)
    body_text = _extract_body_text(directive_node)
    return Admonition(
        kind="versionadded",
        children=(
            Paragraph((Text(f"New in version {version_arg}. {body_text}"),)),
        ),
    )


def deprecated_handler(directive_node):
    """处理 .. deprecated:: 指令。"""
    version_arg = _extract_argument(directive_node)
    body_text = _extract_body_text(directive_node)
    return Admonition(
        kind="deprecated",
        children=(
            Paragraph((Text(f"Deprecated since version {version_arg}. {body_text}"),)),
        ),
    )


def _extract_argument(node):
    """从指令节点提取参数字符串。"""
    # 简化实现——实际需要遍历 tree-sitter CST 节点
    for child in node.children:
        if child.type == "argument":
            return child.text.decode()
    return ""


def _extract_body_text(node):
    """从指令节点提取体内容文本。"""
    for child in node.children:
        if child.type == "body":
            return child.text.decode().strip()
    return ""
```

## 示例3：包含叙述文档

配置 `docs_path` 以包含 RST 格式的叙述性文档（教程、指南等）：

```toml
[global]
module = 'your_package'
docs_path = "docs/source/"
```

Papyri 会遍历 `docs_path` 下的 `.rst` 文件，将其转换为 IR 并存入 DocBundle 的 `docs/` 目录。这些文档与 API 文档共享交叉引用系统。

## 示例4：多包配置

一次为多个包生成文档：

```bash
papyri gen numpy.toml scipy.toml matplotlib.toml
```

每个包的 TOML 独立配置，gen 依次处理。跨包的交叉引用在 ingest 阶段的 relink pass 中解析。

## 示例5：严格模式配置

CI 环境中使用严格模式，确保文档质量：

```bash
papyri gen your-package.toml \
    --fail \                  # 任何错误立即失败
    --fail-unseen-error \     # 新类型错误失败
    --exec \                  # 执行所有 doctest
    --pack                    # 生成后打包
```

## 关键点总结

1. **[global.directives] 是关键**：未注册的指令会在验证阶段报错，必须显式处理
2. **内置处理器**：`papyri.directives:drop` 丢弃，`papyri.directives:code_handler` 保留为代码
3. **exclude 使用限定名**：格式为 `module:attribute`，支持子模块路径
4. **submodules 必须可导入**：列出的子模块会被 `importlib.import_module()` 导入
5. **docs_path 指向 RST 文件**：叙述文档与 API 文档统一在 IR 层交叉引用
6. **{{version}} 模板**：meta.tag 中的 `{{version}}` 会被替换为包的实际版本号

## 相关示例

- [基础 gen 工作流](01-basic-gen.md)
- [Pack 与 Upload 工作流](03-pack-and-upload.md)
- [自定义指令处理器](04-custom-directive-handler.md)
