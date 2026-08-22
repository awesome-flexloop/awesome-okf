---
type: Example
title: COS 文件上传示例
description: 腾讯云 COS 文件上传流程：获取签名/服务端代理上传、前端直传流程、文件删除、图片类型和大小限制。
tags: [demo-wall, example, cos, upload, file, storage]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: "/references/demo-wall-source.md"
    title: "Demo Wall 源码信源"
---

## COS 配置

确保环境变量已配置（F-099, F-130）：

```env
COS_SECRET_ID=your-secret-id
COS_SECRET_KEY=your-secret-key
COS_BUCKET=your-bucket-name
COS_REGION=ap-guangzhou
```

COS SDK 在 `src/lib/cos.ts` 中初始化，导出 cos 实例、COS_BUCKET、COS_REGION 常量。

## 上传作品图片

作品截图和封面图通过 POST /api/file 上传（F-086, F-131）：

### 前端上传示例

```tsx
'use client';

async function uploadImage(file: File): Promise<{ url: string; path: string }> {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch('/api/file', {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.error || '上传失败');
  }

  return res.json();
}
```

### 使用示例

```tsx
const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
  const file = e.target.files?.[0];
  if (!file) return;

  // 前端大小预校验（服务端也会校验）
  if (file.size > 5 * 1024 * 1024) {
    alert('文件大小不能超过 5MB');
    return;
  }

  // 前端类型预校验
  if (!['image/jpeg', 'image/png', 'image/webp', 'image/gif'].includes(file.type)) {
    alert('只支持 JPG/PNG/WebP/GIF 格式');
    return;
  }

  try {
    const { url, path } = await uploadImage(file);
    console.log('上传成功:', url);
    // 保存 url 到表单数据
  } catch (err) {
    console.error('上传失败:', err);
  }
};
```

### 服务端处理流程

POST /api/file（F-086）：

1. getAuthUser() 验证登录
2. 从 FormData 提取文件
3. 校验文件大小 ≤ 5MB
4. 校验 MIME 类型在白名单（image/jpeg, image/png, image/webp, image/gif）
5. 生成文件路径：`uploads/{YYYY-MM-DD}/{uuid}.{ext}`
   - uuid 防止文件名冲突
   - 按日期分目录便于管理
6. 使用 cos.putObject() 上传到腾讯云 COS
7. 返回公开 URL：`https://{BUCKET}.cos.{REGION}.myqcloud.com/{Key}`

返回格式：

```json
{
  "success": true,
  "url": "https://bucket.cos.ap-guangzhou.myqcloud.com/uploads/2026-04-22/a1b2c3d4.webp",
  "path": "uploads/2026-04-22/a1b2c3d4.webp"
}
```

## 上传头像

头像使用专用端点 POST /api/avatar（F-087, F-133）：

```tsx
async function uploadAvatar(file: File) {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch('/api/avatar', {
    method: 'POST',
    body: formData,
  });

  const data = await res.json();
  // 上传成功后自动更新 SysUser.avatarUrl
  // data.url 为新头像 URL
}
```

头像限制：
- 文件大小 ≤ 2MB
- 类型：image/jpeg, image/png, image/webp, image/svg+xml
- 路径：`avatars/{userId}-{timestamp}.{ext}`
- 上传成功后自动更新用户 avatarUrl，无需额外 API 调用

## 删除文件

DELETE /api/file 删除 COS 上的文件（F-086, F-132）：

```tsx
async function deleteFile(path: string, url: string) {
  await fetch('/api/file', {
    method: 'DELETE',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ path, url }),
  });
}
```

服务端从 path 或 url 参数解析 COS Key，调用 cos.deleteObject() 删除。可以只传 path 或只传 url，服务端会自动解析。

## 文件类型与大小限制汇总

| 端点 | 大小限制 | 允许类型 | 路径格式 | 自动更新 |
|------|---------|---------|---------|---------|
| POST /api/file | 5MB | jpg/png/webp/gif | uploads/{date}/{uuid}.{ext} | 否 |
| POST /api/avatar | 2MB | jpg/png/webp/svg | avatars/{userId}-{timestamp}.{ext} | 是（avatarUrl） |

## 安全注意事项

- 服务端代理上传而非前端直传，COS 密钥不暴露给浏览器
- 文件类型和大小在服务端校验（前端校验仅为用户体验优化）
- 文件路径使用 UUID 命名，防止路径遍历和文件名冲突
- COS 密钥通过环境变量注入，不硬编码
- a 标签协议白名单防止 XSS（见富文本安全章节）

## 相关内容

- [COS 对象存储](/concepts/09-cos-storage.md)
- [作品提交流程](/concepts/13-form-submission.md)
- [作品提交示例](/examples/submit-work.md)
- [富文本编辑器](/concepts/08-rich-text-editor.md)
