---
type: example
title: "与 MyST 构建流程集成"
description: "如何在 MyST Markdown 项目中结合 jupyterlab-myst（JupyterLab 编辑）和 myst-execute（构建时执行）创建可计算文档的完整工作流"
tags: [jupyterlab-myst, myst-execute, workflow, integration, build]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "/references/plugin-entry-src.md"
    facts: [F-003, F-005, F-006]
related_concepts:
  - /concepts/00-architecture-plugins.md
  - /concepts/03-inline-expressions.md
  - ../myst-execute/concepts/00-execution-architecture.md
---

# 与 MyST 构建流程集成

jupyterlab-myst 和 myst-execute 是互补工具：jupyterlab-myst 在 JupyterLab IDE 中提供交互式编辑体验，myst-execute 在构建时执行 Notebook 生成静态站点。本示例展示如何将两者结合形成完整的可计算文档工作流。

## 工作流概述

```
┌─────────────────────────────────────────────┐
│  JupyterLab + jupyterlab-myst（编辑阶段）    │
│                                             │
│  - 编写 MyST Markdown 单元格                 │
│  - 交互式执行代码单元格                      │
│  - inline expression 即时求值               │
│  - 预览 directives 渲染效果                  │
│  - 保存为 .ipynb 文件                        │
└──────────────────┬──────────────────────────┘
                   │ .ipynb 文件
                   ▼
┌─────────────────────────────────────────────┐
│  mystmd build + myst-execute（构建阶段）     │
│                                             │
│  - 解析 .ipynb 和 .md 文件                   │
│  - 构建时执行代码单元格（或使用缓存）          │
│  - 转换 inline expression 为静态输出         │
│  - 生成 HTML 静态站点                        │
└──────────────────┬──────────────────────────┘
                   │ 静态 HTML
                   ▼
┌─────────────────────────────────────────────┐
│  部署（可选 + thebe 交互）                    │
│                                             │
│  - 静态 HTML 包含 myst-execute 输出          │
│  - 可选集成 thebe 运行时交互                 │
│  - 读者可重新执行代码（Binder/JupyterLite）  │
└─────────────────────────────────────────────┘
```

## 编辑阶段：JupyterLab + jupyterlab-myst

### 项目设置

创建项目目录：

```bash
mkdir my-myst-project
cd my-myst-project

# 创建 myst.yml 配置
cat > myst.yml << 'EOF'
version: 1
project:
  title: "My Computable Document"
  execute:
    timeout: 120
  kernels:
    python3:
      name: python3
      display_name: Python 3
      language: python
site:
  title: "My Computable Document"
EOF
```

### 在 JupyterLab 中编辑

1. 启动 JupyterLab：`jupyter lab`
2. 确保 jupyterlab-myst 已安装
3. 创建新 Notebook，选择 Python 3 内核
4. 将第一个单元格改为 Markdown 类型，输入 frontmatter + 内容：

```markdown
---
title: "数据分析示例"
kernelspec:
  name: python3
  display_name: Python 3
---

# 数据分析示例

本文档演示 jupyterlab-myst 与 myst-execute 的协同工作。
```

5. 创建代码单元格：

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

np.random.seed(42)
data = np.random.randn(1000)
mean = data.mean()
std = data.std()
```

6. Shift+Enter 执行代码。

7. 创建 Markdown 单元格使用 inline expression：

```markdown
## 结果

数据共 {eval}`len(data)` 个样本，
均值为 {eval}`mean:.4f`，
标准差为 {eval}`std:.4f`。

下图展示数据分布：
```

8. 再创建代码单元格：

```python
plt.figure(figsize=(8, 4))
plt.hist(data, bins=30, edgecolor='black')
plt.title('Data Distribution')
plt.axvline(mean, color='red', linestyle='--', label=f'Mean = {mean:.2f}')
plt.legend()
plt.show()
```

9. Shift+Enter 执行后，Markdown 单元格中的 inline expression 自动求值显示。

### 保存 Notebook

在 JupyterLab 中保存 Notebook（File → Save Notebook），文件扩展名为 .ipynb。jupyterlab-myst 的 inline expression 结果保存在 metadata 中，但 myst-execute 构建时会重新执行。

## 构建阶段：mystmd build

### 安装 mystmd

```bash
npm install -g mystmd
```

### 构建项目

```bash
# 初始化 MyST 项目（如果还没有 myst.yml）
myst init

# 构建（使用缓存）
myst build

# 强制重新执行所有代码（忽略缓存）
myst build --ignore-cache
```

### 构建过程中发生了什么

1. **解析**：mystmd 解析 .ipynb 文件，提取 Markdown 和代码单元格
2. **执行**：myst-execute 启动 Jupyter 内核，执行代码单元格
3. **缓存**：执行结果缓存到 `_build/.cache/`（MD5 键控）
4. **inline expression**：构建时求值，结果直接嵌入输出 HTML（静态，不需要内核）
5. **转换**：MyST directives 转换为 HTML 组件
6. **输出**：生成静态 HTML 站点到 `_build/site/`

### 关键配置

在 myst.yml 中确保配置了正确的内核：

```yaml
project:
  execute:
    timeout: 120
    cache: true
  kernels:
    python3:
      name: python3
```

文档级 frontmatter 也可以覆盖：

```markdown
---
title: "文档标题"
kernelspec:
  name: python3
execute:
  timeout: 300
  cache: false  # 本文档禁用缓存
---
```

## 部署阶段（可选：添加 thebe 交互）

如果希望静态站点中的代码也可被读者交互执行，可以集成 thebe：

1. 在 myst.yml 中启用 thebe：

```yaml
site:
  template: book-theme
  options:
    thebe:
      binder:
        repo: "your-username/your-repo"
        ref: "main"
```

2. 构建时 myst-theme 会自动注入 thebe 相关的 JavaScript 和配置
3. 读者打开页面后点击"Activate"按钮连接 Binder，即可交互式执行代码

## 兼容性说明

### inline expression 的兼容性

jupyterlab-myst 和 myst-execute 对 inline expression 的处理方式不同但兼容：

| 阶段 | jupyterlab-myst（JupyterLab） | myst-execute（构建时） |
|------|-------------------------------|----------------------|
| 执行方式 | user_expressions 内核请求 | 常规 execute_request |
| 结果存储 | cell metadata['user_expressions'] | 直接写入 MDAST output 节点 |
| 格式 | MIME bundle（text/plain, text/html, image/png 等） | 与代码单元格输出相同格式 |
| 持久化 | .ipynb metadata | 构建缓存 JSON / HTML 输出 |

两者都解析 `{eval}\`expression\`` 语法，在各自的执行环境中求值。

### directives 兼容性

jupyterlab-myst 注册的 directives 列表与 myst-execute 构建时使用的是同一套 MyST 生态包（myst-ext-card、myst-ext-grid、myst-ext-proof 等），渲染结果一致。

### 注意事项

1. **不要依赖 jupyterlab-myst 的 inline expression 缓存**：myst-execute 构建时会重新执行所有表达式，JupyterLab 中缓存的结果不会被使用（避免使用过时的结果）。

2. **kernelspec 名称一致**：确保 myst.yml 中的 kernelspec.name 与 JupyterLab 中使用的内核名称一致。

3. **Notebook 信任**：在 JupyterLab 中首次打开 .ipynb 时，inline expression 结果不会显示（Notebook 不受信任），执行一个代码单元格后自动信任。

4. **文件路径**：JupyterLab 中的相对路径（如 `pd.read_csv('data.csv')`）是相对于 .ipynb 文件所在目录。myst build 时也是相对于项目根目录（myst.yml 所在位置），确保两者一致。

## 推荐工作流

1. **在 JupyterLab 中开发**：使用 jupyterlab-myst 交互式编写和测试代码、调整 Markdown
2. **定期构建预览**：`myst start` 启动开发服务器，实时预览构建结果
3. **提交前完整构建**：`myst build --ignore-cache` 确保所有代码从零执行通过
4. **部署**：将 `_build/site/` 部署到静态托管服务
5. **（可选）启用 thebe**：让读者也能交互执行代码

## 相关文档

- [01-using-jupyterlab-myst.md](01-using-jupyterlab-myst.md)：安装和基本使用
- [03-inline-expression-workflow.md](03-inline-expression-workflow.md)：内联表达式高级用法
- [myst-execute examples/01-configure-notebook-execution.md](../../myst-execute/examples/01-configure-notebook-execution.md)：myst-execute 构建配置
