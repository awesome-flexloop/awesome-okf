---
type: Concept
title: 国际化路由
description: Demo Wall 的 next-intl 国际化方案，[language] 动态段、三层中间件链、翻译文件结构。
tags: [demo-wall, i18n, next-intl, routing, middleware]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: "/references/demo-wall-source.md"
    title: "Demo Wall 源码信源"
---

## next-intl 方案

采用 next-intl 的 [language] 动态路由段，URL 结构 /{locale}/...，所有页面路由嵌套在 src/app/[language]/ 下（F-016~F-017）。支持 zh-CN（默认）、en-US、ja-JP 三种语言（F-126）。

## language/ 三件套（F-110~F-112）

- **routing.ts**：locales=['zh-CN','en-US','ja-JP']，defaultLocale='zh-CN'
- **request.ts**：getRequestConfig 动态 import 翻译文件
- **navigation.ts**：createNavigation(routing) 生成 Link/redirect/usePathname/useRouter/getPathname

## 翻译文件

位于 src/assets/translations/，包含 zh-CN.json、en-US.json、ja-JP.json（F-127）。

## 双层 Layout（F-117~F-118）

- 根 layout.tsx：空壳，仅返回 children
- [language]/layout.tsx：渲染 html lang={locale}，加载 Inter/Noto_Sans_SC/JetBrains_Mono 字体；Provider 嵌套 SessionProvider → QueryProvider → NextIntlClientProvider → SiteLayout

## 三层中间件链（F-113~F-116）

1. /api/auth 直接放行
2. isProtectedRoute 正则 /^\/(zh-CN|en-US|ja-JP)\/(submit|console|profile)/ 未登录重定向到 /{lang}/sign-in
3. /api/* 跳过 i18n 中间件
4. 其余路径交给 next-intl createMiddleware 处理

Matcher 跳过 _next 和静态文件，始终匹配 /api 和 /trpc。

## labelI18n 字典多语言（F-129）

SysDictItem 的 labelI18n 字段存储 JSON 多语言标签，API 根据 lang 参数选择，fallback 到 itemLabel。sortFilterOptions 先按 sortOrder 再按 localeCompare 排序（F-078）。

## 相关概念

- [认证系统](/concepts/04-auth-system.md)
- [架构总览](/concepts/02-architecture-overview.md)
- [字典系统](/concepts/11-dictionary-system.md)
- [API 路由设计](/concepts/06-api-routes.md)
