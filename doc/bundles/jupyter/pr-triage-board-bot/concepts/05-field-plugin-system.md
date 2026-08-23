---
okf_version: "0.2"
type: "concept"
title: "字段插件体系"
description: "字段类型系统（FieldDataType/FieldConfig/FieldSpec）、条件类型映射、REQUIRED_FIELDS注册表模式与插件扩展机制"
tags: [field-plugin, type-system, registry, mapped-types, conditional-types, extensibility]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T10:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: field-config-source
    resource: /references/field-config-source.md
    title: "字段配置体系源码"
  - id: field-impl-source
    resource: /references/field-implementations-source.md
    title: "字段实现源码"
---

# 字段插件体系

pr-triage-board-bot采用**插件式字段架构**——每个PR分类维度是一个独立的字段模块，通过统一的注册表（REQUIRED_FIELDS）组装。这种设计使得添加新字段只需创建一个新文件并注册，不需要修改核心同步逻辑。

## 类型系统四层

字段类型从简单到复杂分为四层：

### 第一层：FieldDataType（数据类型枚举）

```typescript
type FieldDataType = "TEXT" | "NUMBER" | "DATE" | "SINGLE_SELECT";
```

对应GitHub Project V2支持的四种自定义字段数据类型。这是最底层的类型标签。

### 第二层：FieldConfig（静态配置）

```typescript
interface FieldConfig {
    dataType: FieldDataType;
    options?: readonly string[];  // 仅SINGLE_SELECT类型需要
}
```

FieldConfig描述字段的**静态属性**：数据类型是什么，单选字段有哪些选项。

示例：
```typescript
const ciConfig: FieldConfig = {
    dataType: "SINGLE_SELECT",
    options: ["Tests Passing", "Tests Failing"]
};
```

### 第三层：ExtractFieldValueType（类型映射）

```typescript
type ExtractFieldValueType<T extends FieldConfig> =
    T extends { dataType: "SINGLE_SELECT" }
        ? T extends { options: readonly (infer U)[] } ? U : never
        : T extends { dataType: "DATE" } ? Date
        : T extends { dataType: "NUMBER" } ? number
        : T extends { dataType: "TEXT" } ? string
        : never;
```

这是一个TypeScript条件类型（Conditional Types），根据FieldConfig的dataType自动推导getValue函数的返回值类型：

| dataType | 返回类型 | 示例 |
|----------|---------|------|
| SINGLE_SELECT | 选项字符串字面量联合类型 | `"Tests Passing" \| "Tests Failing"` |
| DATE | `Date` | `new Date()` |
| NUMBER | `number` | `42` |
| TEXT | `string` | `"some text"` |

这种映射确保了类型安全：如果配置了SINGLE_SELECT和options，getValue就必须返回其中一个选项值。

### 第四层：FieldSpec（完整规范）

```typescript
type FieldSpec<T extends FieldConfig = FieldConfig> = {
    dataType: T['dataType'];
    getValue: (octokit: PaginatedOctokit, pr: any) => Promise<ExtractFieldValueType<T>>;
} & (T extends { options: any } ? { options: T['options'] } : { options?: undefined });
```

FieldSpec将静态配置与动态计算函数绑定：
- `dataType`：从FieldConfig继承
- `getValue`：异步函数，接收octokit客户端和PR数据，返回对应类型的值
- `options`：条件属性——只有SINGLE_SELECT字段才有options，其他字段为undefined

## FIELD_CONFIGS：静态配置表

```typescript
const FIELD_CONFIGS = {
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

关键点：
- 使用 `as const` 将所有值推导为字面量类型（而非string）
- 使用 `satisfies Record<string, FieldConfig>` 确保每个值都符合FieldConfig约束，同时保留精确类型
- options数组是readonly元组类型，ExtractFieldValueType可以从中提取字面量联合类型

## REQUIRED_FIELDS：字段注册表

```typescript
type RequiredFieldsType = {
    [K in keyof typeof FIELD_CONFIGS]: FieldSpec<typeof FIELD_CONFIGS[K]>
};

const REQUIRED_FIELDS: RequiredFieldsType = {
    "Author Kind":          { ...FIELD_CONFIGS["Author Kind"],          getValue: getAuthorKind },
    "Opened At":            { ...FIELD_CONFIGS["Opened At"],            getValue: getOpenedAt },
    "Total Lines Changed":  { ...FIELD_CONFIGS["Total Lines Changed"],  getValue: getTotalLinesChanged },
    "Maintainer Engagement":{ ...FIELD_CONFIGS["Maintainer Engagement"],getValue: getMaintainerEngagement },
    "CI Status":            { ...FIELD_CONFIGS["CI Status"],            getValue: getCIStatus },
    "Merge Conflicts":      { ...FIELD_CONFIGS["Merge Conflicts"],      getValue: getMergeConflicts },
    "Approval Status":      { ...FIELD_CONFIGS["Approval Status"],      getValue: getApprovalStatus },
};
```

`RequiredFieldsType` 是一个映射类型（Mapped Types），确保：
1. REQUIRED_FIELDS的键必须与FIELD_CONFIGS完全一致（不能多也不能少）
2. 每个键对应的值必须是正确类型的FieldSpec
3. getValue函数的返回类型必须与字段配置匹配

使用展开运算符（`...`）将静态配置复制到FieldSpec中，然后绑定getValue实现。

## getValue函数签名

每个字段模块导出一个getValue函数，类型标注为：

```typescript
export const getFieldName: typeof REQUIRED_FIELDS["Field Name"]["getValue"] = async (octokit, pr) => {
    // 计算并返回值
};
```

使用 `typeof REQUIRED_FIELDS["Field Name"]["getValue"]` 自动推导函数类型，不需要手动标注参数和返回值类型——TypeScript会从注册表中反向推导。

## 注册表模式的优势

1. **开闭原则**：添加新字段不需要修改main.ts或project.ts中的核心逻辑，只需：
   - 创建 `fields/newfield.ts` 导出getValue函数
   - 在FIELD_CONFIGS中添加配置
   - 在REQUIRED_FIELDS中注册
2. **类型安全**：TypeScript在编译时验证getValue返回类型与字段配置匹配
3. **统一遍历**：main函数中通过 `Object.entries(REQUIRED_FIELDS)` 统一遍历所有字段
4. **自动字段创建**：Project.verifyAndCreateFields() 遍历注册表自动创建缺失字段

## 已实现但未注册的字段：Files Changed Type

`fields/fileschangedtype.ts` 实现了 `getFilesChangedType` 函数，根据变更文件的扩展名判断主要变更类型（Documentation/Python/Frontend），但**未在fieldconfig.ts中导入和注册**。这是一个已完成但尚未启用的字段示例，展示了如何扩展字段体系。

启用该字段只需要：
1. 在FIELD_CONFIGS中添加配置项
2. 在REQUIRED_FIELDS中注册getValue函数

## 字段值的null语义

所有getValue函数都可以返回 `null`（对应TypeScript类型中隐式包含的null），表示"当前无法确定该字段的值"。例如：
- CI还在运行 → statusCheckRollup不是SUCCESS/FAILURE → 返回null
- GitHub正在计算合并状态 → mergeable是UNKNOWN → 返回null
- 没有任何审查 → 返回null

main函数中将null映射为 `clearProjectV2ItemFieldValue` mutation，即清空字段值而非设置错误的默认值。

## 相关概念

- [Project管理类](04-project-class.md)
- [七个核心字段详解](06-core-fields.md)
- [同步循环与增量更新](07-sync-loop.md)
