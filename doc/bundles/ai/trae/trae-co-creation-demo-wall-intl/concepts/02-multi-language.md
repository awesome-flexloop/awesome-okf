---
type: Concept
title: 5语言国际化
description: intl版支持5种语言（en-US/zh-CN/ja-JP/id-ID/vi-VN），默认语言从zh-CN切换为en-US，覆盖东南亚市场。middleware.ts中isProtectedRoute正则遗漏id-ID/vi-VN是已知Bug，需从routing.locales动态生成正则修复。
tags: [demo-wall, intl, i18n, next-intl, multi-language, middleware, bug]
generated: { by: "reference_agent/trae-cn", at: 2026-04-22T00:00:00+08:00 }
verified: { by: "process:grep-verification", at: 2026-04-22T00:00:00+08:00 }
status: stable
stale_after: 2026-10-22
sources:
  - id: src
    resource: /references/demo-wall-intl-source.md
    title: Demo Wall Intl 源码信源索引
---

## 语言配置

国际版将支持语言从中文版的3种扩展到5种，默认语言从中文切换为英语：

| 配置项 | 中文版 | 国际版 |
|--------|--------|--------|
| locales | `['zh-CN', 'en-US', 'ja-JP']` | `['en-US', 'zh-CN', 'ja-JP', 'id-ID', 'vi-VN']` |
| defaultLocale | `'zh-CN'` | `'en-US'` |
| 翻译文件数 | 3个 | 5个 |
| URL 结构 | `/{locale}/...` | `/{locale}/...`（相同） |

配置位于 `src/lib/language/routing.ts`：

```typescript
export const routing = {
  locales: ['en-US', 'zh-CN', 'ja-JP', 'id-ID', 'vi-VN'],
  defaultLocale: 'en-US',
  localePrefix: 'always'  // URL 始终包含语言前缀
} as const;
```

## 5种语言覆盖

| 语言代码 | 语言 | 覆盖市场 | 翻译文件 |
|---------|------|---------|---------|
| en-US | 英语（美国） | 全球通用，默认语言 | en-US.json |
| zh-CN | 简体中文 | 中国及海外华人 | zh-CN.json |
| ja-JP | 日语 | 日本 | ja-JP.json |
| id-ID | 印尼语 | 印度尼西亚（2.7亿人口，东南亚最大经济体） | id-ID.json |
| vi-VN | 越南语 | 越南（1亿人口，快速增长市场） | vi-VN.json |

选择 id-ID 和 vi-VN 的原因：东南亚是中国互联网产品出海的重点市场，印尼和越南人口基数大、互联网渗透率增长快。

## URL 结构与路由

国际版使用 next-intl 的 `[language]` 动态路由段，URL 结构为 `/{locale}/...`：

```
/en-US/              → 英语首页
/zh-CN/              → 中文首页
/ja-JP/works         → 日语作品列表
/id-ID/submit        → 印尼语提交页
/vi-VN/console       → 越南语管理后台
```

根路径 `/` 会根据浏览器语言或默认语言（en-US）重定向到对应语言路径。

## 字典数据的多语言标签

字典数据（国家/城市/分类/荣誉）通过 `labelI18n` 字段支持多语言，API 根据请求的 lang 参数返回对应语言的标签：

```typescript
// SysDictItem 的 labelI18n 字段示例
{
  "code": "frontend",
  "labelI18n": {
    "en-US": "Frontend",
    "zh-CN": "前端",
    "ja-JP": "フロントエンド",
    "id-ID": "Frontend",
    "vi-VN": "Frontend"
  }
}
```

API 返回时使用 `pickI18nLabel` 函数根据当前语言提取标签：

```typescript
function pickI18nLabel(item: { labelI18n: Record<string, string> }, lang: string) {
  return item.labelI18n[lang] || item.labelI18n['en-US'] || item.name;
}
```

## 已知 Bug：isProtectedRoute 正则遗漏

### 问题描述

middleware.ts 中的 `isProtectedRoute` 正则硬编码了语言列表，未包含新增的 id-ID 和 vi-VN：

```typescript
// src/middleware.ts - 当前有 Bug 的代码
const isProtectedRoute = (pathname: string) => {
  return /^\/(zh-CN|en-US)\/(submit|console|profile)/.test(pathname);
};
```

### 影响范围

| 路径 | zh-CN/en-US | ja-JP | id-ID/vi-VN |
|------|:-----------:|:-----:|:-----------:|
| `/submit` | ✅ 受保护 | ❌ 未保护 | ❌ **未保护（Bug）** |
| `/console` | ✅ 受保护 | ❌ 未保护 | ❌ **未保护（Bug）** |
| `/profile` | ✅ 受保护 | ❌ 未保护 | ❌ **未保护（Bug）** |
| 公开页面（首页/列表/详情） | ✅ 正常 | ✅ 正常 | ✅ 正常 |

受影响的是需要登录认证的页面（submit 提交作品、console 管理后台、profile 个人中心）。印尼语和越南语用户访问 `/id-ID/submit` 或 `/vi-VN/console` 时不会触发认证检查，可能导致未授权访问。

> 注意：ja-JP 在中文版中也存在同样问题（中文版正则也只包含 zh-CN|en-US），但中文版3种语言时这个问题不那么突出，扩展到5种后暴露出根本原因是硬编码。

### 根因

这是一个典型的**DRY违反**——语言列表在 routing.ts 中定义为单一数据源，但 middleware.ts 没有引用它而是硬编码了正则。新增语言时只更新了 routing.ts 和翻译文件，忘记同步修改 middleware.ts。

### 修复方案

从 routing.locales 动态构建正则，消除硬编码：

```typescript
// src/middleware.ts - 修复后的代码
import { routing } from './lib/language/routing';

const localePattern = routing.locales.join('|');
const isProtectedRoute = (pathname: string) => {
  return new RegExp(`^/(${localePattern})/(submit|console|profile)`).test(pathname);
};
```

修复后，未来新增任何语言时只需修改 routing.ts，中间件自动适配。

## 新增语言检查清单

新增语言（如 ko-KR 韩语、th-TH 泰语）时需完成以下步骤：

1. **routing.ts**：在 locales 数组中添加新语言代码
2. **翻译文件**：创建 `src/messages/{locale}.json`，确保所有 key 与其他语言文件对齐
3. **字典 labelI18n**：为 SysDictItem 数据补充新语言的标签翻译
4. **middleware.ts**：确认 isProtectedRoute 使用动态正则（修复 Bug 后此步自动完成）
5. **CSV 导出**：导出逻辑中的 AUDIT_STATUS_LABEL/DISPLAY_STATUS_LABEL 如有硬编码标签需补充翻译
6. **测试**：访问新语言下的受保护路由（submit/console/profile）验证认证检查生效

详见 [添加新语言示例](../examples/add-new-language.md)。

## 翻译文件管理

- 所有翻译文件必须包含完全相同的 key 集合，缺失 key 会导致运行时 fallback 到默认语言或报错
- 翻译文件位于 `src/messages/` 目录，文件名格式为 `{locale}.json`
- 建议使用 next-intl 的 `getRequestConfig` 配置缺失 key 的 fallback 策略

## 相关概念

- [Demo Wall Intl 简介](00-introduction.md)
- [与中文版完整差异对照](06-differences-from-cn.md)
- [5语言配置与翻译扩展示例](../examples/multi-language-setup.md)
- [添加新语言完整步骤](../examples/add-new-language.md)
