---
type: Example
title: 作品提交示例
description: 四步表单填写、图片上传到 COS、富文本编辑、标签选择、提交 API 调用的完整示例。
tags: [demo-wall, example, submit, work, form, upload]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: "/references/demo-wall-source.md"
    title: "Demo Wall 源码信源"
---

## 作品提交流程概览

作品提交需要登录，走四步向导。API 端点：POST /api/submit（F-079）。

## Step 1：填写基本信息

```typescript
const basicInfo = {
  title: "AI 智能助手 Demo",
  summary: "一个基于大模型的智能对话助手，支持多轮对话和上下文理解。",
  countryCode: "CN",
  cityCode: "beijing",
  categoryCode: "assistant",
  devStatusCode: "released",
  tags: [1, 3, 5], // 标签ID
  coverUrl: "https://bucket.cos.ap-guangzhou.myqcloud.com/uploads/2026-04-22/uuid-cover.webp"
};
```

## 图片上传到 COS

填写过程中需要上传封面和截图。调用 POST /api/file（F-086）：

```bash
curl -X POST http://localhost:3000/api/file \
  -H "Cookie: next-auth.session-token=<session>" \
  -F "file=@screenshot1.png"
```

响应：

```json
{
  "success": true,
  "url": "https://bucket.cos.region.myqcloud.com/uploads/2026-04-22/uuid.png",
  "path": "uploads/2026-04-22/uuid.png"
}
```

上传限制（F-086）：
- 文件大小：≤ 5MB
- 类型：image/jpeg、image/png、image/webp、image/gif
- 路径格式：uploads/{YYYY-MM-DD}/{uuid}.{ext}

## Step 2：上传视觉素材

上传 1-5 张截图，与封面使用相同的 /api/file 端点，保存返回的 URL 到 screenshots 数组。

```typescript
const screenshots = [
  "https://bucket.cos.region.myqcloud.com/uploads/2026-04-22/uuid1.png",
  "https://bucket.cos.region.myqcloud.com/uploads/2026-04-22/uuid2.png"
];
```

## Step 3：填写内容介绍

使用 Tiptap 富文本编辑器编辑 story 内容（F-104）：

```typescript
const content = {
  // story 是富文本 HTML，服务端会 sanitize
  story: "<p>这是一个<strong>智能对话助手</strong>，支持以下功能：</p><ul><li>多轮对话</li><li>上下文理解</li><li>知识库检索</li></ul>",
  highlights: ["多轮对话支持", "上下文记忆", "知识库RAG检索"],
  scenarios: ["客服场景", "个人助理", "教育辅导"],
  demoUrl: "https://demo.example.com/ai-assistant",
  repoUrl: "https://github.com/example/ai-assistant"
};
```

富文本白名单限制（F-104）：p/br/strong/em/u/s/h2/h3/ul/ol/li/a/blockquote/code，a 标签仅允许 http/https/mailto 协议。

## Step 4：填写团队信息

```typescript
const teamInfo = {
  team: ["张三", "李四", "王五"], // 至少1人
  teamIntro: "我们是一支专注于 AI 应用开发的团队，致力于打造实用的 AI 工具。",
  contactPhone: "13800138000",
  contactEmail: "team@example.com"
};
```

## 提交作品

合并所有步骤数据，POST 到 /api/submit：

```bash
curl -X POST http://localhost:3000/api/submit \
  -H "Content-Type: application/json" \
  -H "Cookie: next-auth.session-token=<session>" \
  -d '{
    "title": "AI 智能助手 Demo",
    "summary": "一个基于大模型的智能对话助手。",
    "countryCode": "CN",
    "cityCode": "beijing",
    "categoryCode": "assistant",
    "devStatusCode": "released",
    "tagIds": [1, 3, 5],
    "coverUrl": "https://bucket.cos.region.myqcloud.com/uploads/2026-04-22/uuid-cover.webp",
    "screenshots": [
      "https://bucket.cos.region.myqcloud.com/uploads/2026-04-22/uuid1.png"
    ],
    "story": "<p>这是一个<strong>智能对话助手</strong>...</p>",
    "highlights": ["多轮对话支持", "上下文记忆"],
    "scenarios": ["客服场景"],
    "demoUrl": "https://demo.example.com/ai-assistant",
    "repoUrl": "https://github.com/example/ai-assistant",
    "teamMembers": ["张三", "李四"],
    "teamIntro": "我们是AI应用开发团队。",
    "contactPhone": "13800138000",
    "contactEmail": "team@example.com"
  }'
```

### 服务端处理（F-079）

1. getAuthUser() 验证登录
2. zod 校验所有字段（F-105）
3. sanitizeRichText(story) 净化 HTML
4. prisma.$transaction() 内原子性创建：
   - WorkBase（核心信息）
   - WorkTagRelation（标签关联）
   - WorkDetail（富文本/链接）
   - WorkImage（截图，imageType=screenshot）
   - WorkTeam（团队信息）
   - WorkStatistic（auditStatus/displayStatus 初始值）
5. 自动审核判断：标签 isAutoAudit + 时间窗口内 → 自动通过
6. writeOperationLog() 记录

### 自动审核规则

如果选中的标签中存在 `isAutoAudit=true` 的标签，且当前时间在 `auditStartTime` ~ `auditEndTime` 范围内，则作品自动审核通过（auditStatus=1, displayStatus=1），否则进入待审核状态（auditStatus=0）。

## 提交后

- 待审核状态：作品仅作者和管理员可见
- 自动通过：作品立即在列表页展示
- 管理员审核后：通过则公开可见，拒绝则作者可查看原因并修改重新提交

## 相关内容

- [作品提交流程](../concepts/13-form-submission.md)
- [富文本编辑器](../concepts/08-rich-text-editor.md)
- [COS 对象存储](../concepts/09-cos-storage.md)
- [审核与治理](../concepts/10-audit-governance.md)
- [管理员审核示例](admin-review.md)
