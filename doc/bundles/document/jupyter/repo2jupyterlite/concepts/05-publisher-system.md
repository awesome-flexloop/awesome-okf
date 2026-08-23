---
type: Concept
title: Publisher 存储系统
description: Publisher 抽象基类接口设计、LocalFilesystemPublisher 的零拷贝优化、哨兵文件原子性、HTTP缓存协商和扩展接口
tags: [publisher, storage, filesystem, sentinel, cache-control, etag, plugin]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T16:00:00+08:00" }
verified: { by: "process:grep-api-verify", at: "2026-08-22T16:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: publisher-source
    resource: /references/publisher-source.md
    title: 发布器抽象信源
---

Publisher 是 BinderLite 中负责构建产物存储和服务的抽象层。它定义了一套统一的接口，使得存储后端可以插拔替换——本地文件系统、S3 对象存储、Google Cloud Storage 等都可以通过实现 Publisher 接口接入。

## Publisher 抽象基类

`Publisher` 类定义在 `binderlite/publish.py`，是所有发布器的抽象基类（F-086~F-091）。

### 接口方法

| 方法 | 类型 | 返回值 | 说明 |
|------|------|--------|------|
| `get_target_dir(slug)` | 上下文管理器 | 目录路径（str） | 返回构建产物的目标目录 |
| `exists(slug)` | async | bool | 检查 slug 的构建是否已完成 |
| `upload(source_dir, slug)` | async | None | 将构建产物上传/发布到存储 |
| `get_redirect_url(slug)` | async | str | 返回构建完成后的重定向 URL |
| `mount_extra_handlers(app)` | 普通 | None | 挂载额外的 FastAPI 路由 |

### get_target_dir 设计

基类使用**临时目录模式**（F-087）：

1. `tempfile.mktemp()` 生成一个唯一的临时目录路径（注意：mktemp 不创建目录，只生成路径名）
2. `yield tmpdirname` 将临时目录路径交给调用方（repo2jupyterlite CLI 在此目录中构建）
3. finally 块中 `shutil.rmtree(tmpdirname)` 清理临时目录

这是一种"构建→上传→清理"的模式：构建产物先写到临时目录，然后由 `upload()` 方法拷贝到最终存储位置，最后清理临时目录。

### 抽象方法约束

`exists()`、`upload()`、`get_redirect_url()` 在基类中抛出 `NotImplementedError`，子类必须实现。`mount_extra_handlers()` 默认为 `pass`（空操作），子类按需覆盖。

## LocalFilesystemPublisher

`LocalFilesystemPublisher(Publisher)` 是本地文件系统存储实现（F-092~F-099）。它在基类接口基础上做了重要优化——**零拷贝构建**。

### 零拷贝优化（直接输出）

与基类的"临时目录→拷贝"模式不同，LocalFilesystemPublisher 的 `get_target_dir()` 直接返回最终输出目录（F-093）：

```python
output_dir = output_dir_prefix / slug
if output_dir.exists():
    shutil.rmtree(output_dir)
yield output_dir
```

这意味着：
- repo2jupyterlite CLI 直接将文件构建到最终服务目录
- 不需要构建后再拷贝文件
- I/O 开销大幅降低（对于大型 JupyterLite 站点，构建产物可达数十MB）

这种优化是安全的，因为哨兵文件机制保证了不完整的构建不会被服务。

### upload() — 哨兵文件标记

由于构建直接输出到最终目录，`upload()` 方法不需要拷贝任何文件，只需要写入一个**哨兵文件**标记构建完成（F-094）：

```python
with open(output_dir_prefix / slug / ".completed-sentinel", "w") as f:
    f.write("")
```

写入空文件 `.completed-sentinel` 即表示构建完成。

### exists() — 原子性检查

`exists()` 不检查目录是否存在（目录在构建开始前就被创建了），而是检查哨兵文件是否存在（F-095）：

```python
return (output_dir_prefix / slug / ".completed-sentinel").exists()
```

这确保了构建的原子性：
- 构建进行中：目录存在但哨兵文件不存在 → `exists()` 返回 False → 新请求仍会等待/触发构建
- 构建完成：哨兵文件存在 → `exists()` 返回 True → 直接服务文件
- 构建失败：哨兵文件从未被写入 → `exists()` 返回 False → 后续请求重新触发构建

### serve_object() — HTTP 文件服务

`serve_object(slug, path, request_headers)` 负责通过 HTTP 服务已构建的静态文件（F-098）：

1. **路径解析**：`file_path = output_dir_prefix / slug / path`
2. **目录索引**：如果 `file_path.is_dir()`，自动追加 `index.html`
3. **FileResponse**：使用 Starlette 的 FileResponse 返回文件，设置 `Cache-Control: public, max-age=86400`（缓存1天）
4. **条件请求**：通过 `is_not_modified()` 检查缓存协商，命中时返回 `NotModifiedResponse`（HTTP 304）

### HTTP 缓存协商

`is_not_modified()` 方法实现了两种 HTTP 缓存验证机制（F-097）：

**ETag 验证**：
- 检查请求头 `If-None-Match` 是否等于响应头 `ETag`
- 匹配则返回 304 Not Modified

**Last-Modified 验证**：
- 解析请求头 `If-Modified-Since` 和响应头 `Last-Modified`
- 如果请求时间 &gt;= 文件修改时间，返回 304

Starlette 的 FileResponse 会自动计算 ETag（基于文件大小和修改时间）和设置 Last-Modified 头，`is_not_modified()` 只是基于这些头进行条件判断。

### mount_extra_handlers() — 静态文件挂载

LocalFilesystemPublisher 挂载了一个 StaticFiles 实例到 `/render` 路径（F-099）：

```python
app.mount("/render", StaticFiles(directory=output_dir_prefix), name="render")
```

这提供了对已构建文件的直接静态访问：`/render/gh-user/repo/sha/path/to/file`。与 `/v1/` 路由的动态构建逻辑不同，`/render/` 路径直接由 Starlette 的 StaticFiles 中间件服务，性能更高。

## Slug 与目录结构

所有构建产物存储在 `output/` 目录下（由 `output_dir_prefix = Path("output")` 指定，模块加载时自动创建 F-085）。

Slug 通过 `escapism.escape()` 编码（在 run.py 中），允许 `/` 字符以实现目录嵌套：

```
output/
└── gh-{user}/
    └── {repo}/
        └── {commit-sha}/
            ├── .completed-sentinel   # 构建完成标记
            ├── lab/
            │   └── index.html
            ├── pyodide/             # 或 xeus/
            ├── kernels/
            ├── content/
            ├── index.html
            └── ...
```

目录嵌套避免了单目录下文件过多导致的文件系统性能问题。

## 扩展 Publisher

要实现新的存储后端（如 S3、GCS），需要继承 `Publisher` 并实现以下方法：

```python
class S3Publisher(Publisher):
    @contextmanager
    def get_target_dir(self, slug):
        # 使用临时目录（基类模式）
        tmpdirname = tempfile.mktemp()
        try:
            yield tmpdirname
        finally:
            shutil.rmtree(tmpdirname)
    
    async def exists(self, slug):
        # 检查S3上是否存在哨兵文件
        ...
    
    async def upload(self, source_dir, slug):
        # 将source_dir中的文件上传到S3
        # 最后上传.completed-sentinel
        ...
    
    async def get_redirect_url(self, slug):
        # 返回S3/CDN的URL
        return f"https://cdn.example.com/{slug}/index.html"
    
    def mount_extra_handlers(self, app):
        # 可选：挂载反向代理路由到S3/CDN
        ...
```

### 实现要点

1. **哨兵文件仍然是必需的**：在 upload 完成所有文件上传后，最后上传哨兵文件，确保原子性
2. **get_target_dir 使用临时目录模式**：云存储无法像本地文件系统那样直接写入目标位置，需要先构建到临时目录再上传
3. **serve_object 需要适配**：云存储场景可能需要重定向到 CDN URL 或通过代理流式传输
4. **缓存头设置**：建议保留 `Cache-Control: public, max-age=86400` 以利用 CDN 缓存

## 相关概念

- [03-BinderLite Web应用](03-binderlite-web.md)
- [06-构建流程与缓存策略](06-build-process.md)
- [08-整体架构总结](08-architecture-summary.md)
