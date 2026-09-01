---
type: Concept
title: CLI 命令参考
description: papyri 命令行工具的完整参考——gen、pack、unpack、upload、ingest、take、xref、render、bootstrap 等
tags: [papyri, cli, commands, reference, typer]
generated: { by: reference_agent/trae-soLO, at: "2026-08-22T00:00:00Z" }
verified: { by: "process:grep-api-check", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: cli-src
    resource: /references/cli-source.md
    title: Papyri CLI 命令源码信源
---

## CLI 总览

Papyri 使用 Typer 构建 CLI，入口在 `papyri/__init__.py`。顶层命令 `papyri` 有以下子命令：

```
papyri gen        生成 IR 文档（核心命令）
papyri pack       将 DocBundle 打包为 .papyri 文件
papyri unpack     解包 .papyri 文件为目录
papyri upload     上传 DocBundle 到 viewer
papyri ingest     摄取 DocBundle 到本地 GraphStore
papyri take       获取包的元数据信息
papyri xref       交叉引用诊断
papyri render     终端渲染文档（开发调试）
papyri bootstrap  初始化配置/目录
```

查看帮助：`papyri --help` 或 `papyri <command> --help`

## gen：生成文档

```
papyri gen [OPTIONS] CONFIG_FILES...
```

### 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `CONFIG_FILES` | List[Path] | ✅ | TOML 配置文件路径（支持多个） |

### 选项

| 选项 | 默认 | 说明 |
|------|------|------|
| `--install / --no-install` | `--install` | 是否自动安装缺失的包 |
| `--exec / --no-exec` | `--no-exec` | 是否执行 doctest 代码示例 || `--only TEXT` | 无 | 只生成指定限定名（如 `numpy:einsum`），可多次指定 |
| `--infer / --no-infer` | `--infer` | 是否进行类型推断（token→引用关联） |
| `--fail / --no-fail` | `--no-fail` | 遇到第一个错误即停止 |
| `--fail-early` | False | 覆盖提前错误选项 |
| `--fail-unseen-error / --no-fail-unseen-error` | `--no-fail-unseen-error` | 只在遇到新类型错误时失败 |
| `--exec-failure [raise|ignore]` | `raise` | 代码执行失败策略 |
| `--upload / --no-upload` | `--no-upload` | 生成后上传到 viewer |
| `--pack / --no-pack` | `--no-pack` | 生成后打包 |
| `--help` | - | 显示帮助 |

### 示例

```bash
# 基本生成
papyri gen examples/papyri.toml

# 快速测试（无推断、无执行）
papyri gen examples/papyri.toml --no-infer

# 执行代码示例
papyri gen examples/numpy.toml --exec

# 只生成特定对象
papyri gen examples/numpy.toml --only numpy:einsum --only numpy:array

# 生成并上传
papyri gen examples/papyri.toml --upload

# 严格模式
papyri gen examples/papyri.toml --fail --fail-unseen-error

# 多配置文件
papyri gen examples/numpy.toml examples/scipy.toml
```

## pack：打包

```
papyri pack [OPTIONS] BUNDLE_DIR
```

将 DocBundle 目录打包为 `.papyri` 文件。

### 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `BUNDLE_DIR` | Path | ✅ | DocBundle 目录路径 |

### 选项

| 选项 | 默认 | 说明 |
|------|------|------|
| `--output FILE` | 自动 | 输出文件路径（默认 `<module>-<version>.papyri`） |
| `--help` | - | 显示帮助 |

### 示例

```bash
# 打包 gen 输出
papyri pack ~/.papyri/data/papyri_0.1.0/

# 指定输出路径
papyri pack ~/.papyri/data/numpy_2.0.0/ -o numpy-2.0.0.papyri
```

## unpack：解包

```
papyri unpack [OPTIONS] ARTIFACT [OUTPUT_DIR]
```

将 `.papyri` 文件解包为 DocBundle 目录。包含 `_safe_child()` 路径遍历防护。

### 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `ARTIFACT` | Path | ✅ | `.papyri` 文件路径 |
| `OUTPUT_DIR` | Path | ❌ | 输出目录（默认为当前目录） |

### 示例

```bash
papyri unpack papyri-0.1.0.papyri /tmp/papyri-bundle/
```

## upload：上传

```
papyri upload [OPTIONS] PATH
```

将 DocBundle 目录或 `.papyri` 文件上传到 viewer。

### 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `PATH` | Path | ✅ | DocBundle 目录或 `.papyri` 文件路径 |

### 选项

| 选项 | 默认 | 说明 |
|------|------|------|
| `--url TEXT` | `http://localhost:4321/api/bundle` | 上传端点 URL（也可用 `PAPYRI_UPLOAD_URL` 环境变量） |
| `--token TEXT` | 无 | Bearer 认证令牌（也可用 `PAPYRI_UPLOAD_TOKEN` 环境变量） |
| `--help` | - | 显示帮助 |

### 示例

```bash
# 上传目录
papyri upload ~/.papyri/data/papyri_0.1.0/

# 上传 .papyri 文件
papyri upload numpy-2.0.0.papyri

# 指定远程服务器
papyri upload papyri-0.1.0.papyri --url https://docs.example.com/api/bundle --token mytoken
```

## ingest：摄取到本地

```
papyri ingest [OPTIONS] PATH
```

将 `.papyri` 文件摄取到本地 GraphStore（不启动 viewer 也可以索引文档）。

### 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `PATH` | Path | ✅ | `.papyri` 文件路径 |

## take：获取包信息

```
papyri take [OPTIONS] PACKAGE_NAME
```

获取指定包的版本和元数据信息。

## xref：交叉引用诊断

```
papyri xref [OPTIONS] BUNDLE_DIR
```

诊断 DocBundle 中的交叉引用状态，报告未解析的引用。

## render：终端渲染

```
papyri render [OPTIONS] QUALIFIED_NAME
```

在终端中渲染指定限定名的文档（用于开发调试，不依赖 viewer）。使用 Rich 终端渲染。

### 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `QUALIFIED_NAME` | str | ✅ | 限定名（如 `numpy:einsum`） |

## bootstrap：初始化

```
papyri bootstrap
```

初始化 Papyri 配置目录（`~/.papyri/`），创建必要的子目录。首次使用时自动调用。

## 退出码

| 退出码 | 含义 |
|--------|------|
| 0 | 成功 |
| 1 | 一般错误（配置错误、文件不存在等） |
| 2 | 生成过程中出现错误（`--fail` 模式下） |

## 相关概念

- [快速开始](01-getting-started.md)
- [gen 管线](05-gen-pipeline.md)
- [pack 与 upload](08-pack-and-upload.md)
- [配置系统](07-config-system.md)
