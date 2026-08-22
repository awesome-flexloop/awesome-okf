---
type: Example
title: "Pack 与 Upload 工作流"
description: "将 DocBundle 打包为 .papyri 制品、解包检查、上传到本地或远程 viewer 实例的完整流程"
tags: [pack, upload, artifact, cbor, viewer, deploy]
generated: { by: "reference_agent/trae-soLO", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: papyri-src
    resource: "/references/papyri-source.md"
    title: "Papyri Python 核心包源码信源"
  - id: cli-src
    resource: "/references/cli-source.md"
    title: "Papyri CLI 命令源码信源"
  - id: viewer-src
    resource: "/references/viewer-source.md"
    title: "Papyri TypeScript 摄取器与查看器源码信源"
---

# Pack 与 Upload 工作流

本示例演示从 gen 输出到 viewer 部署的完整打包和上传流程。

## 示例1：gen + pack 一步完成

使用 `--pack` 标志在 gen 完成后自动打包：

```bash
papyri gen my-papyri.toml --pack
```

这等价于：

```bash
papyri gen my-papyri.toml
papyri pack ~/.papyri/data/papyri_<version>/
```

输出文件 `<module>-<version>.papyri` 生成在当前目录。

## 示例2：手动打包到指定路径

```bash
# 打包到指定输出文件
papyri pack ~/.papyri/data/papyri_0.1.0/ -o dist/papyri-0.1.0.papyri

# 验证文件存在和大小
ls -lh dist/papyri-0.1.0.papyri
```

## 示例3：解包检查

```bash
# 解包到临时目录
papyri unpack dist/papyri-0.1.0.papyri /tmp/papyri-bundle/

# 检查解包结果
ls /tmp/papyri-bundle/
# papyri.json  module/  docs/  examples/  assets/

# 对比原始 gen 输出和解包结果（确定性验证）
diff -r ~/.papyri/data/papyri_0.1.0/ /tmp/papyri-bundle/
# 应该无差异（确定性打包保证）
```

## 示例4：上传到本地 viewer

启动 viewer 后上传 DocBundle：

```bash
# 终端1：启动 viewer（开发模式）
cd papyri/ts
pnpm install
pnpm dev
# Viewer 运行在 http://localhost:4321

# 终端2：上传
papyri upload ~/.papyri/data/papyri_0.1.0/
```

## 示例5：上传到远程 viewer

使用 `--url` 和 `--token` 上传到远程部署：

```bash
# 设置环境变量（也可以直接用命令行选项）
export PAPYRI_UPLOAD_URL="https://docs.example.com/api/bundle"
export PAPYRI_UPLOAD_TOKEN="my-secret-token"

# 上传目录
papyri upload ~/.papyri/data/papyri_0.1.0/

# 或者上传 .papyri 文件
papyri upload dist/papyri-0.1.0.papyri --url https://docs.example.com/api/bundle --token my-secret-token
```

## 示例6：gen + pack + upload 一条龙

```bash
papyri gen my-papyri.toml --pack --upload
```

CI 部署场景：

```bash
#!/bin/bash
set -euo pipefail

# 生成文档（严格模式）
papyri gen my-package.toml --fail --fail-unseen-error --exec --pack

# 上传到文档服务器
papyri upload my-package-*.papyri \
    --url "$PAPYRI_UPLOAD_URL" \
    --token "$PAPYRI_UPLOAD_TOKEN"
```

## 示例7：上传 zip 中的 .papyri

upload 也支持包含 `.papyri` 文件的 zip 压缩包：

```bash
# 将 .papyri 文件压缩
zip papyri-bundle.zip dist/papyri-0.1.0.papyri

# 上传 zip
papyri upload papyri-bundle.zip
```

## 关键点总结

1. **pack 是确定性的**：相同输入两次打包产生字节相同的 `.papyri` 文件（canonical CBOR + zero-mtime gzip）
2. **.papyri 是 CBOR+gzip**：不是 JSON，不能直接文本编辑器查看，需要 unpack
3. **unpack 有路径遍历防护**：`_safe_child()` 拒绝 `../` 路径
4. **upload 使用 PUT 方法**：端点是 `/api/bundle`，默认 `http://localhost:4321`
5. **upload 支持三种输入**：目录（自动打包）、`.papyri` 文件、包含 `.papyri` 的 `.zip`
6. **认证用 Bearer token**：通过 `PAPYRI_UPLOAD_TOKEN` 或 `--token` 设置
7. **--pack 和 --upload 可以组合**：`--pack --upload` 一步完成生成到部署

## 相关示例

- [基础 gen 工作流](01-basic-gen.md)
- [自定义 TOML 配置](02-custom-config.md)
