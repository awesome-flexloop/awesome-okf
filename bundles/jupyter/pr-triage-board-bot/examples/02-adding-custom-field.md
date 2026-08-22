---
okf_version: "0.2"
type: "example"
title: "添加自定义字段扩展"
description: "逐步演示如何为pr-triage-board-bot添加新的自定义分类字段，以'Files Changed Type'为例"
tags: [custom-field, extension, how-to, plugin]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T10:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: concepts-field-plugin
    resource: /concepts/05-field-plugin-system.md
    title: "字段插件体系"
  - id: field-impl-source
    resource: /references/field-implementations-source.md
    title: "字段实现源码"
---

# 添加自定义字段扩展

本示例演示如何为机器人添加新的分类字段。我们将以"Files Changed Type"（变更文件类型）为例——该字段的getValue函数已经实现但尚未注册，因此只需完成注册步骤即可。

## 场景需求

我们希望在项目板上新增一个"SINGLE_SELECT"字段，自动判断每个PR的主要变更类型：
- **Documentation**：主要变更为Markdown/RST文档
- **Python**：主要变更为Python代码
- **Frontend**：主要变更为前端文件（JS/TS/CSS/HTML）

## 步骤1：创建字段模块（已存在）

`fields/fileschangedtype.ts` 已经实现了 `getFilesChangedType` 函数：

```typescript
const EXTENSIONS = {
    Documentation: [".md", ".rst"],
    Python: [".py"],
    Frontend: [".js", ".jsx", ".ts", ".tsx", ".css", ".html", ".scss"],
};

export const getFilesChangedType: typeof REQUIRED_FIELDS["Files Changed Type"]["getValue"] = async (octokit, pr) => {
    const response = await octokit.graphql.paginate(`
        query paginate($cursor: String, $prNodeId: ID!) {
            node(id: $prNodeId) {
                ... on PullRequest {
                    files(first: 100, after: $cursor) {
                        nodes { path, additions, deletions }
                        pageInfo { hasNextPage, endCursor }
                    }
                }
            }
        }
    `, { prNodeId: pr.id });

    const fileDiffs: Record<string, number> = { other: 0 };

    for (const file of response.node.files.nodes) {
        const extension = extname(file.path);
        const totalLines = file.additions + file.deletions;
        let categorized = false;
        for (const [category, exts] of Object.entries(EXTENSIONS)) {
            if (exts.includes(extension)) {
                fileDiffs[category] = (fileDiffs[category] || 0) + totalLines;
                categorized = true;
                break;
            }
        }
        if (!categorized) {
            fileDiffs.other += totalLines;
        }
    }

    const sortedCategories = Object.entries(fileDiffs)
        .filter(([category]) => category !== "other")
        .sort((a, b) => b[1] - a[1]);

    if (sortedCategories.length > 0 && sortedCategories[0][1] > fileDiffs.other) {
        return sortedCategories[0][0] as keyof typeof EXTENSIONS;
    }
    return null;
};
```

> 💡 该函数使用 `typeof REQUIRED_FIELDS["Files Changed Type"]["getValue"]` 标注类型——此时TypeScript会报错，因为"Files Changed Type"还未在注册表中。这是正常的，我们将在步骤3中解决。

## 步骤2：在FIELD_CONFIGS中添加配置

编辑 `src/fieldconfig.ts`，在 `FIELD_CONFIGS` 对象中添加：

```typescript
const FIELD_CONFIGS = {
    // ... 现有字段 ...
    "Merge Conflicts": {
        dataType: "SINGLE_SELECT",
        options: ["Merge Conflicts", "No Merge Conflicts"]
    },
    "Approval Status": {
        dataType: "SINGLE_SELECT",
        options: ["Changes Requested", "Maintainer Approved"]
    },
    // ⬇️ 新增字段
    "Files Changed Type": {
        dataType: "SINGLE_SELECT",
        options: ["Documentation", "Python", "Frontend"]
    }
} as const satisfies Record<string, FieldConfig>;
```

注意：options数组中的字符串必须与getFilesChangedType函数返回的字符串完全一致。

## 步骤3：导入并注册到REQUIRED_FIELDS

在 `src/fieldconfig.ts` 顶部添加导入：

```typescript
import { getFilesChangedType } from './fields/fileschangedtype.js';
```

然后在 `REQUIRED_FIELDS` 对象中注册：

```typescript
const REQUIRED_FIELDS: RequiredFieldsType = {
    // ... 现有字段注册 ...
    "Approval Status":      { ...FIELD_CONFIGS["Approval Status"],      getValue: getApprovalStatus },
    // ⬇️ 新增注册
    "Files Changed Type":   { ...FIELD_CONFIGS["Files Changed Type"],   getValue: getFilesChangedType },
};
```

此时TypeScript类型错误应该消失，因为：
1. FIELD_CONFIGS中添加了"Files Changed Type"键
2. RequiredFieldsType映射类型自动包含了该字段的类型
3. getFilesChangedType的返回类型与SINGLE_SELECT+options匹配

## 步骤4：修复GraphQL查询（如需要）

`getFilesChangedType` 函数使用了PR的files字段，但当前`prs.gql`查询中没有获取files数据。这意味着函数内需要单独查询files（当前实现已经这样做了——使用独立的paginate查询获取文件列表）。

如果要将files加入主查询以减少API调用，需要修改`src/graphql/prs.gql`。但注意files可能很多（first:100有分页），在主查询中获取可能导致超时。当前设计（单独查询每个PR的files）是合理的，因为只在计算新字段值时才需要files数据。

## 步骤5：构建并测试

```bash
# 编译
npm run build

# Dry run验证
node dist/src/main.js \
  --gh-app-id <APP_ID> \
  --gh-app-installation-id <INSTALLATION_ID> \
  --gh-app-pem-file ./private-key.pem \
  --dry-run \
  <org> <project-number>
```

首次运行时，verifyAndCreateFields会自动创建"Files Changed Type"字段及其选项。dry run日志中应该能看到：
```
Missing field detected: Files Changed Type
Created field: Files Changed Type (SINGLE_SELECT)
Setting Files Changed Type to Documentation for https://github.com/...
Setting Files Changed Type to Python for https://github.com/...
Setting Files Changed Type to null for https://github.com/...
```

确认无误后，去掉 `--dry-run` 正式运行。

## 添加全新字段的通用模板

如果要添加一个完全新的字段（如"PR Size Category"），步骤如下：

### 1. 创建 `src/fields/newsizecategory.ts`

```typescript
import type { PaginatedOctokit } from "../main.js";
import type { REQUIRED_FIELDS } from "../fieldconfig.js";

// 注意：这里需要用字符串键名引用尚未注册的字段
// TypeScript会报错，但注册后自动修复
export const getSizeCategory: typeof REQUIRED_FIELDS["Size Category"]["getValue"] = async (octokit, pr) => {
    const total = pr.additions + pr.deletions;
    if (total < 50) return "Tiny";
    if (total < 200) return "Small";
    if (total < 500) return "Medium";
    if (total < 1000) return "Large";
    return "Huge";
};
```

### 2. 在FIELD_CONFIGS添加配置

```typescript
"Size Category": {
    dataType: "SINGLE_SELECT",
    options: ["Tiny", "Small", "Medium", "Large", "Huge"]
}
```

### 3. 导入并注册

```typescript
import { getSizeCategory } from './fields/newsizecategory.js';

// 在REQUIRED_FIELDS中：
"Size Category": { ...FIELD_CONFIGS["Size Category"], getValue: getSizeCategory },
```

### 4. 编译测试

```bash
npm run typecheck  # 确保类型检查通过
npm run build
```

## 设计原则回顾

- **开闭原则**：扩展字段不需要修改同步循环逻辑
- **类型安全**：TypeScript条件类型确保返回值与配置匹配
- **自动创建**：新字段首次运行自动在项目板上创建
- **null语义**：无法判定时返回null而非错误默认值

## 相关示例

- [GitHub App创建与配置完整流程](01-github-app-setup.md)：扩展字段前先确保App配置正确
- [GitHub Action部署workflow配置](03-github-action-workflow.md)：扩展后部署到定时workflow

## 相关概念

- [字段插件体系](../concepts/05-field-plugin-system.md)：四层类型系统、注册表模式、条件类型映射详解
- [七个核心字段详解](../concepts/06-core-fields.md)：现有字段的计算逻辑参考
- [同步循环与增量更新](../concepts/07-sync-loop.md)：字段值如何被同步循环调用和比较
