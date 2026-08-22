---
type: Reference
title: simple-validators 验证器源码信源
description: simple-validators 包提供的 20+ 个运行时验证函数、ValidationOptions 类型以及错误/警告收集机制的源码登记。
tags: [mystmd, validation, simple-validators, schema, config]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "simple-validators/src/index.ts"
    facts: [F-105, F-106]
  - path: "simple-validators/src/validators.ts"
    facts: [F-107, F-108, F-109, F-110, F-111, F-112]
  - path: "simple-validators/src/types.ts"
    facts: []
---

## 源码位置

- `simple-validators/src/index.ts` — 包导出入口
- `simple-validators/src/validators.ts` — 验证函数实现
- `simple-validators/src/types.ts` — ValidationOptions、KeyOptions 类型定义

## 导出 API

### 核心工具函数

| 函数 | 签名 | 说明 |
|------|------|------|
| `defined` | `<T>(val: T \| null \| undefined): val is T` | 检查值非 null/undefined（返回 `val != null`） |
| `locationSuffix` | `(opts: Partial<ValidationOptions>) => string` | 生成位置后缀字符串（file#location） |
| `incrementOptions` | `(property: string, opts: ValidationOptions) => ValidationOptions` | 增量创建嵌套属性的验证选项，更新 location |
| `validationError` | `(message: string, opts: ValidationOptions) => undefined` | 记录错误（推入 messages.errors，调用 errorLogFn），返回 undefined |
| `validationWarning` | `(message: string, opts: ValidationOptions) => undefined` | 记录警告（推入 messages.warnings，调用 warningLogFn），返回 undefined |

### 标量验证函数

| 函数 | 说明 |
|------|------|
| `validateBoolean(input, opts)` | 验证布尔值；'true'/'false' 字符串（不区分大小写）自动转换 |
| `validateString(input, opts)` | 验证字符串；支持 maxLength、regex、coerceNumber、escapeFn 选项 |
| `validateNumber(input, opts)` | 验证数字；Number(input) 强制转换；支持 min/max/integer 选项 |
| `validateUrl(input, opts)` | 验证 URL |
| `validateSubdomain(input, opts)` | 验证子域名 |
| `validateDomain(input, opts)` | 验证域名 |
| `validateEmail(input, opts)` | 验证邮箱地址 |
| `validateChoice(input, opts)` | 验证枚举值（在 choices 列表中） |
| `validateEnum(input, opts)` | 验证 TypeScript 枚举值 |
| `validateDate(input, opts)` | 验证日期 |

### 复合验证函数

| 函数 | 说明 |
|------|------|
| `validateObject(input, opts)` | 验证对象 |
| `validateKeys(input, opts)` | 验证对象键名 |
| `validateObjectKeys(input, opts)` | 验证对象键集合（required/optional 检查） |
| `validateList(input, opts)` | 验证列表/数组 |

### 对象工具函数

| 函数 | 说明 |
|------|------|
| `fillMissingKeys` | 填充缺失键的默认值 |
| `filterKeys` | 过滤对象键 |

### 验证机制

validationError/validationWarning 的工作方式：
1. 检查 opts.suppressErrors/suppressWarnings，若被抑制则直接返回 undefined
2. 从 opts.messages 获取 errors/warnings 数组（不存在则创建）
3. 构建完整消息：`'${opts.property}' ${message}${locationSuffix(opts)}`
4. 将 `{property, message: fullMessage}` 推入对应数组
5. 调用 opts.errorLogFn/warningLogFn（如果存在）
6. 返回 undefined（表示验证失败）

incrementOptions 的工作方式：
- 将当前 property 追加到 location（`opts.location.opts.property`）
- 返回新的 ValidationOptions 对象（展开复制）
