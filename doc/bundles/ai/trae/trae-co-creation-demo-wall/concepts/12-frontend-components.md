---
type: Concept
title: 前端组件体系
description: Demo Wall 的 shadcn/ui 组件库、Radix UI primitives、CRUD 通用组件、WorkCard/EditForm 业务组件、ParticlesBackground 粒子动效。
tags: [demo-wall, components, shadcn, radix, tailwind, ui]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: "/references/demo-wall-source.md"
    title: "Demo Wall 源码信源"
---

## UI 框架栈（F-120）

- **Tailwind CSS**：darkMode: class，CSS 变量驱动主题
- **shadcn/ui**：components.json 配置 style=default, rsc=true, tsx=true, baseColor=zinc
- **Radix UI**：基础 primitives（Checkbox/Dialog/Label/Select/Separator/Slot）
- **lucide-react**：图标库
- **sonner**：Toast 通知
- **class-variance-authority + tailwind-merge + clsx**：样式组合工具

## 自定义 Tailwind 主题（F-121）

品牌绿色板：
- green-300: #9DF7C6
- green-400: #32F08C
- green-500: #1FDB79
- green-600: #14B368

CSS 变量驱动的主题色：border/input/ring/background/foreground/primary/secondary/destructive/muted/accent/popover/card/sidebar/chart，支持暗色模式。

## 组件目录结构（F-021, F-122）

### ui/ — 基础 UI 组件（shadcn/ui）

| 组件 | 说明 |
|------|------|
| badge.tsx | 徽章 |
| button.tsx | 按钮（变体：default/destructive/secondary/ghost/link） |
| card.tsx | 卡片 |
| checkbox.tsx | 复选框（Radix Checkbox） |
| date-picker.tsx | 日期选择器 |
| dialog.tsx | 对话框（Radix Dialog） |
| dotted-glow-background.tsx | 装饰性点状光晕背景 |
| input.tsx | 输入框 |
| label.tsx | 标签（Radix Label） |
| select.tsx | 选择器（Radix Select） |
| textarea.tsx | 文本域 |

### common/ — 通用组件

| 组件 | 说明 |
|------|------|
| query-provider.tsx | React QueryClientProvider 封装 |
| action-button.tsx | 通用操作按钮（loading状态） |
| form-select.tsx | 表单选择组件 |
| hero-banner.tsx | 首页 Hero Banner |
| loading-overlay.tsx | 加载状态遮罩 |

### crud/ — CRUD 通用组件

| 组件 | 说明 |
|------|------|
| crud-feedback.tsx | CRUD 操作反馈提示 |
| crud-filter-bar.tsx | 通用筛选栏 |
| crud-pagination.tsx | 通用分页组件 |

这些 CRUD 组件抽象了列表页的通用 UI 模式，减少重复代码。

### layout/ — 布局组件

| 组件 | 说明 |
|------|------|
| site-layout.tsx | 站点整体布局（导航/内容区/页脚） |
| particles-background.tsx | @tsparticles/react 粒子动效背景（F-123） |

### auth/ — 认证组件

| 组件 | 说明 |
|------|------|
| sign-in-form.tsx | 登录表单 |
| sign-up-form.tsx | 注册表单 |

### work/ — 作品业务组件

| 组件 | 说明 |
|------|------|
| work-card.tsx | 作品卡片展示组件（列表页） |
| edit-form.tsx | 作品编辑表单 |
| city-filter.tsx | 城市筛选组件 |
| liked-works.tsx | 用户点赞/收藏作品列表 |
| works-management.tsx | 管理后台作品管理（审核操作） |

## 工具函数（F-101）

`src/lib/utils.ts` 导出 `cn()` 函数，组合 clsx 和 tailwind-merge，用于条件式 className 合并：

```typescript
import { cn } from '@/lib/utils';
<div className={cn('base-class', isActive && 'active-class', className)} />
```

## 相关概念

- [架构总览](02-architecture-overview.md)
- [CRUD 数据层](07-crud-layer.md)
- [作品提交流程](13-form-submission.md)
