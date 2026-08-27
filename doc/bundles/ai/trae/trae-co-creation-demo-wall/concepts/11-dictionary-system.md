---
type: Concept
title: 字典系统
description: Demo Wall 的 SysDict/SysDictItem 动态分类系统，国家/城市/类别/状态/荣誉字典，seed 初始化，管理 API，以及字典表在封禁/屏蔽等场景的复用。
tags: [demo-wall, dictionary, sysdict, i18n, configuration]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: "/references/demo-wall-source.md"
    title: "Demo Wall 源码信源"
---

## 字典系统概览

字典系统由两张表实现（F-028~F-029）：

- **SysDict**：字典分类（dictCode 唯一标识）
- **SysDictItem**：字典项（通过 dictCode 归属到某个字典）

这是一个通用的键值对+层级分类系统，不仅用于业务分类（作品分类/开发状态/荣誉类型），还复用于用户封禁列表（banned_users）和邮箱域名屏蔽（blocked_email_domains）（F-049）。

## SysDict 模型（F-028）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BigInt PK | 自增主键 |
| dictCode | String(50) unique | 字典编码 |
| dictName | String(50) | 字典名称 |
| description | String?(255) | 描述 |
| isSystem | Boolean? default(false) | 是否系统内置 |

## SysDictItem 模型（F-029）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BigInt PK | 自增主键 |
| dictCode | String(50) | 所属字典编码 |
| itemLabel | String(100) | 默认显示标签 |
| labelI18n | Json? | 多语言标签 {"zh-CN":"...","en-US":"..."} |
| itemValue | String(100) | 字典项值 |
| parentValue | String?(100) | 父级值（层级关系，如城市→省份） |
| sortOrder | Int? default(0) | 排序序号 |
| status | Boolean? default(true) | 是否启用 |

唯一约束：`@@unique([dictCode, itemValue])`

## 预置系统字典（F-049~F-055）

seed.ts 初始化以下系统字典（isSystem=true）：

| dictCode | 用途 | 预置项 |
|----------|------|--------|
| audit_status | 审核状态 | 0=待审核、1=已通过、2=已拒绝 |
| dev_status | 开发状态 | ideation/prototype/completed/released |
| category_code | 作品分类 | utility/scenario/assistant/content/creative/other |
| honor_type | 荣誉类型 | community_choice/city_star/best_of_year |
| banned_users | 封禁用户黑名单 | 动态添加 |
| blocked_email_domains | 屏蔽邮箱域名 | example.com、example.org、example.net |
| country | 省份/国家 | 从 seed-data-countries.ts 导入 |
| city | 城市 | 从 seed-data-countries.ts 导入，parentValue 关联省份 |

addItem() 辅助函数执行幂等 upsert（先查后创建），seed 可重复执行（F-057）。

## 字典管理 API（F-085）

GET /api/dictionaries：字典列表（分页/搜索/筛选），支持 `code` 参数获取单个字典（含 items），支持 `lang` 参数做多语言标签替换。

POST/PUT/DELETE /api/dictionaries：通过 `type` 参数区分操作字典（dict）还是字典项（item）。

## 多语言标签解析（F-129）

API 返回字典项时，根据 lang 参数解析 labelI18n：

- 如果 labelI18n 存在且包含对应语言的键，返回该语言标签
- 否则 fallback 到 itemLabel

筛选项排序（F-078）：先按 sortOrder 升序，sortOrder 相同时按 `label.localeCompare(label, lang)` 本地化排序。

## 字典复用：封禁与屏蔽（F-103）

字典系统最巧妙的复用是将封禁用户和屏蔽域名也存储为字典：

- banned_users 字典的 itemValue 存储被封禁用户的 ID 字符串
- blocked_email_domains 字典的 itemValue 存储被屏蔽的邮箱域名
- banUser() 自动 ensureDict（首次封禁自动创建字典），使用 upsert 写入
- isEmailDomainBlocked() 合并默认域名和数据库配置的域名（转小写匹配）
- 60秒内存缓存避免频繁查库

这种设计省掉了额外的黑名单表设计，且支持动态配置无需改代码。

## 角色为什么不用字典？

角色（SysRole）选择硬编码三级（root/admin/common）而非字典，因为角色与代码权限检查强耦合（isAdmin() 直接判断字符串），动态化会导致安全漏洞——如果管理员通过 API 新增了一个角色但代码中没有对应的权限检查逻辑，会造成安全问题（F-084）。

## 相关概念

- [数据模型设计](03-data-model.md)
- [审核与治理](10-audit-governance.md)
- [认证系统](04-auth-system.md)
- [国际化路由](05-i18n-routing.md)
- [API 路由设计](06-api-routes.md)
- [字典管理示例](../examples/dictionary-management.md)
