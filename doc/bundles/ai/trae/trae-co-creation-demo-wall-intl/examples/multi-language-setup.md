---
type: Example
title: 5语言配置与翻译扩展示例
description: 演示next-intl多语言配置、翻译文件结构、语言切换组件、字典labelI18n翻译补充，以及isProtectedRoute正则Bug的修复方法。
tags: [demo-wall, intl, i18n, next-intl, multi-language, middleware, example]
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

### routing.ts 配置

```typescript
// src/lib/language/routing.ts
export const routing = {
  locales: ['en-US', 'zh-CN', 'ja-JP', 'id-ID', 'vi-VN'],
  defaultLocale: 'en-US',
  localePrefix: 'always',
} as const;

export type Locale = (typeof routing.locales)[number];
```

### 请求配置

```typescript
// src/lib/language/request.ts
import { getRequestConfig } from 'next-intl/server';
import { routing } from './routing';

export default getRequestConfig(async ({ requestLocale }) => {
  let locale = await requestLocale;
  if (!locale || !routing.locales.includes(locale as any)) {
    locale = routing.defaultLocale;
  }

  return {
    locale,
    messages: (await import(`../../messages/${locale}.json`)).default,
  };
});
```

### next-intl 中间件配置

```typescript
// src/middleware.ts
import createIntlMiddleware from 'next-intl/middleware';
import { auth } from '@/lib/auth-nextauth';
import { routing } from '@/lib/language/routing';

const intlMiddleware = createIntlMiddleware(routing);

// ⚠️ Bug：当前硬编码只包含 zh-CN|en-US，遗漏 ja-JP、id-ID、vi-VN
// const isProtectedRoute = (pathname: string) => {
//   return /^\/(zh-CN|en-US)\/(submit|console|profile)/.test(pathname);
// };

// ✅ 修复：从 routing.locales 动态生成正则
const localePattern = routing.locales.join('|');
const protectedPathPattern = new RegExp(
  `^/(${localePattern})/(submit|console|profile)`
);
const isProtectedRoute = (pathname: string) => {
  return protectedPathPattern.test(pathname);
};

export default auth((req) => {
  const { nextUrl } = req;
  const { pathname } = nextUrl;

  // API 认证路由放行
  if (pathname.startsWith('/api/auth')) {
    return;
  }

  // 受保护路由检查登录
  if (isProtectedRoute(pathname) && !req.auth) {
    const locale = pathname.split('/')[1] || routing.defaultLocale;
    return Response.redirect(new URL(`/${locale}/auth/login`, nextUrl));
  }

  // /api 路径跳过 i18n 中间件
  if (pathname.startsWith('/api')) {
    return;
  }

  return intlMiddleware(req);
});

export const config = {
  matcher: ['/((?!_next|.*\\..*).*)'],
};
```

## 翻译文件结构

翻译文件位于 `src/messages/` 目录，每个语言一个 JSON 文件。

### 翻译文件示例（en-US.json）

```json
{
  "common": {
    "submit": "Submit",
    "cancel": "Cancel",
    "save": "Save",
    "delete": "Delete",
    "confirm": "Confirm",
    "loading": "Loading...",
    "noData": "No data available",
    "language": "Language"
  },
  "nav": {
    "home": "Home",
    "works": "Works",
    "rankings": "Rankings",
    "submit": "Submit Work",
    "console": "Admin Console",
    "profile": "Profile",
    "login": "Login",
    "logout": "Logout",
    "register": "Register"
  },
  "work": {
    "title": "Title",
    "description": "Description",
    "category": "Category",
    "honor": "Honor",
    "country": "Country",
    "city": "City",
    "team": "Team",
    "images": "Images",
    "submitWork": "Submit Your Work",
    "editWork": "Edit Work",
    "like": "Like",
    "views": "Views",
    "likes": "Likes"
  },
  "auth": {
    "loginTitle": "Login",
    "registerTitle": "Register",
    "email": "Email",
    "password": "Password",
    "username": "Username",
    "loginSuccess": "Login successful",
    "registerSuccess": "Registration successful"
  },
  "console": {
    "title": "Admin Console",
    "overview": "Overview",
    "works": "Works Management",
    "users": "Users",
    "dictionaries": "Dictionaries",
    "logs": "Logs",
    "export": "Export CSV",
    "syncEdgeConfig": "Sync Edge Config"
  },
  "auditStatus": {
    "pending": "Pending Review",
    "approved": "Approved",
    "rejected": "Rejected"
  },
  "displayStatus": {
    "visible": "Visible",
    "hidden": "Hidden"
  }
}
```

### 翻译文件示例（id-ID.json 印尼语，intl 新增）

```json
{
  "common": {
    "submit": "Kirim",
    "cancel": "Batal",
    "save": "Simpan",
    "delete": "Hapus",
    "confirm": "Konfirmasi",
    "loading": "Memuat...",
    "noData": "Tidak ada data",
    "language": "Bahasa"
  },
  "nav": {
    "home": "Beranda",
    "works": "Karya",
    "rankings": "Peringkat",
    "submit": "Kirim Karya",
    "console": "Konsol Admin",
    "profile": "Profil",
    "login": "Masuk",
    "logout": "Keluar",
    "register": "Daftar"
  },
  "work": {
    "title": "Judul",
    "description": "Deskripsi",
    "category": "Kategori",
    "honor": "Penghargaan",
    "country": "Negara",
    "city": "Kota",
    "team": "Tim",
    "images": "Gambar",
    "submitWork": "Kirim Karya Anda",
    "editWork": "Edit Karya",
    "like": "Suka",
    "views": "Dilihat",
    "likes": "Suka"
  },
  "auth": {
    "loginTitle": "Masuk",
    "registerTitle": "Daftar",
    "email": "Email",
    "password": "Kata Sandi",
    "username": "Nama Pengguna",
    "loginSuccess": "Berhasil masuk",
    "registerSuccess": "Pendaftaran berhasil"
  },
  "console": {
    "title": "Konsol Admin",
    "overview": "Ringkasan",
    "works": "Manajemen Karya",
    "users": "Pengguna",
    "dictionaries": "Kamus",
    "logs": "Log",
    "export": "Ekspor CSV",
    "syncEdgeConfig": "Sinkronkan Edge Config"
  },
  "auditStatus": {
    "pending": "Menunggu Review",
    "approved": "Disetujui",
    "rejected": "Ditolak"
  },
  "displayStatus": {
    "visible": "Terlihat",
    "hidden": "Tersembunyi"
  }
}
```

## 语言切换组件

```tsx
// src/components/language-switcher.tsx
'use client';

import { usePathname, useRouter } from '@/i18n/navigation';
import { useLocale, useTranslations } from 'next-intl';
import { routing, type Locale } from '@/lib/language/routing';

const LANGUAGE_NAMES: Record<Locale, string> = {
  'en-US': 'English',
  'zh-CN': '中文',
  'ja-JP': '日本語',
  'id-ID': 'Bahasa Indonesia',
  'vi-VN': 'Tiếng Việt',
};

export function LanguageSwitcher() {
  const t = useTranslations('common');
  const locale = useLocale() as Locale;
  const router = useRouter();
  const pathname = usePathname();

  const handleChange = (newLocale: Locale) => {
    router.replace(pathname, { locale: newLocale });
  };

  return (
    <select
      value={locale}
      onChange={(e) => handleChange(e.target.value as Locale)}
      aria-label={t('language')}
    >
      {routing.locales.map((loc) => (
        <option key={loc} value={loc}>
          {LANGUAGE_NAMES[loc]}
        </option>
      ))}
    </select>
  );
}
```

## 字典数据 labelI18n 翻译

字典数据（SysDictItem）的多语言通过 `labelI18n` 字段存储：

```typescript
// 字典查询时根据当前语言选择标签
function pickI18nLabel(
  item: { labelI18n: Record<string, string>; name?: string },
  lang: string
): string {
  return (
    item.labelI18n?.[lang] ||
    item.labelI18n?.['en-US'] ||
    item.name ||
    ''
  );
}

// 使用示例
const categories = await prisma.sysDictItem.findMany({
  where: { dictCode: 'category', enabled: true },
  orderBy: { sortOrder: 'asc' },
});

const lang = 'id-ID';
const categoryOptions = categories.map(cat => ({
  value: cat.code,
  label: pickI18nLabel(cat, lang),  // 返回印尼语标签
}));
```

### 补充字典翻译（seed 或管理后台）

新增语言时需要补充所有字典项的 labelI18n 翻译：

```typescript
// prisma/seed.ts 中补充印尼语翻译
await prisma.sysDictItem.updateMany({
  where: { dictCode: 'audit_status' },
  data: {
    labelI18n: {
      'en-US': 'Approved',
      'zh-CN': '已通过',
      'ja-JP': '承認済み',
      'id-ID': 'Disetujui',
      'vi-VN': 'Đã duyệt',
    }
  }
});
```

## 翻译文件一致性检查

确保所有语言文件包含相同的 key 集合：

```typescript
// scripts/check-translations.ts
import fs from 'fs';
import path from 'path';

const messagesDir = path.join(__dirname, '../src/messages');
const files = fs.readdirSync(messagesDir).filter(f => f.endsWith('.json'));

const keys = new Map<string, Set<string>>();
for (const file of files) {
  const content = JSON.parse(fs.readFileSync(path.join(messagesDir, file), 'utf8'));
  keys.set(file, new Set(getAllKeys(content)));
}

// 以 en-US.json 为基准
const baseKeys = keys.get('en-US.json')!;
for (const [file, fileKeys] of keys) {
  const missing = [...baseKeys].filter(k => !fileKeys.has(k));
  const extra = [...fileKeys].filter(k => !baseKeys.has(k));
  if (missing.length > 0) {
    console.log(`${file} - Missing keys: ${missing.join(', ')}`);
  }
  if (extra.length > 0) {
    console.log(`${file} - Extra keys: ${extra.join(', ')}`);
  }
}

function getAllKeys(obj: any, prefix = ''): string[] {
  return Object.entries(obj).flatMap(([k, v]) => {
    const key = prefix ? `${prefix}.${k}` : k;
    return v && typeof v === 'object' && !Array.isArray(v)
      ? getAllKeys(v, key)
      : [key];
  });
}
```

运行检查：

```bash
npx tsx scripts/check-translations.ts
```

## 在客户端组件中使用翻译

```tsx
'use client';

import { useTranslations } from 'next-intl';

export function SubmitButton() {
  const t = useTranslations('common');
  return <button>{t('submit')}</button>;
}
```

## 在服务端组件中使用翻译

```tsx
import { getTranslations } from 'next-intl/server';

export default async function HomePage({ params }: { params: { locale: string } }) {
  const t = await getTranslations('nav');
  return (
    <nav>
      <a href={`/${params.locale}`}>{t('home')}</a>
      <a href={`/${params.locale}/works`}>{t('works')}</a>
    </nav>
  );
}
```

## 相关内容

- [5语言国际化](/concepts/02-multi-language.md)
- [添加新语言完整步骤](/examples/add-new-language.md)
