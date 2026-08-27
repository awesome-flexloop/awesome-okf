---
type: Concept
title: COS 对象存储
description: Demo Wall 的腾讯云 COS 对象存储配置，cos-nodejs-sdk-v5 初始化、服务端代理上传流程、临时密钥生成、文件类型校验、图片上传/删除 API。
tags: [demo-wall, cos, tencent-cloud, storage, upload]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: "/references/demo-wall-source.md"
    title: "Demo Wall 源码信源"
---

## COS SDK 配置

使用腾讯云 COS SDK（cos-nodejs-sdk-v5 ^2.15.4），配置位于 `src/lib/cos.ts`（F-009, F-099, F-130）：

- 实例：使用 `COS_SECRET_ID` 和 `COS_SECRET_KEY` 环境变量初始化
- 常量：`COS_BUCKET`（存储桶名称）、`COS_REGION`（地域）

## 服务端代理上传（F-131）

项目选择服务端代理上传而非前端直传 COS，虽然增加服务器带宽开销，但避免了密钥泄露风险和前端 CORS 配置复杂度。

### 上传流程

```
前端 FormData → POST /api/file → 服务端校验 → PUT 到 COS → 返回 URL
```

POST /api/file 处理逻辑（F-086, F-131）：

1. 获取登录用户（getAuthUser）
2. 从 FormData 提取文件（field name="file"）
3. **大小校验**：限制 5MB
4. **类型校验**：白名单 `image/jpeg`, `image/png`, `image/webp`, `image/gif`
5. 生成文件路径：`uploads/{YYYY-MM-DD}/{uuid}.{ext}`
6. 使用 `cos.putObject()` 上传到 COS
7. 返回 `{ success: true, url, path }`

返回的 URL 格式：`https://{BUCKET}.cos.{REGION}.myqcloud.com/{Key}`

### 删除流程（F-132）

DELETE /api/file 处理逻辑：

1. 获取登录用户
2. 接受 `{ path, url }` 参数
3. 从 path 或 url 解析 COS Key
4. 调用 `cos.deleteObject({ Bucket, Region, Key })` 删除

## 头像上传（F-087, F-133）

POST /api/avatar 专门处理头像上传：

- 大小限制：2MB
- 类型白名单：`image/jpeg`, `image/png`, `image/webp`, `image/svg+xml`
- 文件路径：`avatars/{userId}-{timestamp}.{ext}`
- 上传成功后自动更新 `SysUser.avatarUrl`

## 环境变量（F-136）

Docker 构建时通过 ARG 传入 COS 环境变量：
- `COS_SECRET_ID`
- `COS_SECRET_KEY`
- `COS_BUCKET`
- `COS_REGION`

开发环境在 `.env` 文件中配置。

## 安全注意事项

- COS 密钥必须通过环境变量注入，禁止硬编码
- 文件类型校验在服务端做（MIME type 检查），不能依赖前端校验
- 文件大小限制防止存储滥用
- 路径使用 UUID 命名避免文件名冲突和路径遍历攻击
- 服务端代理模式下 COS 密钥不暴露给前端

## 相关概念

- [作品提交流程](13-form-submission.md)
- [API 路由设计](06-api-routes.md)
- [富文本编辑器](08-rich-text-editor.md)
- [Docker 部署](15-docker-deployment.md)
- [COS 文件上传示例](../examples/cos-file-upload.md)
