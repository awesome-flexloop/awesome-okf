---
type: Reference
title: Papyri CLI 命令源码信源
description: Papyri 命令行接口各子命令的参数、选项与行为源码索引
tags: [papyri, cli, typer, commands]
generated: { by: reference_agent/trae-soLO, at: "2026-08-22T00:00:00Z" }
verified: { by: "process:grep-api-check", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: papyri-repo
    resource: https://github.com/carreau/papyri
    title: Papyri GitHub Repository
---

## CLI 命令源码索引

源码路径：`external/libs/jupyter/papyri/papyri/cli/`

### 全局选项

在 `papyri/__init__.py` 中定义：

- `--version/-V`：显示版本号和 logo 后退出
- 所有子命令通过 `app.command()(_cmd)` 注册到 typer.Typer 应用
- `pretty_exceptions_enable=False`，`no_args_is_help=True`

### gen 命令（cli/gen.py）

**用法**：`papyri gen <config.toml>`

| 参数/选项 | 类型 | 默认值 | 说明 |
|-----------|------|--------|------|
| `file` | Argument (str) | - | TOML 配置文件路径，支持 glob 自动补全 |
| `--infer/--no-infer` | bool | True | 是否对代码示例运行类型推断 |
| `--exec` | bool \| None | None | 是否执行 docstring 代码示例 |
| `--debug` | bool | False | 调试模式 |
| `--no-progress` | flag | False | 禁用进度条（CI/调试器环境有用） |
| `--dry-run` | bool | False | 试运行模式 |
| `--api/--no-api` | bool | True | 是否生成 API 文档 |
| `--examples/--no-examples` | bool | True | 是否生成示例文档 |
| `--narrative/--no-narrative` | bool | True | 是否生成叙述性文档 |
| `--fail` | bool | False | 遇到第一个错误即失败 |
| `--fail-early` | bool | False | 覆盖提前错误选项 |
| `--fail-unseen-error` | bool | False | 遇到任何未见过的错误即失败 |
| `--only` | list[str] | None | 限制生成到指定的限定名（可重复） |
| `--upload` | flag | False | 生成后自动上传到 viewer |
| `--pack` | flag | False | 生成后自动打包为 .papyri 制品 |

### upload 命令

**用法**：`papyri upload <bundle-path>`

- 默认端点：`http://localhost:4321/api/bundle`（环境变量 `PAPYRI_UPLOAD_URL` 覆盖）
- 认证：`$PAPYRI_UPLOAD_TOKEN` 或 `--token`
- HTTP 方法：PUT
- User-Agent：`papyri-upload/<version>`（环境变量 `PAPYRI_VERSION` 覆盖）
- 支持上传：目录、`.papyri` 文件、`.zip` 包含的 `.papyri` 文件

### pack 命令

**用法**：`papyri pack <bundle-dir>`

- 输出：当前目录下的 `<module>-<version>.papyri` 文件
- 编码：CBOR（canonical 模式，RFC 8949 §4.2）+ gzip（zero mtime header）
- 确定性：同一输入目录两次运行产生字节完全相同的输出

### unpack 命令

**用法**：`papyri unpack <file.papyri> <output-dir>`

- 将 `.papyri` 制品解包回 JSON DocBundle 目录
- 路径安全：`_safe_child()` 拒绝逃逸目标目录的路径

### 其他命令

| 命令 | 文件 | 功能 |
|------|------|------|
| `find` | cli/find.py | 查找文档对象 |
| `describe` | cli/describe.py | 描述文档对象 |
| `debug` | cli/debug.py | 调试文档对象 |
| `diff` | cli/diff.py | 比较两个 DocBundle |
| `about` | cli/about.py | 显示项目信息 |
| `bootstrap` | cli/bootstrap.py | 引导配置 |
