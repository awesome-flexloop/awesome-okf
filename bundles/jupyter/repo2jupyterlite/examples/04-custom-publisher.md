---
type: Example
title: 自定义 Publisher 示例
description: 实现S3云存储Publisher的完整示例，包括临时目录构建、文件上传、哨兵文件原子性和重定向URL
tags: [custom-publisher, s3, cloud-storage, extension, storage-backend]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T16:00:00+08:00" }
verified: { by: "process:grep-api-verify", at: "2026-08-22T16:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: publisher-source
    resource: /references/publisher-source.md
    title: 发布器抽象信源
---

本示例演示如何实现一个基于 Amazon S3（或兼容 S3 协议的对象存储如 MinIO）的自定义 Publisher，支持将构建产物上传到云存储并通过 CDN 服务。

## Publisher 接口回顾

根据 [Publisher信源](/references/publisher-source.md)，需要实现的方法：

| 方法 | 类型 | 返回值 | 说明 |
|------|------|--------|------|
| `get_target_dir(slug)` | @contextmanager | 目录路径 | 返回临时构建目录 |
| `exists(slug)` | async | bool | 检查哨兵文件是否存在 |
| `upload(source_dir, slug)` | async | None | 上传构建产物到S3 |
| `get_redirect_url(slug)` | async | str | 返回CDN URL |
| `mount_extra_handlers(app)` | sync | None | 可选：挂载代理路由 |

## 实现 S3Publisher

```python
import os
import shutil
import tempfile
from contextlib import contextmanager
from pathlib import Path

import boto3
from botocore.config import Config
from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.responses import Response

from binderlite.publish import Publisher


class S3Publisher(Publisher):
    """将构建产物上传到S3并通过CDN重定向服务的Publisher"""

    def __init__(
        self,
        bucket: str,
        cdn_base_url: str | None = None,
        region: str = "us-east-1",
        prefix: str = "binderlite/",
    ):
        """
        参数:
            bucket: S3存储桶名称
            cdn_base_url: CDN基础URL（如 https://cdn.example.com），None则直接使用S3 URL
            region: AWS区域
            prefix: S3 key前缀
        """
        self.bucket = bucket
        self.cdn_base_url = cdn_base_url
        self.prefix = prefix
        self.s3 = boto3.client(
            "s3",
            region_name=region,
            config=Config(signature_version="s3v4"),
        )

    def _s3_key(self, slug: str, filename: str = "") -&gt; str:
        """构造S3 key"""
        return f"{self.prefix}{slug}/{filename}" if filename else f"{self.prefix}{slug}"

    @contextmanager
    def get_target_dir(self, slug):
        """使用临时目录（不能直接写入S3，需要先构建到本地临时目录）"""
        tmpdirname = tempfile.mktemp()
        try:
            yield tmpdirname
        finally:
            # 上传完成或失败后都清理临时目录
            if os.path.exists(tmpdirname):
                shutil.rmtree(tmpdirname)

    async def exists(self, slug):
        """检查S3上是否存在哨兵文件"""
        try:
            self.s3.head_object(
                Bucket=self.bucket,
                Key=self._s3_key(slug, ".completed-sentinel"),
            )
            return True
        except Exception:
            # head_object失败（404等）表示不存在
            return False

    async def upload(self, source_dir, slug):
        """将source_dir中的所有文件上传到S3，最后上传哨兵文件"""
        source_path = Path(source_dir)

        # 第一步：上传所有构建文件
        for file_path in source_path.rglob("*"):
            if not file_path.is_file():
                continue

            # 计算相对路径作为S3 key的一部分
            relative_path = file_path.relative_to(source_path)
            s3_key = self._s3_key(slug, str(relative_path))

            # 根据文件扩展名设置Content-Type
            extra_args = {}
            suffix = file_path.suffix.lower()
            content_types = {
                ".html": "text/html",
                ".js": "application/javascript",
                ".css": "text/css",
                ".json": "application/json",
                ".wasm": "application/wasm",
                ".svg": "image/svg+xml",
                ".png": "image/png",
                ".ico": "image/x-icon",
            }
            if suffix in content_types:
                extra_args["ContentType"] = content_types[suffix]

            # 设置缓存策略：HTML不缓存（短TTL），静态资源长缓存
            if suffix == ".html":
                extra_args["CacheControl"] = "public, max-age=300"
            else:
                extra_args["CacheControl"] = "public, max-age=86400, immutable"

            self.s3.upload_file(
                str(file_path),
                self.bucket,
                s3_key,
                ExtraArgs=extra_args,
            )

        # 第二步：最后上传哨兵文件（原子性标记）
        # 使用put_object直接创建空文件
        self.s3.put_object(
            Bucket=self.bucket,
            Key=self._s3_key(slug, ".completed-sentinel"),
            Body=b"",
            ContentType="application/octet-stream",
        )

    async def get_redirect_url(self, slug, path: str = "index.html"):
        """返回CDN/S3上的URL"""
        if self.cdn_base_url:
            base = self.cdn_base_url.rstrip("/")
            return f"{base}/{self._s3_key(slug, path)}"
        else:
            # 使用S3预签名URL或直接公共URL
            location = self.s3.get_bucket_location(
                Bucket=self.bucket
            )["LocationConstraint"]
            return f"https://{self.bucket}.s3.{location}.amazonaws.com/{self._s3_key(slug, path)}"

    async def serve_object(self, slug, path, request_headers):
        """重定向到CDN/S3 URL（不代理传输）"""
        # 处理目录路径
        if not path or path.endswith("/"):
            path = path + "index.html" if path else "index.html"

        url = await self.get_redirect_url(slug, path)
        return RedirectResponse(url=url, status_code=302)

    def mount_extra_handlers(self, app):
        """不需要额外挂载，所有请求通过/v1/路由重定向到CDN"""
        pass
```

## 使用 S3Publisher

修改 `binderlite/run.py` 使用 S3Publisher：

```python
import os
from binderlite.publish import LocalFilesystemPublisher
from mymodule import S3Publisher

# 根据环境变量选择publisher
if os.getenv("PUBLISHER_BACKEND") == "s3":
    publisher = S3Publisher(
        bucket=os.getenv("S3_BUCKET", "my-binderlite-builds"),
        cdn_base_url=os.getenv("CDN_BASE_URL"),
        region=os.getenv("AWS_REGION", "us-east-1"),
        prefix=os.getenv("S3_PREFIX", "binderlite/"),
    )
else:
    publisher = LocalFilesystemPublisher()

publisher.mount_extra_handlers(app)
```

## 关键设计要点

### 1. 临时目录模式

与 LocalFilesystemPublisher 的零拷贝优化不同，S3Publisher 必须使用**临时目录模式**（基类模式），因为：
- S3 不是文件系统，无法直接让 repo2jupyterlite 将文件写入S3
- 必须先在本地临时目录构建，然后上传到S3
- `finally` 块确保临时目录被清理

### 2. 哨兵文件的原子性

哨兵文件 `.completed-sentinel` **必须最后上传**：

```python
# 先上传所有文件...
# 最后上传哨兵文件
self.s3.put_object(..., Key=...completed-sentinel, Body=b"")
```

这确保了：
- 如果上传过程中断（网络错误、进程崩溃），哨兵文件不存在
- `exists()` 检查返回 False，下次请求重新构建
- 所有文件上传完成后才设置哨兵，用户不会访问到不完整的站点

### 3. Content-Type 和缓存策略

S3 上传时设置正确的 Content-Type 很重要：
- `.html`：`text/html`，短缓存（5分钟）以支持更新
- `.js`/`.css`/`.wasm`：长缓存（1天 + immutable），配合构建时hash文件名
- `.json`：`application/json`
- `.svg`/`.png`：对应图片MIME类型

### 4. 重定向 vs 代理

`serve_object()` 使用 **302重定向** 到CDN URL 而非代理传输：
- 优点：减轻应用服务器负载，CDN直接服务文件
- 缺点：URL跳转到CDN域名（用户可见）
- 替代方案：使用 `StreamingResponse` 代理S3文件（服务器带宽消耗大但URL不跳转）

### 5. 生产环境改进

```python
# 添加S3传输配置以支持大文件
from boto3.s3.transfer import TransferConfig

transfer_config = TransferConfig(
    multipart_threshold=8 * 1024 * 1024,  # 8MB分段
    max_concurrency=10,
    use_threads=True,
)

# 上传时使用transfer_config
self.s3.upload_file(..., Config=transfer_config)
```

## 部署配置

```bash
# 环境变量配置
export PUBLISHER_BACKEND=s3
export S3_BUCKET=my-binderlite-builds
export CDN_BASE_URL=https://cdn.example.com/binderlite
export AWS_REGION=us-east-1
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
```

S3 Bucket 策略需要允许公共读取（构建产物）：

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::my-binderlite-builds/binderlite/*"
    }
  ]
}
```

## 相关概念

- [05-Publisher存储系统](/concepts/05-publisher-system.md)
- [03-BinderLite Web应用](/concepts/03-binderlite-web.md)
- [08-整体架构总结](/concepts/08-architecture-summary.md#扩展点)
