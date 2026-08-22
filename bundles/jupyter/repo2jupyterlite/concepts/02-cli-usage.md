---
type: Concept
title: CLI 命令使用详解
description: repo2jupyterlite 命令的参数、fetch/build 两阶段流程、本地与远程仓库构建、ContentProvider 检测机制
tags: [cli, command, fetch, build, contentprovider, argparse]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T16:00:00+08:00" }
verified: { by: "process:grep-api-verify", at: "2026-08-22T16:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: cli-source
    resource: /references/cli-source.md
    title: CLI入口信源
---

`repo2jupyterlite` 命令是工具的核心入口，实现了从指定源（本地目录或远程仓库）获取代码并构建 JupyterLite 静态站点的完整流程。

## 命令行参数

CLI 使用 Python 标准库 `argparse` 解析参数（F-023, F-024）：

```bash
repo2jupyterlite &lt;url&gt; &lt;output_dir&gt; [--ref &lt;ref&gt;]
```

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `url` | 位置参数 | 是 | 仓库URL或本地路径 |
| `output_dir` | 位置参数 | 是 | JupyterLite 构建输出目录（必须不存在） |
| `--ref` | 可选参数 | 否 | 检出的分支/tag/commit引用，默认 None（使用默认分支） |

### 参数约束

- **output_dir 不可已存在**：如果 `os.path.exists(args.output_dir)` 返回 True，程序打印错误并 `sys.exit(1)`（F-025）。这是为了防止意外覆盖已有构建产物。
- **url 可以是本地路径或远程URL**：程序通过 `os.path.exists(args.url)` 自动判断（F-026）。

## 执行流程

CLI 的 `main()` 函数执行流程分为两个主要阶段：**获取（fetch）** 和 **构建（build）**。

### 流程图

```
开始
  │
  ├─ 解析参数
  │
  ├─ 检查 output_dir 是否存在？──是──→ 报错退出
  │
  ├─ url 是本地路径？
  │    ├─ 是 → checkout_dir = url，无需fetch
  │    └─ 否 → 创建TemporaryDirectory
  │            → fetch(url, ref, checkout_dir)
  │
  ├─ build(checkout_dir, output_dir)
  │
  └─ 打印访问提示 → 结束
```

### 本地路径模式

当 `url` 参数指向一个本地已存在的路径时（F-026）：

1. 直接使用该路径作为 `checkout_dir`
2. 跳过 fetch 阶段
3. 使用 `nullcontext()` 作为临时目录上下文管理器（因为不需要清理）
4. 直接调用 `build()`

这适用于本地已有 notebook 目录的场景。

### 远程仓库模式

当 `url` 不是本地路径时（F-027）：

1. 创建 `TemporaryDirectory()` 作为临时检出目录
2. 调用 `fetch(args.url, args.ref, checkout_dir)` 将仓库克隆/下载到临时目录
3. 在 `with temp_dir:` 上下文中调用 `build()`
4. 构建完成后临时目录自动清理

## Fetch 阶段

`fetch(url, ref, checkout_path)` 函数负责检测源类型并获取仓库内容。

### ContentProvider 检测链

fetch 遍历预定义的 `content_providers` 列表（F-014），按顺序尝试检测：

```python
content_providers = [
    contentproviders.Local,      # 本地目录
    contentproviders.Zenodo,     # Zenodo 数据集
    contentproviders.Figshare,   # Figshare 数据集
    contentproviders.Dataverse,  # Dataverse 数据集
    contentproviders.Hydroshare, # Hydroshare 水文数据
    contentproviders.Swhid,      # Software Heritage 标识符
    contentproviders.Mercurial,  # Mercurial 仓库
    contentproviders.Git,        # Git 仓库
]
```

检测逻辑（F-016）：
1. 对每个 ContentProvider 类实例化
2. 调用 `cp.detect(url, ref=ref)` 
3. 如果返回非 None 的 spec 对象，则选中该 provider
4. 记录日志 `"Picked {ClassName} content provider."`
5. break 跳出循环

**注意**：列表顺序很重要——Local 排在 Git 前面意味着本地路径检测优先于 Git URL 检测。

### 获取内容

选中 provider 后（F-018）：
1. 调用 `picked_content_provider.fetch(spec, checkout_path, yield_output=True)`
2. 该方法返回一个生成器，逐行产生获取过程的日志输出
3. 每行通过 `log.info(log_line, extra=dict(phase="fetching"))` 记录

### 无匹配 Provider

如果所有 ContentProvider 都无法识别 URL（F-017）：
- 记录 ERROR 级别的日志
- **静默返回**（不抛异常，不退出程序）
- FIXME 注释表明此处错误处理有待改进

这意味着传入无法识别的 URL 时，程序不会崩溃，但后续 build 阶段会在空目录上运行。

## Build 阶段

`build(repo_dir, output_dir)` 函数调用 JupyterLite CLI 完成静态站点构建。

### 构建命令

```python
cmd = [
    "jupyter", "lite", "build", ".",
    "--output-dir", abs_output_path,
    "--contents", ".",
]
```

各参数含义：
- `jupyter lite build`：JupyterLite 构建命令
- `.`：构建当前目录（即 repo_dir，因为 cwd 设置为 repo_dir）
- `--output-dir &lt;abs_output_path&gt;`：输出目录的绝对路径
- `--contents .`：将当前目录作为内容目录（即把仓库中的 notebook 文件包含进去）

### 配置文件自动检测

如果仓库根目录存在 `jupyterlite_config.json`（F-021），自动追加 `--config jupyterlite_config.json` 参数。这允许仓库自定义 JupyterLite 配置（如内核设置、禁用某些界面等）。

### 执行构建

通过 `subprocess.check_call(cmd, cwd=repo_dir)` 执行（F-022）：
- 在 `repo_dir` 作为工作目录执行命令
- `check_call` 在命令返回非零退出码时抛出 `CalledProcessError`

### 工作目录处理

`abs_output_path = os.path.abspath(output_dir)`（F-066）确保输出目录使用绝对路径，避免因 cwd 切换导致路径错误。

## 日志输出

CLI 在模块级别配置了日志（F-023）：

```python
logging.basicConfig(format="%(asctime)s %(msg)s", level=logging.DEBUG)
```

日志格式包含时间戳和消息，级别为 DEBUG（输出所有日志）。fetch 阶段的输出带有 `phase="fetching"` 额外字段。

## 使用示例

### 构建本地目录

```bash
# 构建当前目录下的notebook
repo2jupyterlite . ./my-jupyterlite
```

### 构建远程 Git 仓库

```bash
# 构建GitHub仓库的main分支
repo2jupyterlite https://github.com/username/repo ./output --ref main
```

### 构建指定 commit

```bash
repo2jupyterlite https://github.com/username/repo ./output --ref abc1234
```

### 构建后预览

```bash
cd ./output
python -m http.server 8000
# 浏览器访问 http://localhost:8000
```

## 注意事项

- 构建过程需要 Node.js 环境（JupyterLite 构建前端资源时使用）
- `environment.yml` 中列出的包会在 JupyterLite 构建时被安装到 WASM 环境中，但只有纯 Python 包和 emscripten-forge 编译的包能成功安装
- 临时目录使用 Python 的 `tempfile.TemporaryDirectory()`，在 with 块退出时自动删除
- 本地路径模式下不会复制目录内容——jupyter lite build 直接在原目录上操作（以原目录为 cwd）

## 相关概念

- [01-快速开始](01-getting-started.md)
- [04-仓库提供者系统](04-repo-providers.md)
- [06-构建流程与缓存策略](06-build-process.md)
