---
type: Concept
title: pack 与 upload
description: papyri pack 将 DocBundle 打包为 .papyri 制品，papyri upload 通过 HTTP PUT 上传到 viewer 的摄取端点
tags: [papyri, pack, upload, cbor, artifact, http]
generated: { by: reference_agent/trae-soLO, at: "2026-08-22T00:00:00Z" }
verified: { by: "process:grep-api-check", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: papyri-src
    resource: /references/papyri-source.md
    title: Papyri Python 核心包源码信源
  - id: cli-src
    resource: /references/cli-source.md
    title: Papyri CLI 命令源码信源
---

## pack：打包为 .papyri 制品

`papyri pack` 将 gen 输出的 JSON DocBundle 目录打包为单个 `.papyri` 制品文件。

### 打包过程

`pack.py` 中的 `make_artifact_from_dir()` 执行以下步骤：

1. **读取 papyri.json**：解析 BundleManifest 元数据
2. **读取 toc.json**：读取目录树（如果存在）
3. **遍历 module/ 目录**：读取每个 API 对象的 JSON 文件，反序列化为 GeneratedDoc
4. **遍历 docs/ 目录**：读取叙述性文档
5. **遍历 examples/ 目录**：读取示例 Section
6. **遍历 assets/ 目录**：读取二进制资源为 bytes
7. **组装 Bundle Node**：将所有数据组装为 Bundle 节点
8. **CBOR 编码**：使用 `encoder.encode()` 进行 canonical CBOR 编码（RFC 8949 §4.2，map key 排序）
9. **Gzip 压缩**：使用 zero-mtime header 压缩（确保可重现构建）
10. **输出文件**：写入 `<module>-<version>.papyri`

### 确定性保证

同一输入目录两次运行 `make_artifact_from_dir()` 必须产生字节完全相同的输出。这通过以下机制实现：

- **canonical CBOR**：`cbor2.dumps(obj, canonical=True)` 确保 map key 排序
- **字段位置编码**：Node 字段编码为 CBOR 数组（非 map），属性顺序由类定义固定
- **zero-mtime gzip**：gzip 头中的 mtime 设为 0
- **字典顺序控制**：GeneratedDoc 的 `_content` 字典通过 `_OrderedDictProxy` 维护顺序，`_ordered_sections` 单独记录顺序

这一特性使得 `.papyri` 制品适用于内容寻址、签名和镜像。

### 安全性：路径遍历防护

`pack.py` 中的 `_safe_child(base, name)` 函数在解包时拒绝路径遍历攻击：

```python
def _safe_child(base: Path, name: str) -> Path:
    base_resolved = base.resolve()
    child = (base / name).resolve()
    if not child.is_relative_to(base_resolved):
        raise BundleError(f"unsafe path in bundle: {name!r}")
    return child
```

### 安全性：URL 安全校验

`_is_safe_url(url)` 函数在打包时验证 Link/Image 节点的 URL：

- 只允许 `http`/`https`/`mailto` 协议和相对 URL
- 阻止 `javascript:`/`data:` 等 XSS 向量
- 先剥离控制字符和空白字符，防止 `java\tscript:` 类走私

### unpack：解包

`papyri unpack` 是 pack 的逆操作：

1. 读取 `.papyri` 文件
2. gzip 解压
3. CBOR 解码为 Bundle Node
4. 写入 JSON DocBundle 目录（用于检查和调试）

## upload：上传到 Viewer

`papyri upload` 将 DocBundle 发送到 viewer 实例进行摄取。

### 上传协议

- **HTTP 方法**：PUT（不是 POST）
- **端点**：`/api/bundle`（默认 `http://localhost:4321/api/bundle`）
- **认证**：Bearer token（`Authorization: Bearer <token>`）
- **User-Agent**：`papyri-upload/<version>`（非默认 `Python-urllib/3.x`，避免被反向代理/WAF 拒绝）
- **Origin 头**：设置为上传主机名（防御性设置，Astro 的 `checkOrigin` 已禁用）

### 支持的输入格式

upload 命令接受三种输入：

1. **DocBundle 目录**：自动先打包再上传
2. **`.papyri` 文件**：直接上传
3. **包含 `.papyri` 的 `.zip` 文件**：解压后上传

### 环境变量

| 变量 | 说明 |
|------|------|
| `PAPYRI_UPLOAD_URL` | 覆盖默认端点 URL |
| `PAPYRI_UPLOAD_TOKEN` | 设置认证 token |

也可以通过 `--url` 和 `--token` 命令行选项指定。

### gen --pack / gen --upload

`papyri gen` 提供 `--pack` 和 `--upload` 标志，在生成完成后自动执行打包或上传：

```bash
# 生成并打包
papyri gen examples/papyri.toml --pack

# 生成并上传
papyri gen examples/papyri.toml --upload

# 生成、打包并上传
papyri gen examples/papyri.toml --pack --upload
```

## 相关概念

- [IR 与 DocBundle](03-ir-and-docbundle.md)
- [gen 管线](05-gen-pipeline.md)
- [GraphStore 与交叉链接](09-graphstore-and-crosslinks.md)
- [TypeScript 摄取与渲染器](12-ingest-and-viewer.md)
