---
type: Concept
title: 作品提交流程
description: Demo Wall 的四步作品提交流程：StepIndicator 向导、Step1BasicInfo-Step4Team 步骤组件、react-hook-form+zod 校验、草稿保存。
tags: [demo-wall, form, submission, wizard, react-hook-form, zod]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: "/references/demo-wall-source.md"
    title: "Demo Wall 源码信源"
---

## 四步提交流程

作品提交采用四步向导（Wizard）模式，文件位于 `src/app/[language]/submit/`（F-019）：

```
Step1 基本信息 → Step2 视觉素材 → Step3 内容介绍 → Step4 团队信息 → 提交
```

## 提交目录文件结构（F-019）

| 文件 | 说明 |
|------|------|
| page.tsx | 提交页面入口 |
| submission-form.tsx | 四步表单容器（状态管理、步骤切换、提交逻辑） |
| editor/RichTextEditor.tsx | Tiptap 富文本编辑器组件 |
| steps/StepIndicator.tsx | 步骤指示器（显示当前步骤） |
| steps/Step1BasicInfo.tsx | 步骤1：基本信息 |
| steps/Step2VisualAssets.tsx | 步骤2：视觉素材（截图上传） |
| steps/Step3Content.tsx | 步骤3：内容介绍（富文本/highlights/scenarios/链接） |
| steps/Step4Team.tsx | 步骤4：团队信息（成员/介绍/联系方式） |

## 各步骤收集的数据

### Step1 — 基本信息

- title（作品名称）：2-50 字符
- summary（简介）：10-100 字符
- countryCode/cityCode（国家/城市）：字典选择，必填
- categoryCode（分类）：字典选择，必填
- devStatusCode（开发状态）：字典选择，必填
- tags（标签）：1-5 个标签选择
- coverUrl（封面图）：必填，通过 /api/file 上传到 COS

### Step2 — 视觉素材

- screenshots（截图）：1-5 张图片上传到 COS（imageType=screenshot）

### Step3 — 内容介绍

- story（作品故事）：富文本编辑，纯文本 20-2000 字符（HTML 经 stripHtmlTags 后计算长度）
- highlights（亮点）：1-5 个，每个 1-30 字符
- scenarios（应用场景）：至少 1 个，每个 1-100 字符
- demoUrl（Demo链接）：合法 URL 或空
- repoUrl（代码仓库）：合法 URL 或空

### Step4 — 团队信息

- team（团队成员）：至少 1 人，每人 1-20 字符（JSON 数组）
- teamIntro（团队介绍）：1-500 字符
- contactPhone（联系电话）：最多 20 字符
- contactEmail（联系邮箱）：合法邮箱或空

## 表单技术栈

- **react-hook-form**（^7.71.2）：表单状态管理（F-008）
- **zod**（^4.3.6）：通过 @hookform/resolvers 集成 schema 校验（F-008, F-010）
- **buildWorkFormSchema(t, options)**：动态构建 zod schema，支持 requireTeamIntro 选项（F-105）

## 提交 API 处理（F-079）

POST /api/submit 服务端处理：

1. getAuthUser() 验证登录
2. zod updateSchema 校验输入
3. sanitizeRichText() 清理 story HTML
4. 事务内创建：WorkBase → WorkTagRelation → WorkDetail → WorkImage(screenshot) → WorkTeam → WorkStatistic
5. 自动审核判断：检查标签 isAutoAudit + 时间窗口
   - 命中：auditStatus=1, displayStatus=1，写 WorkAuditLog
   - 未命中：auditStatus=0, displayStatus=0
6. writeOperationLog() 记录操作日志
7. 返回结果

作品更新（PUT /api/works）采用类似模式，但重建关联时使用"删后重建"策略（F-071）。

## 相关概念

- [富文本编辑器](/concepts/08-rich-text-editor.md)
- [COS 对象存储](/concepts/09-cos-storage.md)
- [CRUD 数据层](/concepts/07-crud-layer.md)
- [API 路由设计](/concepts/06-api-routes.md)
- [审核与治理](/concepts/10-audit-governance.md)
- [作品提交示例](/examples/submit-work.md)
