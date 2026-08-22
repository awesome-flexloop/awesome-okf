---
type: Reference
title: 发布器抽象信源
description: binderlite/publish.py Publisher 基类与 LocalFilesystemPublisher 的API登记
tags: [publisher, storage, filesystem, cache, http, sentinel]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T16:00:00+08:00" }
verified: { by: "process:grep-api-verify", at: "2026-08-22T16:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: publish-py
    resource: ../../../../../../external/libs/jupyter/repo2jupyterlite/binderlite/publish.py
    title: binderlite/publish.py 源码
---

## 模块概览

`binderlite/publish.py` 定义了发布器抽象基类 `Publisher` 和本地文件系统实现 `LocalFilesystemPublisher`，负责构建产物的存储、存在性检查、上传和HTTP服务。

## 模块级变量

| 变量 | 类型 | 说明 |
|------|------|------|
| `output_dir_prefix` | `Path` | 值为 `Path("output")`，模块加载时 `os.makedirs(..., exist_ok=True)` |

## `Publisher`（抽象基类）

### `get_target_dir(self, slug)`（上下文管理器）

**装饰器**：`@contextmanager`

**参数**：`slug`：URL安全的仓库唯一标识

**基类行为**：
1. `tmpdirname = tempfile.mktemp()` 获取临时目录路径（不创建）
2. `yield tmpdirname`
3. finally 块中 `shutil.rmtree(tmpdirname)` 清理

**约定**：子类可覆盖此方法以改变目标目录策略。

### `exists(self, slug)`（异步）

**签名**：`async exists(self, slug) -&gt; bool`

**基类行为**：`raise NotImplementedError()`

**约定**：返回 slug 对应的构建产物是否已发布完成。

### `upload(self, source_dir, slug)`（异步）

**签名**：`async upload(self, source_dir, slug) -&gt; None`

**基类行为**：`raise NotImplementedError()`

**约定**：将 source_dir 中的构建产物上传/移动到 slug 对应的存储位置。

### `get_redirect_url(self, slug)`（异步）

**签名**：`async get_redirect_url(self, slug) -&gt; str`

**基类行为**：`raise NotImplementedError()`

**约定**：返回构建完成后重定向用户的URL。

### `mount_extra_handlers(self, app)`

**签名**：`mount_extra_handlers(self, app: FastAPI) -&gt; None`

**基类行为**：`pass`（无操作）

**约定**：子类可在此挂载额外的 FastAPI 路由/处理器。

## `LocalFilesystemPublisher(Publisher)`

本地文件系统存储实现。

### `get_target_dir(self, slug)`（上下文管理器）

**覆盖行为**：
1. `output_dir = output_dir_prefix / slug`
2. 如果目录已存在，`shutil.rmtree(output_dir)` 清理
3. `yield output_dir`（直接返回最终目录，零拷贝优化）

**与基类区别**：不使用临时目录，直接 yield 最终输出目录，避免构建后拷贝。

### `upload(self, source_dir, slug)`（异步）

**签名**：`async upload(self, source_dir, slug) -&gt; None`

**行为**：
- 写入空文件 `output_dir_prefix / slug / ".completed-sentinel"`
- 由于 `get_target_dir` 已返回最终目录，构建产物已直接写入目标位置，此方法只写哨兵文件

### `exists(self, slug)`（异步）

**签名**：`async exists(self, slug) -&gt; bool`

**行为**：返回 `(output_dir_prefix / slug / ".completed-sentinel").exists()`

### `get_redirect_url(self, slug)`

**签名**：`get_redirect_url(self, slug) -&gt; str`

**行为**：返回 `f"/render/{slug}/index.html"`

### `is_not_modified(self, response_headers, request_headers)`

**签名**：`is_not_modified(self, response_headers, request_headers) -&gt; bool`

**行为**：实现 HTTP 缓存协商：
1. 检查 `if-none-match` vs `etag`：匹配则返回 True
2. 检查 `if-modified-since` vs `last-modified`：请求时间 &gt;= 文件修改时间则返回 True
3. 都不匹配返回 False

**注意**：使用 `email.utils.parsedate` 解析HTTP日期。

### `serve_object(self, slug, path, request_headers)`（异步）

**签名**：`async serve_object(self, slug, path, request_headers) -&gt; FileResponse | NotModifiedResponse`

**行为**：
1. `file_path = output_dir_prefix / slug / path`
2. 如果 `file_path.is_dir()`，追加 `"index.html"`
3. 构造 `FileResponse(file_path, headers={"Cache-Control": "public, max-age=86400"})`
4. 如果 `is_not_modified` 返回 True，包装为 `NotModifiedResponse(resp.headers)`
5. 否则返回 FileResponse

### `mount_extra_handlers(self, app)`

**行为**：`app.mount("/render", StaticFiles(directory=output_dir_prefix), name="render")`

挂载 `/render` 路径到 output 目录，提供直接的静态文件访问。

## 哨兵文件机制

`.completed-sentinel` 是一个空文件，在构建成功完成后由 `upload()` 方法创建。`exists()` 检查此文件而非目录是否存在，确保构建的原子性——构建过程中目录可能存在但不完整。
