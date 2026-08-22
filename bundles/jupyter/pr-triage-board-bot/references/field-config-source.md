---
type: Reference
title: "字段配置体系源码"
description: "fieldconfig.ts类型系统、FIELD_CONFIGS配置、FieldSpec/FieldConfig类型映射、REQUIRED_FIELDS注册表"
tags: [field-config, type-system, registry, single-select, data-type, mapped-types]
sources:
  - id: fieldconfig-ts
    resource: "../../../../../external/libs/jupyter/pr-triage-board-bot/src/fieldconfig.ts"
    title: "src/fieldconfig.ts"
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T10:00:00Z" }
status: stable
stale_after: 2027-12-31
---

# 字段配置体系源码

## 文件概览

`src/fieldconfig.ts` 定义了字段类型系统和字段注册表，是插件式字段架构的核心。

## 类型定义

### FieldDataType

```typescript
export type FieldDataType = "TEXT" | "NUMBER" | "DATE" | "SINGLE_SELECT";
```

对应 GitHub Project V2 支持的自定义字段数据类型。

### FieldConfig接口

```typescript
export interface FieldConfig {
    dataType: FieldDataType;
    options?: readonly string[];  // SINGLE_SELECT类型的选项列表
}
```

### ExtractFieldValueType：条件类型映射

```typescript
type ExtractFieldValueType<T extends FieldConfig> =
    T extends { dataType: "SINGLE_SELECT" }
        ? T extends { options: readonly (infer U)[] } ? U : never
        : T extends { dataType: "DATE" } ? Date
        : T extends { dataType: "NUMBER" } ? number
        : T extends { dataType: "TEXT" } ? string
        : never;
```

这个条件类型将字段配置映射到对应的TypeScript返回值类型：
- `SINGLE_SELECT` → 选项字符串字面量联合类型（如 `"Bot" | "Maintainer" | ...`）
- `DATE` → `Date`
- `NUMBER` → `number`
- `TEXT` → `string`

### FieldSpec类型

```typescript
export type FieldSpec<T extends FieldConfig = FieldConfig> = {
    dataType: T['dataType'];
    getValue: (octokit: PaginatedOctokit, pr: any) => Promise<ExtractFieldValueType<T>>;
} & (T extends { options: any } ? { options: T['options'] } : { options?: undefined });
```

FieldSpec将FieldConfig与getValue函数绑定，条件类型确保：
- SINGLE_SELECT字段必须包含options且getValue返回对应的字面量类型
- 非SINGLE_SELECT字段options为undefined

## FIELD_CONFIGS：字段静态配置

```typescript
export const FIELD_CONFIGS = {
    "Author Kind": {
        dataType: "SINGLE_SELECT",
        options: ["Bot", "Maintainer", "First Time Contributor", "Early Contributor", "Seasoned Contributor"]
    },
    "Opened At": { dataType: "DATE" },
    "Total Lines Changed": { dataType: "NUMBER" },
    "Maintainer Engagement": {
        dataType: "SINGLE_SELECT",
        options: ["No Maintainer Engagement", "Single Maintainer Engagement", "Multiple Maintainer Engagement"]
    },
    "CI Status": {
        dataType: "SINGLE_SELECT",
        options: ["Tests Passing", "Tests Failing"]
    },
    "Merge Conflicts": {
        dataType: "SINGLE_SELECT",
        options: ["Merge Conflicts", "No Merge Conflicts"]
    },
    "Approval Status": {
        dataType: "SINGLE_SELECT",
        options: ["Changes Requested", "Maintainer Approved"]
    }
} as const satisfies Record<string, FieldConfig>;
```

使用 `as const satisfies Record<string, FieldConfig>` 确保：
- 对象字面量被推导为最精确的类型（readonly字面量类型）
- 每个值满足FieldConfig接口约束

## REQUIRED_FIELDS：字段注册表

```typescript
export const REQUIRED_FIELDS: RequiredFieldsType = {
    "Author Kind":          { ...FIELD_CONFIGS["Author Kind"],          getValue: getAuthorKind },
    "Opened At":            { ...FIELD_CONFIGS["Opened At"],            getValue: getOpenedAt },
    "Total Lines Changed":  { ...FIELD_CONFIGS["Total Lines Changed"],  getValue: getTotalLinesChanged },
    "Maintainer Engagement":{ ...FIELD_CONFIGS["Maintainer Engagement"],getValue: getMaintainerEngagement },
    "CI Status":            { ...FIELD_CONFIGS["CI Status"],            getValue: getCIStatus },
    "Merge Conflicts":      { ...FIELD_CONFIGS["Merge Conflicts"],      getValue: getMergeConflicts },
    "Approval Status":      { ...FIELD_CONFIGS["Approval Status"],      getValue: getApprovalStatus },
};
```

使用展开运算符（`...`）将静态配置与getValue函数合并。`RequiredFieldsType` 是映射类型：

```typescript
type RequiredFieldsType = {
    [K in keyof typeof FIELD_CONFIGS]: FieldSpec<typeof FIELD_CONFIGS[K]>
};
```

确保REQUIRED_FIELDS中的每个键都与FIELD_CONFIGS对应，且FieldSpec类型正确。

## 字段导入关系

```typescript
import { getAuthorKind }         from './fields/authorkind.js';
import { getOpenedAt }           from './fields/openedat.js';
import { getTotalLinesChanged }  from './fields/totallineschanged.js';
import { getMaintainerEngagement } from './fields/maintainerengagement.js';
import { getCIStatus }           from './fields/cistatus.js';
import { getMergeConflicts }     from './fields/mergeconflicts.js';
import { getApprovalStatus }     from './fields/approvalstatus.js';
```

注意：`fileschangedtype.ts` 中的 `getFilesChangedType` **未被导入**到fieldconfig.ts中，是一个已实现但未注册的字段。

## 相关信源

- [字段实现源码](field-implementations-source.md)
- [Project管理类源码](project-source.md)
