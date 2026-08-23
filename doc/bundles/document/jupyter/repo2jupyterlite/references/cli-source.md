---
type: Reference
title: CLI 入口信源
description: repo2jupyterlite/app.py CLI 模块的API登记，包含main/fetch/build函数签名与行为
tags: [cli, app, main, fetch, build, argparse, contentproviders]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T16:00:00+08:00" }
verified: { by: "process:grep-api-verify", at: "2026-08-22T16:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: app-py
    resource: ../../../../../../external/libs/jupyter/repo2jupyterlite/repo2jupyterlite/app.py
    title: repo2jupyterlite/app.py CLI源码
---

## 模块概览

`repo2jupyterlite/app.py` 是 CLI 工具的核心模块，包含命令行入口、仓库获取和 JupyterLite 构建逻辑。

## 公共 API

### `content_providers`（模块级列表）

```python
content_providers = [
    contentproviders.Local,
    contentproviders.Zenodo,
    contentproviders.Figshare,
    contentproviders.Dataverse,
    contentproviders.Hydroshare,
    contentproviders.Swhid,
    contentproviders.Mercurial,
    contentproviders.Git,
]
```

来自 `repo2docker.contentproviders`，按顺序遍历检测URL类型。

### `fetch(url, ref, checkout_path)`

**签名**：`fetch(url: str, ref: str | None, checkout_path: str) -&gt; None`

**行为**：
1. 遍历 `content_providers`，对每个类实例化后调用 `cp.detect(url, ref=ref)`
2. 第一个返回非 None spec 的 ContentProvider 被选中
3. 遍历选中 provider 的 `fetch(spec, checkout_path, yield_output=True)` 输出，逐行 INFO 日志
4. 无匹配 provider 时记录 ERROR 日志并 return（不抛异常）

**参数**：
- `url`：仓库URL或本地路径
- `ref`：分支/tag/commit引用，可为None
- `checkout_path`：检出目标目录（应为空目录）

### `build(repo_dir, output_dir)`

**签名**：`build(repo_dir: str, output_dir: str) -&gt; None`

**行为**：
1. 构造命令：`jupyter lite build . --output-dir &lt;abs_output_path&gt; --contents .`
2. 如果 `&lt;repo_dir&gt;/jupyterlite_config.json` 存在，追加 `--config jupyterlite_config.json`
3. 在 `cwd=repo_dir` 下执行 `subprocess.check_call(cmd)`

**参数**：
- `repo_dir`：包含仓库内容的目录
- `output_dir`：JupyterLite 构建输出目录的绝对路径

### `main()`

**签名**：`main() -&gt; None`

**行为**：
1. argparse 解析参数：
   - 位置参数 `url`：要构建的仓库URL
   - 位置参数 `output_dir`：输出目录路径
   - 可选参数 `--ref`：指定检出的引用（默认None）
2. 如果 `output_dir` 已存在，打印错误并 `sys.exit(1)`
3. 如果 `url` 是本地路径（`os.path.exists(args.url)`）：
   - 直接使用该路径作为 checkout_dir，temp_dir 为 nullcontext()
4. 否则：
   - 创建 TemporaryDirectory
   - 调用 `fetch(args.url, args.ref, checkout_dir)`
5. 在 `with temp_dir:` 中调用 `build(checkout_dir, args.output_dir)`
6. 打印提示信息：`Go to http://localhost:8000/{output_dir}`

## 日志配置

```python
logging.basicConfig(format="%(asctime)s %(msg)s", level=logging.DEBUG)
log = logging
```

日志格式包含时间戳和消息，级别 DEBUG。
