---
type: Concept
title: 架构概览
description: sphinxext-rediraffe 整体架构：核心组件、事件钩子机制、从配置到重定向HTML生成的完整链路、双Builder设计
tags: [sphinxext-rediraffe, architecture, builder, event-hook, build-finished]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T16:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T16:30:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: rediraffe-source
    resource: /references/rediraffe-source.md
    title: sphinxext-rediraffe 源码信源登记
---

# 架构概览

## 整体架构

sphinxext-rediraffe 是一个单文件（485行）的Sphinx扩展，架构极为精简。核心由三个部分组成：

1. **图处理层**：解析重定向配置，构建有向图，执行链式压缩和循环检测
2. **构建钩子层**：通过 Sphinx 的 `build-finished` 事件，在HTML构建完成后生成重定向页面
3. **Diff检查层**：两个自定义 Builder，通过 Git diff 检测文件变更，验证/自动补全重定向配置

```
┌─────────────────────────────────────────────────────┐
│                   conf.py 配置                       │
│  rediraffe_redirects (dict/str)                     │
│  rediraffe_branch (str)                             │
│  rediraffe_template (str)                           │
│  rediraffe_auto_redirect_perc (int)                 │
└────────┬────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│                setup(app) 扩展入口                    │
│  ┌─────────────────┐  ┌──────────────────────────┐  │
│  │ add_config_value│  │ add_builder              │  │
│  │ (4个配置项)      │  │ (2个自定义Builder)       │  │
│  └─────────────────┘  └──────────────────────────┘  │
│  ┌──────────────────────────────────────────────┐   │
│  │ connect('build-finished', build_redirects)   │   │
│  └──────────────────────────────────────────────┘   │
└────────┬────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│              运行时两个独立路径                        │
│                                                     │
│  ┌─────────────────────┐  ┌──────────────────────┐  │
│  │  正常HTML构建路径    │  │  CI检查/自动写入路径  │  │
│  │                     │  │                      │  │
│  │ build-finished 事件 │  │ sphinx-build -b      │  │
│  │      ↓              │  │  rediraffecheckdiff  │  │
│  │ build_redirects()   │  │       或             │  │
│  │      ↓              │  │  rediraffewritediff  │  │
│  │ create_graph()      │  │      ↓               │  │
│  │      ↓              │  │ CheckRedirectsDiff   │  │
│  │ create_simple_      │  │ Builder.init()       │  │
│  │   redirects()       │  │      ↓               │  │
│  │      ↓              │  │ git diff 检测        │  │
│  │ 写HTML重定向文件    │  │ 重命名/删除文件       │  │
│  │ + JSON记录          │  │ 验证/自动写入        │  │
│  └─────────────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

## 核心组件详解

### 1. 图处理函数

| 函数 | 职责 | 调用时机 |
|------|------|---------|
| `create_graph(path)` | 解析重定向文本文件为 `dict[str, str]` | 配置为文件路径时，build-finished 或 Builder.init() |
| `create_simple_redirects(dict)` | 链式压缩 + 循环检测，输出叶子节点映射 | 图解析后立即调用 |
| `remove_suffix(name, suffixes)` | 移除源文件后缀（.rst/.md等） | 路径转换阶段 |

图处理的核心思想是将重定向关系建模为**有向图**，然后做两件事：
- 检测环（循环重定向是致命错误）
- 将所有路径压缩到叶子节点（用户只跳一次）

### 2. build_redirects 主函数

`build_redirects(app, exception)` 是扩展的核心函数，连接到 Sphinx 的 `build-finished` 事件。它在HTML构建**完成后**执行，执行流程如下：

```
build_redirects 执行流程：
1. 读取/初始化 _rediraffe_redirected.json 记录
2. 检查构建器类型（跳过linkcheck和非HTML构建器）
3. 加载Jinja2模板（自定义文件或默认模板）
4. 解析重定向配置（dict直接用 / 文件调用create_graph）
5. 调用 create_simple_redirects 压缩链路
6. 对每个重定向对：
   a. 路径标准化（Windows→POSIX）
   b. 移除源后缀，添加.html
   c. dirhtml特殊处理（page→page/index.html）
   d. 检查源/目标文件状态
   e. 渲染Jinja2模板写入HTML
   f. 更新JSON记录
7. 写入 _rediraffe_redirected.json
```

关键设计决策：
- **在 build-finished 阶段执行**：此时所有HTML文件已生成，可以验证目标文件是否存在
- **不修改已有内容文件**：只在源HTML位置不存在时才创建重定向文件
- **增量构建支持**：通过JSON记录避免重复写入

### 3. 自定义 Builder 体系

rediraffe 注册了两个自定义 Builder：

#### CheckRedirectsDiffBuilder（name: `rediraffecheckdiff`）

这是一个"伪构建器"——它不生成任何输出文件，而是利用 Builder.init() 生命周期执行 Git diff 检查：

```
执行流程：
1. 解析 rediraffe_redirects 配置
2. 调用 git rev-parse --show-toplevel 获取仓库根目录
3. 调用 git diff --name-status --diff-filter=R <branch> 获取重命名文件
4. 调用 git diff --diff-filter=D --name-only <branch> 获取删除文件
5. 对每个删除/重命名的源文件：
   - 如果在重定向配置中 → 输出 info 日志
   - 如果不在重定向配置中 → 输出 error 日志，设置 statuscode=1
```

#### WriteRedirectsDiffBuilder（name: `rediraffewritediff`）

继承自 CheckRedirectsDiffBuilder，额外增加了自动写入功能：

```
执行流程：
1. 验证 rediraffe_redirects 必须是文件路径（str类型）
2. 调用父类 init() 执行 diff 检查
3. 对每个重命名文件：
   - 如果相似度 >= rediraffe_auto_redirect_perc
   - 自动以引号包裹格式追加到 redirects.txt 文件
```

## Sphinx 事件与扩展机制

rediraffe 使用标准的 Sphinx 扩展 API：

```python
def setup(app: Sphinx) -> ExtensionMetadata:
    # 注册配置值
    app.add_config_value('rediraffe_redirects', None, None)
    app.add_config_value('rediraffe_branch', '', None)
    app.add_config_value('rediraffe_template', None, None)
    app.add_config_value('rediraffe_auto_redirect_perc', 100, None)

    # 注册自定义Builder
    app.add_builder(CheckRedirectsDiffBuilder)
    app.add_builder(WriteRedirectsDiffBuilder)

    # 连接事件钩子
    app.connect('build-finished', build_redirects)

    return {
        'version': __version__,
        'env_version': 1,
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
```

关键元数据：
- **parallel_read_safe: True**：支持并行读取
- **parallel_write_safe: True**：支持并行写入（因为重定向在build-finished阶段，写操作在所有文档写入完成后执行）
- **env_version: 1**：环境版本号

## 支持的构建器

rediraffe 在 `build_redirects` 函数中显式检查构建器类型：

| 构建器类型 | 类名 | 是否支持 | 说明 |
|-----------|------|---------|------|
| HTML | `StandaloneHTMLBuilder` | ✅ | 标准HTML输出（page.html格式） |
| Directory HTML | `DirectoryHTMLBuilder` | ✅ | 目录URL格式（page/index.html） |
| ReadTheDocs | `readthedocs` | ✅ | RTD标准构建器 |
| ReadTheDocs DirHTML | `readthedocsdirhtml` | ✅ | RTD目录HTML构建器 |
| Link Check | `CheckExternalLinksBuilder` | ⏭️ 跳过 | 链接检查时不需要生成重定向 |
| 其他构建器 | — | ⏭️ 跳过 | 输出info日志说明不支持 |

## 数据流总览

以一次正常的 `sphinx-build -b html` 构建为例：

```
sphinx-build -b html . _build
    │
    ├─ Sphinx初始化 → setup() 注册配置、Builder、事件钩子
    │
    ├─ Sphinx读取源文件 → 解析RST/MD → 生成doctree
    │
    ├─ Sphinx写入HTML文件 → 每个文档生成对应的.html
    │
    └─ build-finished 事件触发
         │
         └─ build_redirects(app, exception=None)
              │
              ├─ 读取 _rediraffe_redirected.json（上次记录）
              ├─ 加载/解析重定向配置
              ├─ create_simple_redirects() 压缩链路
              ├─ 遍历每个重定向对
              │   ├─ 检查源.html是否已存在（冲突检测）
              │   ├─ 检查目标.html是否存在（有效性检测）
              │   └─ 渲染Jinja2模板 → 写入源.html路径
              └─ 写入 _rediraffe_redirected.json
```

## 为什么架构如此精简

rediraffe 的代码量极小（单文件485行）但功能完整，得益于几个关键设计选择：

1. **利用Sphinx已有机制**：不重新实现构建逻辑，只在 build-finished 钩子中插入重定向文件生成
2. **单一职责**：图处理、HTML生成、Git diff检查各司其职，函数边界清晰
3. **配置即数据**：重定向映射是简单的 key-value 对，不需要复杂的配置对象
4. **Builder做检查器**：巧妙利用Sphinx的Builder扩展点实现CI检查功能，而非发明新的命令行入口

## 相关概念

- [重定向图模型](/concepts/03-redirect-graph.md)
- [配置项详解](/concepts/04-configuration.md)
- [Builder体系详解](/concepts/05-builders.md)
- [Jinja2模板系统](/concepts/06-jinja-templates.md)
- [路径处理与跨平台兼容](/concepts/07-path-and-cross-platform.md)
- [sphinxext-rediraffe 源码信源登记](/references/rediraffe-source.md)
