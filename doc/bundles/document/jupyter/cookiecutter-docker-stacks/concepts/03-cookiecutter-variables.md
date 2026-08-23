---
type: Concept
title: "模板变量详解"
description: "cookiecutter.json的4个模板变量定义、14个基础镜像选项、预设配置文件用法"
tags: [cookiecutter, variables, json, config, base-image]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T09:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T09:00:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - { id: src-files, resource: "/references/template-files.md", title: "模板文件源码索引" }
  - { id: src-workflow, resource: "/references/workflow-source.md", title: "CI/CD工作流源码索引" }
---

# 模板变量详解

cookiecutter-docker-stacks 通过 `cookiecutter.json` 定义了4个模板变量，控制生成项目的名称、基础镜像等关键配置。

## cookiecutter.json 结构

```json
{
  "stack_name": "my-jupyter-stack",
  "stack_org": "my-project",
  "stack_base_image": [
    "quay.io/jupyter/docker-stacks-foundation",
    "quay.io/jupyter/base-notebook",
    ...（共14个选项）
  ],
  "stack_description": "{{cookiecutter.stack_name}} is a community maintained Jupyter Docker Stack image"
}
```

## 变量详解

### stack_name

| 属性 | 值 |
|------|-----|
| 默认值 | `"my-jupyter-stack"` |
| 类型 | 字符串 |
| 用途 | 生成项目的目录名、镜像名、README标题 |

`stack_name` 决定了：
- 生成的目录名：`./{{cookiecutter.stack_name}}/`
- Docker镜像名（与stack_org组合）：`{{cookiecutter.stack_org}}/{{cookiecutter.stack_name}}`
- CI/CD中的IMAGE_NAME环境变量：`${{ github.event.repository.name }}`（即仓库名）
- README.md中的标题：`# {{cookiecutter.stack_name}}`

**命名建议**：
- 使用小写字母、数字和连字符（kebab-case）
- 反映镜像用途，如 `finance-notebook`、`ml-training-stack`
- 避免特殊字符和空格

### stack_org

| 属性 | 值 |
|------|-----|
| 默认值 | `"my-project"` |
| 类型 | 字符串 |
| 用途 | Docker Hub用户名或组织名、CI/CD镜像所有者 |

`stack_org` 决定了：
- Docker镜像的完整路径：`{{cookiecutter.stack_org}}/{{cookiecutter.stack_name}}`
- CI/CD中的OWNER环境变量：`${{ github.repository_owner }}`（即GitHub仓库所有者）
- 测试中的TEST_IMAGE：`{{cookiecutter.stack_org}}/{{cookiecutter.stack_name}}`

**注意**：CI/CD中`OWNER`使用的是`github.repository_owner`（GitHub仓库所有者），而非cookiecutter中设置的值。推送到Docker Hub时，用户名也使用`env.OWNER`，密码使用`secrets.DOCKERHUB_TOKEN`。因此GitHub仓库名和Docker Hub用户名需要匹配，或在推送步骤中修改。

### stack_base_image

| 属性 | 值 |
|------|-----|
| 默认值 | 列表第一个选项（`quay.io/jupyter/docker-stacks-foundation`） |
| 类型 | 选择列表（14个选项） |
| 用途 | Dockerfile中的FROM指令基础镜像 |

这是最重要的变量，决定了你的自定义镜像从哪个官方镜像开始构建。

### stack_description

| 属性 | 值 |
|------|-----|
| 默认值 | `"{{cookiecutter.stack_name}} is a community maintained Jupyter Docker Stack image"` |
| 类型 | 字符串（支持Jinja2模板） |
| 用途 | README.md中的项目描述 |

`stack_description` 使用了Jinja2模板语法，会自动引用 `stack_name` 的值。你可以在交互式生成时自定义描述。

## 14个基础镜像选项

完整列表及选择建议：

| 序号 | 基础镜像 | 适用场景 | 包含内容 |
|------|---------|---------|---------|
| 1 | `quay.io/jupyter/docker-stacks-foundation` | 需要完全自定义 | Ubuntu 24.04 + Micromamba + tini + start.sh，无Jupyter |
| 2 | `quay.io/jupyter/base-notebook` | 最小Jupyter环境 | Foundation + JupyterLab/Server/Hub + pandoc |
| 3 | `quay.io/jupyter/minimal-notebook` | 需要命令行工具 | Base + git/curl/TeX/常用CLI |
| 4 | `quay.io/jupyter/scipy-notebook` | Python数据科学 | Minimal + numpy/pandas/scipy/matplotlib/sklearn |
| 5 | `quay.io/jupyter/r-notebook` | R语言分析 | Minimal + R + IRKernel + tidyverse |
| 6 | `quay.io/jupyter/julia-notebook` | Julia科学计算 | Minimal + Julia + IJulia + Pluto |
| 7 | `quay.io/jupyter/tensorflow-notebook` | TensorFlow CPU | Scipy + TensorFlow |
| 8 | `quay.io/jupyter/tensorflow-notebook:cuda-latest` | TensorFlow GPU | Scipy + TensorFlow + CUDA |
| 9 | `quay.io/jupyter/pytorch-notebook` | PyTorch CPU | Scipy + PyTorch |
| 10 | `quay.io/jupyter/pytorch-notebook:cuda11-latest` | PyTorch GPU (CUDA 11) | Scipy + PyTorch + CUDA 11 |
| 11 | `quay.io/jupyter/pytorch-notebook:cuda12-latest` | PyTorch GPU (CUDA 12) | Scipy + PyTorch + CUDA 12 |
| 12 | `quay.io/jupyter/datascience-notebook` | 多语言数据科学 | Scipy + R + Julia + rpy2 |
| 13 | `quay.io/jupyter/pyspark-notebook` | PySpark大数据 | Scipy + OpenJDK 21 + Spark + PyArrow |
| 14 | `quay.io/jupyter/all-spark-notebook` | Spark全语言 | PySpark + R(sparklyr/ggplot2) |

### 基础镜像选择决策树

```
需要Jupyter吗？
├─ 否 → docker-stacks-foundation（自己装一切）
└─ 是 → 需要科学计算包吗？
    ├─ 否，只要基础Jupyter → base-notebook
    ├─ 否，但需要CLI工具和PDF导出 → minimal-notebook
    └─ 是 → 主要用什么语言/框架？
        ├─ Python数据科学 → scipy-notebook
        ├─ R语言 → r-notebook
        ├─ Julia → julia-notebook
        ├─ Python+R+Julia全要 → datascience-notebook
        ├─ TensorFlow
        │   ├─ CPU → tensorflow-notebook
        │   └─ GPU → tensorflow-notebook:cuda-latest
        ├─ PyTorch
        │   ├─ CPU → pytorch-notebook
        │   ├─ GPU (CUDA 11) → pytorch-notebook:cuda11-latest
        │   └─ GPU (CUDA 12) → pytorch-notebook:cuda12-latest
        └─ Spark
            ├─ 仅PySpark → pyspark-notebook
            └─ PySpark+R+SparkR → all-spark-notebook
```

## 预设配置文件（configs/）

模板仓库的 `configs/` 目录包含14个YAML配置文件，每个文件对应一个基础镜像选项。预设配置文件使用 `default_context` 预设模板变量值：

```yaml
# configs/scipy.yaml
default_context:
  stack_base_image: "quay.io/jupyter/scipy-notebook"
```

### 使用预设配置生成项目

```bash
# 使用scipy配置，非交互式生成
cookiecutter https://github.com/jupyter/cookiecutter-docker-stacks \
  --config-file configs/scipy.yaml \
  --no-input

# 本地克隆后的用法
cookiecutter . --config-file configs/pytorch-cuda12.yaml --no-input \
  --output-dir /tmp
```

使用 `--no-input` 参数时，cookiecutter不会进入交互模式，所有变量使用默认值或config-file中预设的值。stack_name和stack_org会使用cookiecutter.json中的默认值（"my-jupyter-stack"和"my-project"）。

### 自定义配置文件

你也可以创建自己的YAML配置文件，预设所有变量：

```yaml
# my-config.yaml
default_context:
  stack_name: "my-ml-stack"
  stack_org: "mycompany"
  stack_base_image: "quay.io/jupyter/pytorch-notebook:cuda12-latest"
  stack_description: "My company's machine learning Jupyter environment with PyTorch CUDA 12"
```

然后使用：

```bash
cookiecutter https://github.com/jupyter/cookiecutter-docker-stacks \
  --config-file my-config.yaml \
  --no-input
```

## 模板渲染机制

cookiecutter 使用 Jinja2 模板引擎渲染文件：

1. 目录名 `{{cookiecutter.stack_name}}` 被渲染为用户输入的值
2. 文件内容中的 `{{cookiecutter.xxx}}` 被替换为对应变量值
3. 某些文件通过文件名中的 `{{cookiecutter.stack_name}}` 实现路径动态化

特殊处理：
- **docker.yml** 中使用 `{% raw %}` 和 `{% endraw %}` 标记保护 GitHub Actions 表达式（`${{ }}`）不被 Jinja2 渲染
- prettier 和 yamllint 排除了 docker.yml，因为 Jinja2 语法会导致格式检查失败

```yaml
# docker.yml中的raw保护示例
env:
  {%- raw %}
  OWNER: ${{ github.repository_owner }}
  IMAGE_NAME: ${{ github.event.repository.name }}
  {%- endraw %}
```

## 命令行参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `--no-input` | 非交互式，使用默认/配置值 | `--no-input` |
| `--config-file` | 指定YAML配置文件 | `--config-file configs/scipy.yaml` |
| `--output-dir` | 指定输出目录 | `--output-dir /tmp` |
| `--overwrite-if-exists` | 覆盖已存在的目录 | `--overwrite-if-exists` |

## 相关概念

- [项目介绍](00-introduction.md)
- [快速上手](01-getting-started.md)
- [模板结构解析](02-template-structure.md)
- [Dockerfile模板与编写指南](04-dockerfile-template.md)
- [预设配置与基础镜像选择](08-config-presets.md)
