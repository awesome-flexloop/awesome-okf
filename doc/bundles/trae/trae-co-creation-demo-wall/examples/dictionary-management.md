---
type: Example
title: 字典管理示例
description: 查询字典列表、添加字典项、配置国家/城市/分类、API 调用示例。
tags: [demo-wall, example, dictionary, sysdict, configuration]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: "/references/demo-wall-source.md"
    title: "Demo Wall 源码信源"
---

## 查询字典列表

获取所有字典（分页）（F-085）：

```bash
curl "http://localhost:3000/api/dictionaries?page=1&pageSize=20" \
  -H "Cookie: next-auth.session-token=<admin-session>"
```

### 获取单个字典（含 items）

```bash
curl "http://localhost:3000/api/dictionaries?code=category_code&lang=zh-CN" \
  -H "Cookie: next-auth.session-token=<admin-session>"
```

返回 category_code 字典及其所有字典项，labelI18n 会根据 lang 参数解析为对应语言标签。

### 带筛选的查询

```bash
curl "http://localhost:3000/api/dictionaries?filter=system&query=status&lang=en-US" \
  -H "Cookie: next-auth.session-token=<admin-session>"
```

filter 选项：all/system/custom（F-100）。

## 创建新字典

```bash
curl -X POST http://localhost:3000/api/dictionaries \
  -H "Content-Type: application/json" \
  -H "Cookie: next-auth.session-token=<admin-session>" \
  -d '{
    "type": "dict",
    "dictCode": "ai_model",
    "dictName": "AI模型类型",
    "description": "作品使用的AI模型分类",
    "isSystem": false
  }'
```

## 添加字典项

向 ai_model 字典添加项（F-085）：

```bash
curl -X POST http://localhost:3000/api/dictionaries \
  -H "Content-Type: application/json" \
  -H "Cookie: next-auth.session-token=<admin-session>" \
  -d '{
    "type": "item",
    "dictCode": "ai_model",
    "itemLabel": "GPT-4",
    "labelI18n": {
      "zh-CN": "GPT-4",
      "en-US": "GPT-4",
      "ja-JP": "GPT-4"
    },
    "itemValue": "gpt4",
    "sortOrder": 1,
    "status": true
  }'
```

### 添加带层级的字典项（城市→省份）

城市字典项通过 parentValue 关联省份（F-029, F-055）：

```bash
curl -X POST http://localhost:3000/api/dictionaries \
  -H "Content-Type: application/json" \
  -H "Cookie: next-auth.session-token=<admin-session>" \
  -d '{
    "type": "item",
    "dictCode": "city",
    "itemLabel": "深圳",
    "labelI18n": {"zh-CN": "深圳", "en-US": "Shenzhen", "ja-JP": "深セン"},
    "itemValue": "shenzhen",
    "parentValue": "guangdong",
    "sortOrder": 5,
    "status": true
  }'
```

## 更新字典项

```bash
curl -X PUT http://localhost:3000/api/dictionaries \
  -H "Content-Type: application/json" \
  -H "Cookie: next-auth.session-token=<admin-session>" \
  -d '{
    "type": "item",
    "id": "100",
    "itemLabel": "GPT-4o",
    "labelI18n": {
      "zh-CN": "GPT-4o",
      "en-US": "GPT-4o",
      "ja-JP": "GPT-4o"
    },
    "sortOrder": 1
  }'
```

## 删除字典项

```bash
curl -X DELETE "http://localhost:3000/api/dictionaries?type=item&id=100" \
  -H "Cookie: next-auth.session-token=<admin-session>"
```

## 获取筛选项（公开API）

作品筛选页面调用 GET /api/works/filter-options 获取有作品的分类选项（F-077）：

```bash
curl "http://localhost:3000/api/works/filter-options?lang=zh-CN"
```

返回仅包含有已审核（auditStatus=1）作品的 countries、cities、categories、honors，按 sortFilterOptions 排序（F-078）。

## 多语言标签维护

labelI18n 存储格式为 JSON 对象（F-129）：

```json
{
  "zh-CN": "智能助手",
  "en-US": "AI Assistant",
  "ja-JP": "AIアシスタント"
}
```

API 返回时根据 lang 参数选择标签，lang 参数未命中对应语言时 fallback 到 itemLabel。

## 字典复用：封禁用户示例

封禁用户功能也复用字典表（banned_users 字典），不需要创建新表。banUser() 函数自动 ensureDict 并 upsert 字典项（F-103）。这是字典系统灵活性的体现——运营可配置的分类/列表都可以复用 SysDict/SysDictItem。

## 相关内容

- [字典系统](/concepts/11-dictionary-system.md)
- [数据模型设计](/concepts/03-data-model.md)
- [审核与治理](/concepts/10-audit-governance.md)
- [管理员审核示例](/examples/admin-review.md)
