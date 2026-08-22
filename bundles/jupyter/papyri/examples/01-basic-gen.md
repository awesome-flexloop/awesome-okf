---
type: Example
title: "基础 gen 工作流"
description: "从安装 papyri 到为 Python 包生成 IR 文档的完整可运行流程，包含 TOML 配置编写、gen 命令执行和结果检查"
tags: [basic, gen, getting-started, toml, workflow]
generated: { by: "reference_agent/trae-soLO", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: papyri-src
    resource: "/references/papyri-source.md"
    title: "Papyri Python 核心包源码信源"
  - id: cli-src
    resource: "/references/cli-source.md"
    title: "Papyri CLI 命令源码信源"
  - id: config-src
    resource: "/references/config-source.md"
    title: "Papyri 配置系统源码信源"
---

# 基础 gen 工作流

本示例演示 Papyri 的最基本用法：编写 TOML 配置、运行 `papyri gen`、检查输出的 DocBundle。

## 示例1：最小 TOML 配置

为一个已安装的 Python 包（以 papyri 自身为例）创建最小配置文件 `my-lib.toml`：

```toml
[meta]
github_slug = 'carreau/papyri'
tag = '{{version}}'
pypi = 'papyri'

[global]
module = 'papyri'
```

这是最简配置——只指定目标模块名 `module` 和基本元数据。保存为 `my-papyri.toml`。

## 示例2：运行 gen

```bash
# 安装 papyri（如果尚未安装）
pip install papyri

# 运行 gen，使用上面的配置文件
papyri gen my-papyri.toml
```

gen 会：
1. 导入 `papyri` 模块
2. 遍历其公开 API（模块、类、函数）
3. 解析每个对象的 docstring
4. 在 `~/.papyri/data/papyri_<version>/` 生成 DocBundle 目录

输出目录结构：

```
~/.papyri/data/papyri_0.1.0/
├── papyri.json          # Bundle 清单
├── module/
│   └── papyri:*.json    # 每个 API 对象一个 JSON 文件
├── docs/                # 叙述文档（如果配置了 docs_path）
├── examples/            # 示例文档
└── assets/              # 二进制资源
```

## 示例3：快速检查生成结果

```bash
# 查看 Bundle 清单
cat ~/.papyri/data/papyri_*/papyri.json | python -m json.tool

# 查看某个 API 对象的 IR JSON
cat ~/.papyri/data/papyri_*/module/papyri:gen.json | python -m json.tool

# 数一下生成了多少个 API 文档
ls ~/.papyri/data/papyri_*/module/ | wc -l
```

## 示例4：带 doctest 执行的 gen

如果目标包的 docstring 包含可执行的 Examples 节，使用 `--exec` 运行代码示例：

```bash
papyri gen my-papyri.toml --exec
```

执行结果会记录在 Code 节点的 `execution_status` 和 `out` 字段中：
- `"ok"`：执行成功，输出匹配
- `"error"`：执行出错

## 示例5：只生成特定对象

调试时使用 `--only` 只生成一个或几个限定名：

```bash
# 只生成 papyri:gen_main 函数
papyri gen my-papyri.toml --only papyri:gen_main

# 生成多个对象
papyri gen my-papyri.toml --only papyri:gen_main --only papyri:nodes
```

> [!NOTE]
> 限定名使用冒号分隔模块路径和属性路径，如 `numpy.linalg:norm` 而不是 `numpy.linalg.norm`。

## 示例6：无类型推断快速生成

开发调试时跳过类型推断以加速：

```bash
papyri gen my-papyri.toml --no-infer
```

## 关键点总结

1. **TOML 配置是 gen 的唯一入口**：所有生成参数通过 TOML 和命令行选项控制
2. **输出在 ~/.papyri/data/<lib>_<ver>/**：每个库版本一个独立目录
3. **JSON 格式便于检查**：gen 输出是人类可读的 JSON，不是 CBOR
4. **--only 选项用于调试**：只生成指定对象，大幅缩短调试周期
5. **--exec 执行 doctest**：不指定时代码块不执行，只做解析
6. **限定名用冒号**：`module.path:attribute.path`，不是点号

## 相关示例

- [自定义 TOML 配置](02-custom-config.md)
- [Pack 与 Upload 工作流](03-pack-and-upload.md)
