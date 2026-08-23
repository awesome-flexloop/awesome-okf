---
type: Example
title: CLI 构建仓库示例
description: 使用 repo2jupyterlite CLI 构建本地目录和远程GitHub仓库为JupyterLite静态站点的完整示例
tags: [cli, build, example, local, remote, github]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T16:00:00+08:00" }
verified: { by: "process:grep-api-verify", at: "2026-08-22T16:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: cli-source
    resource: /references/cli-source.md
    title: CLI入口信源
---

本示例演示如何使用 `repo2jupyterlite` CLI 命令构建 JupyterLite 静态站点，覆盖本地目录和远程GitHub仓库两种场景。

## 示例1：构建本地目录

假设当前目录下有一个包含 Jupyter Notebook 的项目：

```
my-notebooks/
├── 01-intro.ipynb
├── 02-data-analysis.ipynb
├── data/
│   └── sample.csv
├── environment.yml          # 可选：指定Python包依赖
└── jupyterlite_config.json  # 可选：JupyterLite配置
```

### 步骤1：创建示例项目

```bash
mkdir my-notebooks &amp;&amp; cd my-notebooks
```

创建一个简单的 `environment.yml`（可选，指定需要预装的包）：

```yaml
name: jupyterlite-env
channels:
  - conda-forge
dependencies:
  - numpy
  - pandas
  - matplotlib
```

> **注意**：JupyterLite 运行在浏览器 WASM 环境中，只有纯 Python 包和 emscripten-forge 编译的包能成功安装。`numpy`、`pandas`、`matplotlib` 等流行科学计算包已被 Pyodide 支持。

### 步骤2：执行构建

```bash
repo2jupyterlite . ./my-jupyterlite-site
```

这里：
- `.` 是源目录（当前目录的本地路径）
- `./my-jupyterlite-site` 是输出目录（必须不存在，否则报错退出）

CLI 检测到 `.` 是本地路径后，跳过 fetch 阶段，直接执行 `jupyter lite build`。

### 步骤3：预览构建结果

```bash
cd my-jupyterlite-site
python -m http.server 8000
```

浏览器访问 `http://localhost:8000`，即可看到 JupyterLab 界面，`content/` 目录中包含源目录下的所有 notebook 和文件。

## 示例2：构建远程 GitHub 仓库

### 构建默认分支

```bash
repo2jupyterlite https://github.com/yuvipanda/environment.yml demo-build
```

CLI 检测到 URL 不是本地路径，执行以下流程：
1. 创建临时目录
2. 通过 ContentProvider 链检测 URL 类型（Git）
3. 克隆仓库到临时目录
4. 在临时目录中执行 `jupyter lite build`
5. 构建产物输出到 `demo-build/`
6. 删除临时目录

### 构建指定分支/tag

```bash
repo2jupyterlite https://github.com/username/repo ./output --ref main
```

`--ref` 参数指定要检出的分支名、tag名或commit SHA。

### 构建指定 commit

```bash
repo2jupyterlite https://github.com/username/repo ./output --ref abc1234def5678
```

使用 commit SHA 可确保构建的确定性——同一 SHA 的仓库内容永远不变。

## 示例3：构建带配置的仓库

在仓库根目录放置 `jupyterlite_config.json` 来自定义 JupyterLite：

```json
{
  "jupyter-lite-schema-version": 0,
  "jupyter-config-data": {
    "appName": "My Custom JupyterLite",
    "disabledExtensions": ["@jupyterlab/toc-extension"]
  }
}
```

CLI 会自动检测到此文件并添加 `--config jupyterlite_config.json` 参数（参见 [CLI信源F-021](/references/cli-source.md)）。

## 常见问题

### 输出目录已存在

```
Output path ./output already exists, aborting...
```

**解决**：删除已有输出目录或选择新目录名：
```bash
rm -rf ./output
repo2jupyterlite https://github.com/user/repo ./output
```

### 构建失败

CLI 使用 `subprocess.check_call` 执行 `jupyter lite build`，如果 jupyter lite 命令返回非零退出码，会抛出 `CalledProcessError`。常见原因：
- Node.js 未安装或版本过旧
- `environment.yml` 中包含不支持的包
- 网络问题导致包下载失败

### ContentProvider 未匹配

如果输入的URL无法被任何ContentProvider识别，CLI会记录ERROR日志但不会崩溃，会尝试在空目录上执行build：

```
No matching content provider found for &lt;url&gt;.
```

**解决**：检查URL格式是否正确，或手动clone仓库后使用本地路径构建。

## CLI 参数速查

```bash
repo2jupyterlite &lt;url&gt; &lt;output_dir&gt; [--ref &lt;ref&gt;]
```

| 参数 | 说明 |
|------|------|
| `url` | 本地目录路径或远程仓库URL |
| `output_dir` | 构建输出目录（必须不存在） |
| `--ref` | 检出的分支/tag/commit（仅远程仓库） |

## 相关概念

- [02-CLI命令使用详解](/concepts/02-cli-usage.md)
- [06-构建流程与缓存策略](/concepts/06-build-process.md)
