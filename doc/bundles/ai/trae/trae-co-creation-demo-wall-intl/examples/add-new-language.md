---
type: Example
title: 添加新语言完整步骤
description: 以添加泰语（th-TH）为例，演示在国际版中添加第6种语言的完整流程：routing.ts配置→翻译文件→字典labelI18n→middleware验证→测试。
tags: [demo-wall, intl, i18n, language, thai, example, next-intl]
generated: { by: "reference_agent/trae-cn", at: 2026-04-22T00:00:00+08:00 }
verified: { by: "process:grep-verification", at: 2026-04-22T00:00:00+08:00 }
status: stable
stale_after: 2026-10-22
sources:
  - id: src
    resource: /references/demo-wall-intl-source.md
    title: Demo Wall Intl 源码信源索引
---

## 目标

本示例以添加**泰语（th-TH，ภาษาไทย）**为例，演示在国际版中添加新语言的完整正确流程。添加后支持 6 种语言：en-US、zh-CN、ja-JP、id-ID、vi-VN、th-TH。

## 添加语言检查清单

| 步骤 | 文件/位置 | 操作 |
|------|----------|------|
| 1 | `src/lib/language/routing.ts` | 添加 locale 到 locales 数组 |
| 2 | `src/messages/th-TH.json` | 创建翻译文件 |
| 3 | `prisma/seed.ts` 或数据库 | 补充字典 labelI18n 泰语翻译 |
| 4 | `src/middleware.ts` | 确认 isProtectedRoute 使用动态正则（修复 Bug 后自动覆盖） |
| 5 | 语言切换组件 | 确认 LANGUAGE_NAMES 映射包含新语言 |
| 6 | CSV 导出标签 | 确认 AUDIT_STATUS_LABEL/DISPLAY_STATUS_LABEL 包含新语言 |
| 7 | 测试 | 访问 `/th-TH/` 验证各页面 |

## 步骤一：修改 routing.ts

在语言路由配置中添加 th-TH：

```typescript
// src/lib/language/routing.ts
export const routing = {
  locales: ['en-US', 'zh-CN', 'ja-JP', 'id-ID', 'vi-VN', 'th-TH'],  // 添加 th-TH
  defaultLocale: 'en-US',
  localePrefix: 'always',
} as const;

export type Locale = (typeof routing.locales)[number];
```

## 步骤二：创建翻译文件

创建 `src/messages/th-TH.json`，以 en-US.json 为模板：

```bash
# 复制英语翻译作为模板
cp src/messages/en-US.json src/messages/th-TH.json
```

然后翻译所有 value：

```json
{
  "common": {
    "submit": "ส่ง",
    "cancel": "ยกเลิก",
    "save": "บันทึก",
    "delete": "ลบ",
    "confirm": "ยืนยัน",
    "loading": "กำลังโหลด...",
    "noData": "ไม่มีข้อมูล",
    "language": "ภาษา"
  },
  "nav": {
    "home": "หน้าแรก",
    "works": "ผลงาน",
    "rankings": "อันดับ",
    "submit": "ส่งผลงาน",
    "console": "หน้าผู้ดูแล",
    "profile": "โปรไฟล์",
    "login": "เข้าสู่ระบบ",
    "logout": "ออกจากระบบ",
    "register": "สมัครสมาชิก"
  },
  "work": {
    "title": "ชื่อผลงาน",
    "description": "คำอธิบาย",
    "category": "หมวดหมู่",
    "honor": "รางวัล",
    "country": "ประเทศ",
    "city": "เมือง",
    "team": "ทีม",
    "images": "รูปภาพ",
    "submitWork": "ส่งผลงานของคุณ",
    "editWork": "แก้ไขผลงาน",
    "like": "ถูกใจ",
    "views": "การดู",
    "likes": "ถูกใจ"
  },
  "auth": {
    "loginTitle": "เข้าสู่ระบบ",
    "registerTitle": "สมัครสมาชิก",
    "email": "อีเมล",
    "password": "รหัสผ่าน",
    "username": "ชื่อผู้ใช้",
    "loginSuccess": "เข้าสู่ระบบสำเร็จ",
    "registerSuccess": "สมัครสมาชิกสำเร็จ"
  },
  "console": {
    "title": "หน้าผู้ดูแลระบบ",
    "overview": "ภาพรวม",
    "works": "จัดการผลงาน",
    "users": "ผู้ใช้",
    "dictionaries": "พจนานุกรม",
    "logs": "บันทึก",
    "export": "ส่งออก CSV",
    "syncEdgeConfig": "ซิงค์ Edge Config"
  },
  "auditStatus": {
    "pending": "รอการตรวจสอบ",
    "approved": "อนุมัติแล้ว",
    "rejected": "ถูกปฏิเสธ"
  },
  "displayStatus": {
    "visible": "แสดง",
    "hidden": "ซ่อน"
  }
}
```

### 翻译一致性检查

使用检查脚本确保翻译文件 key 完整：

```bash
# 运行翻译一致性检查（如果有此脚本）
npx tsx scripts/check-translations.ts
```

确保 th-TH.json 没有缺失 key 也没有多余 key。

## 步骤三：补充字典 labelI18n

系统字典数据（国家/城市/分类/荣誉/审核状态等）需要补充泰语标签。

### 方式一：通过管理后台

1. 登录管理员账号
2. 进入字典管理页面
3. 逐个编辑字典项，添加 th-TH 标签
4. 完成后触发 Edge Config 同步

### 方式二：通过数据库脚本

```typescript
// scripts/add-thai-translations.ts
import { prisma } from '../src/lib/prisma';

async function addThaiTranslations() {
  // 审核状态翻译
  const auditStatusMap: Record<string, string> = {
    pending: 'รอการตรวจสอบ',
    approved: 'อนุมัติแล้ว',
    rejected: 'ถูกปฏิเสธ',
  };

  const displayStatusMap: Record<string, string> = {
    visible: 'แสดง',
    hidden: 'ซ่อน',
  };

  // 更新审核状态标签
  for (const [code, label] of Object.entries(auditStatusMap)) {
    await prisma.sysDictItem.updateMany({
      where: { dictCode: 'audit_status', code },
      data: {
        labelI18n: {
          update: {
            'th-TH': label,
          },
        },
      },
    });
  }

  // 更新展示状态标签
  for (const [code, label] of Object.entries(displayStatusMap)) {
    await prisma.sysDictItem.updateMany({
      where: { dictCode: 'display_status', code },
      data: {
        labelI18n: {
          update: {
            'th-TH': label,
          },
        },
      },
    });
  }

  // 分类翻译示例
  const categoryMap: Record<string, string> = {
    frontend: 'ฟรอนต์เอนด์',
    backend: 'แบ็กเอนด์',
    mobile: 'โมบายล์',
    'ai-agent': 'เอเจนต์ AI',
    design: 'ดีไซน์',
    game: 'เกม',
    tool: 'เครื่องมือ',
    other: 'อื่นๆ',
  };

  for (const [code, label] of Object.entries(categoryMap)) {
    await prisma.sysDictItem.updateMany({
      where: { dictCode: 'category', code },
      data: {
        labelI18n: {
          update: {
            'th-TH': label,
          },
        },
      },
    });
  }

  // 国家/城市翻译量大，可以先用英语标签填充，后续由运营翻译
  const countries = await prisma.sysDictItem.findMany({
    where: { dictCode: 'country' },
  });
  for (const country of countries) {
    const labelI18n = country.labelI18n as Record<string, string> || {};
    if (!labelI18n['th-TH']) {
      labelI18n['th-TH'] = labelI18n['en-US'] || country.name;
      await prisma.sysDictItem.update({
        where: { id: country.id },
        data: { labelI18n },
      });
    }
  }

  console.log('Thai translations added successfully');
}

addThaiTranslations()
  .catch(console.error)
  .finally(() => prisma.$disconnect());
```

运行脚本：

```bash
npx tsx scripts/add-thai-translations.ts
```

## 步骤四：确认中间件自动覆盖

如果已按 [5语言国际化](/concepts/02-multi-language.md) 中的修复方案修改了 middleware.ts（使用动态正则），则添加 th-TH 后**无需修改中间件**：

```typescript
// src/middleware.ts —— 修复后，自动覆盖所有在 routing.locales 中定义的语言
import { routing } from './lib/language/routing';

const localePattern = routing.locales.join('|');
const isProtectedRoute = (pathname: string) => {
  return new RegExp(`^/(${localePattern})/(submit|console|profile)`).test(pathname);
};
```

正则自动变为 `/^\/(en-US|zh-CN|ja-JP|id-ID|vi-VN|th-TH)\/(submit|console|profile)/`，泰语受保护路由自动受保护。

**如果尚未修复 Bug**（仍使用硬编码正则），必须修改 middleware.ts 或添加 th-TH 到硬编码正则：

```typescript
// ⚠️ 不推荐的方式（硬编码）
const isProtectedRoute = (pathname: string) => {
  return /^\/(en-US|zh-CN|ja-JP|id-ID|vi-VN|th-TH)\/(submit|console|profile)/.test(pathname);
};
```

**强烈建议**修复为动态正则方式，避免每次添加语言都忘记修改。

## 步骤五：更新语言切换组件

确保语言切换组件包含泰语的显示名称：

```tsx
// src/components/language-switcher.tsx
const LANGUAGE_NAMES: Record<Locale, string> = {
  'en-US': 'English',
  'zh-CN': '中文',
  'ja-JP': '日本語',
  'id-ID': 'Bahasa Indonesia',
  'vi-VN': 'Tiếng Việt',
  'th-TH': 'ไทย',  // 添加泰语
};
```

## 步骤六：更新 CSV 导出标签映射

CSV 导出中的 AUDIT_STATUS_LABEL 和 DISPLAY_STATUS_LABEL 需要补充泰语：

```typescript
// src/app/api/console/works/export/route.ts
const AUDIT_STATUS_LABEL: Record<string, Record<string, string>> = {
  'en-US': { pending: 'Pending', approved: 'Approved', rejected: 'Rejected' },
  'zh-CN': { pending: '待审核', approved: '已通过', rejected: '已拒绝' },
  'ja-JP': { pending: '審査待ち', approved: '承認済み', rejected: '却下' },
  'id-ID': { pending: 'Menunggu Review', approved: 'Disetujui', rejected: 'Ditolak' },
  'vi-VN': { pending: 'Chờ duyệt', approved: 'Đã duyệt', rejected: 'Từ chối' },
  'th-TH': { pending: 'รอการตรวจสอบ', approved: 'อนุมัติแล้ว', rejected: 'ถูกปฏิเสธ' },  // 添加
};

const DISPLAY_STATUS_LABEL: Record<string, Record<string, string>> = {
  'en-US': { visible: 'Visible', hidden: 'Hidden' },
  'zh-CN': { visible: '展示中', hidden: '已隐藏' },
  'ja-JP': { visible: '表示中', hidden: '非表示' },
  'id-ID': { visible: 'Terlihat', hidden: 'Tersembunyi' },
  'vi-VN': { visible: 'Hiển thị', hidden: 'Ẩn' },
  'th-TH': { visible: 'แสดง', hidden: 'ซ่อน' },  // 添加
};
```

## 步骤七：测试

启动开发服务器测试：

```bash
npm run dev
```

### 测试清单

| 测试项 | URL | 预期结果 |
|--------|-----|---------|
| 泰语首页 | `/th-TH/` | 自动重定向到 `/th-TH/`，显示泰语界面 |
| 语言切换 | 任意页面 | 切换到 "ไทย"，URL 变为 `/th-TH/...`，界面变为泰语 |
| 受保护路由-未登录 | `/th-TH/submit` | 重定向到 `/th-TH/auth/login` |
| 受保护路由-未登录 | `/th-TH/console` | 重定向到 `/th-TH/auth/login` |
| 受保护路由-未登录 | `/th-TH/profile` | 重定向到 `/th-TH/auth/login` |
| 登录 | `/th-TH/auth/login` | 可以使用管理员账号登录 |
| 管理后台 | `/th-TH/console` | 登录后可访问，标签显示泰语 |
| 作品提交 | `/th-TH/submit` | 表单标签显示泰语，分类/荣誉/国家下拉显示泰语标签 |
| 字典数据 | 提交页筛选器 | 国家/城市/分类/荣誉显示泰语标签 |
| CSV 导出 | `/th-TH/console/works/export` | 导出的 CSV 中审核状态显示泰语 |
| Edge Config 同步 | POST `/api/sync-edge-config` | 同步后泰语标签缓存到 Edge Config |
| 根路径重定向 | `/` | 浏览器语言偏好为泰语时重定向到 `/th-TH/`，否则默认 `/en-US/` |

## 步骤八：同步 Edge Config（Vercel 部署）

字典数据更新后，需要重新同步 Edge Config：

```bash
curl -X POST https://your-domain.vercel.app/api/sync-edge-config \
  -H "Cookie: next-auth.session-token=your-admin-token"
```

## 常见问题

### Q: 添加语言后 `/th-TH/submit` 可以直接访问（不需要登录）？

A: 这说明中间件正则没有正确覆盖 th-TH。检查：
1. routing.ts 是否已添加 th-TH
2. middleware.ts 是否使用动态正则
3. 重启开发服务器（修改 middleware.ts 需要重启）

### Q: 翻译文件中部分 key 显示为 key 名而非翻译文本？

A: th-TH.json 中缺少对应的 key。使用检查脚本找出缺失 key 并补充翻译。

### Q: 字典下拉显示英语而非泰语？

A: 字典数据的 labelI18n 中没有 th-TH 字段。通过管理后台或脚本补充翻译后，重新同步 Edge Config。

### Q: 添加语言后构建失败？

A: 常见原因：
1. th-TH.json 有 JSON 语法错误（多余逗号、缺少引号等）
2. next-intl 的 getRequestConfig 找不到 th-TH.json 文件
3. TypeScript 类型错误（LANGUAGE_NAMES 缺少 th-TH 键）

## 相关内容

- [5语言国际化](/concepts/02-multi-language.md)
- [5语言配置与翻译扩展示例](/examples/multi-language-setup.md)
- [Vercel Edge Config缓存](/concepts/01-edge-config-cache.md)
