---
type: Reference
title: Demo Wall 源码信源
description: trae-co-creation-demo-wall 源码核心文件路径索引，按模块分类登记所有关键源文件及其职责。
tags: [demo-wall, source, reference, nextjs, prisma]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: "/references/demo-wall-source.md"
    title: "Demo Wall 源码信源"
---

## Demo Wall 源码索引

本文档登记 trae-co-creation-demo-wall 源码中各核心模块的文件路径（相对仓库根），作为 Wiki 中所有事实溯源的信源目标。源码仓库位于 `external/libs/ai/trae-community/trae-co-creation-demo-wall/`。

### 入口配置

| 文件 | 路径（相对仓库根） | 职责 |
|------|-------------------|------|
| 包定义 | `package.json` | 项目元数据（名称/版本/私有）、依赖声明（Next.js 15/React 18/Prisma/NextAuth/next-intl/Tiptap/COS）、npm scripts（dev/build/start/seed/lint/test:*） |
| Next.js 配置 | `next.config.ts` | output='standalone'、images.unoptimized=true、outputFileTracingExcludes 排除 SWC 二进制、next-intl plugin 集成 |
| TypeScript 配置 | `tsconfig.json` | target=ES2017、strictNullChecks=true、moduleResolution=bundler、路径别名 @/* → ./src/* |
| Tailwind 配置 | `tailwind.config.js` | darkMode: class、品牌绿色板（green-300~600）、CSS 变量驱动主题色 |
| PostCSS 配置 | `postcss.config.js` | Tailwind CSS PostCSS 插件配置 |
| ESLint 配置 | `eslint.config.js` | 代码检查规则 |
| shadcn/ui 配置 | `components.json` | style=default、rsc=true、tsx=true、baseColor=zinc |
| 全局样式 | `src/assets/globals.css` | 全局 CSS 变量与 Tailwind 基础样式 |

### 数据模型（Prisma）

| 文件 | 路径 | 职责 |
|------|------|------|
| Prisma Schema | `prisma/schema.prisma` | 数据源配置（postgresql）、17 个 model 定义（SysDict/SysDictItem/SysUser/SysRole/SysUserRole/WorkBase/WorkDetail/WorkImage/WorkTeam/WorkStatistic/WorkHonor/WorkAuditLog/WorkTag/WorkTagRelation/WorkLike/SysAuthLog/SysOperationLog/Account/Session/VerificationToken）、表映射与索引 |
| 种子数据入口 | `prisma/seed.ts` | 初始化系统角色（root/admin/common）、系统字典（audit_status/dev_status/category_code/honor_type/banned_users/blocked_email_domains）、默认管理员账号（trae/trae1234）、国家城市数据导入、addItem 幂等 upsert 辅助函数 |
| 国家城市数据 | `prisma/seed-data-countries.ts` | 国家和城市字典项数据（country/city dictCode） |

### 认证模块

| 文件 | 路径 | 职责 |
|------|------|------|
| NextAuth 配置 | `src/lib/auth-nextauth.ts` | NextAuth v5 配置：PrismaAdapter、Credentials provider、authorize 回调（bcrypt 校验+封禁检查）、jwt/session callbacks、signIn event（日志+更新lastSignInAt）、signIn 页面路径 |
| 认证工具 | `src/lib/auth.ts` | AuthUser 类型定义、getAuthUser()（从 session 获取用户及角色）、hasAnyRole()、isAdmin()（判断 admin/root 角色） |
| 封禁管理 | `src/lib/ban.ts` | clearBanCache()/getBannedUserIds()/isUserBanned()/banUser()/unbanUser()/isEmailDomainBlocked()、字典复用（banned_users/blocked_email_domains）、60秒内存缓存、自动 ensureDict |
| NextAuth 路由 | `src/app/api/auth/[...nextauth]/route.ts` | 导出 handlers.GET 和 handlers.POST |
| 注册 API | `src/app/api/auth/register/route.ts` | POST 注册：邮箱/密码/用户名校验、域名屏蔽检查、邮箱唯一检查、bcrypt hash（salt=10）、分配 common 角色、记录注册日志 |

### API 路由

| 文件 | 路径 | 职责 |
|------|------|------|
| 作品列表/更新 | `src/app/api/works/route.ts` | GET 作品列表（分页/搜索/筛选/排序/i18n标签解析）、PUT 更新作品（权限校验/zod校验/sanitize/事务多表更新） |
| 作品详情 | `src/app/api/works/[id]/route.ts` | GET 作品详情（权限检查/i18n解析/HTML sanitize/完整关联数据） |
| 点赞切换 | `src/app/api/works/[id]/like/route.ts` | POST 切换点赞（事务：创建/删除WorkLike + likeCount增减 + 操作日志） |
| 浏览计数 | `src/app/api/works/[id]/view/route.ts` | POST 记录浏览量（upsert WorkStatistic viewCount+1） |
| 作品统计 | `src/app/api/works/[id]/stats/route.ts` | GET 作品统计（viewCount/likeCount/当前用户是否已赞） |
| 我的点赞 | `src/app/api/works/likes/route.ts` | GET 当前用户点赞作品列表（分页） |
| 筛选项 | `src/app/api/works/filter-options/route.ts` | GET 筛选项（countries/cities/categories/honors，仅返回有审核通过作品的项） |
| 筛选项排序 | `src/app/api/works/filter-options/sort-filter-options.ts` | sortFilterOptions 函数（sortOrder升序 → label.localeCompare） |
| 提交作品 | `src/app/api/submit/route.ts` | POST 提交新作品（zod校验/sanitize/事务五表创建/自动审核逻辑/操作日志） |
| 标签管理 | `src/app/api/tags/route.ts` | GET 标签列表（分页/搜索/筛选）、POST/PUT/DELETE 标签 CRUD |
| 所有标签 | `src/app/api/tags/all/route.ts` | GET 所有标签（不分页，按id升序） |
| 用户管理 | `src/app/api/users/route.ts` | GET 用户列表（管理员，含封禁状态）、POST 创建用户、PUT 更新用户（含角色更新，禁止分配root）、DELETE 删除用户 |
| 用户封禁 | `src/app/api/users/[id]/ban/route.ts` | POST 封禁/解封用户（禁止封禁admin/root） |
| 角色管理 | `src/app/api/roles/route.ts` | GET 角色列表（管理员），POST/PUT/DELETE 返回 403（角色固定） |
| 字典管理 | `src/app/api/dictionaries/route.ts` | GET 字典列表（分页/搜索/筛选/lang解析）、POST/PUT/DELETE 字典/字典项 CRUD（type: dict/item） |
| 文件上传 | `src/app/api/file/route.ts` | POST 上传图片到 COS（5MB限制/jpg/png/webp/gif）、DELETE 删除 COS 文件 |
| 头像上传 | `src/app/api/avatar/route.ts` | POST 上传头像（2MB限制/jpg/png/webp/svg）、自动更新 avatarUrl |
| 个人资料 | `src/app/api/profile/route.ts` | GET 当前用户资料（含角色/作品统计）、PUT 更新资料（username/bio/phone） |
| 公开主页 | `src/app/api/profile/[id]/route.ts` | GET 公开用户主页（已审核可见作品+统计） |
| 修改密码 | `src/app/api/profile/change-password/route.ts` | POST 修改密码（旧密码验证/新密码校验/bcrypt更新） |
| 排行榜 | `src/app/api/rankings/route.ts` | GET 排行榜数据（城市Top20/作品浏览点赞Top20/创作者Top20/7天趋势Top20） |
| 认证日志 | `src/app/api/logs/auth/route.ts` | GET 认证日志列表（管理员，分页/搜索/筛选/日期范围） |
| 操作日志 | `src/app/api/logs/operations/route.ts` | GET 操作日志列表（管理员，分页/搜索/筛选/模块/日期范围，返回modules列表） |
| 管理概览 | `src/app/api/console/overview/route.ts` | GET 管理后台概览统计（7/30天窗口：stats/trend/distribution/latestActivities，原生SQL聚合） |
| 管理作品 | `src/app/api/console/works/route.ts` | GET 作品管理列表（权限区分/多条件筛选）、POST 创建作品、PUT 更新作品（含批量审核/单个审核/标签/荣誉/团队）、DELETE 删除作品 |
| 点赞用户 | `src/app/api/console/works/[id]/likes/route.ts` | GET 作品点赞用户列表（管理员，用于排查刷量） |
| 城市统计 | `src/app/api/console/cities/stats/route.ts` | GET 城市统计（totalWorks/approvedCount/pendingCount/totalViews/totalLikes） |

### 工具模块（lib/）

| 文件 | 路径 | 职责 |
|------|------|------|
| Prisma 单例 | `src/lib/prisma.ts` | prisma 实例（globalThis 缓存防热重载多连接），开发环境日志 query/error/warn，生产环境 error |
| COS 客户端 | `src/lib/cos.ts` | cos-nodejs-sdk-v5 实例（COS_SECRET_ID/COS_SECRET_KEY）、COS_BUCKET/COS_REGION 常量导出 |
| CRUD 常量 | `src/lib/crud.ts` | CRUD_QUERY_PARAMS 常量、DICT_FILTERS/TAG_FILTERS、normalizeFilter 函数 |
| 工具函数 | `src/lib/utils.ts` | cn() 函数（clsx + tailwind-merge） |
| 审计日志 | `src/lib/audit-log.ts` | writeAuthLog()/writeOperationLog()：normalizeId/getHeaderValue/getClientIp/toSafeJson/getRequestMeta 辅助函数，try-catch 不抛异常 |
| 富文本处理 | `src/lib/rich-text.ts` | RICH_TEXT_SANITIZE_OPTIONS 白名单配置（p/br/strong/em/u/s/h2/h3/ul/ol/li/a/blockquote/code）、stripHtmlTags()、sanitizeRichText() |
| 表单校验 | `src/lib/work-form.ts` | WorkFormValues 接口、buildWorkFormSchema(t, options) zod schema 构建函数（含所有字段校验规则） |
| 类型定义 | `src/lib/types.ts` | Work/SubmissionFormData/Tag/DictionaryItem 前端类型接口 |
| Zustand Store | `src/lib/works-store.ts` | useWorksStore：listCache/detailCache 双 Map 缓存、setListCache/setDetailCache/getDetailCache 命令式操作 |
| 反馈 Hook | `src/lib/use-feedback.ts` | useFeedback(timeout=2500) Hook：{ feedback, showFeedback }，自动清除 |
| React Query Hook | `src/lib/use-works.ts` | useWorks(params) Hook：useQuery(['works', params])，staleTime=2分钟，请求 /api/works |
| 语言路由 | `src/lib/language/routing.ts` | routing 配置：locales=['zh-CN','en-US','ja-JP']、defaultLocale='zh-CN' |
| 语言请求 | `src/lib/language/request.ts` | getRequestConfig 配置，动态 import 翻译文件 |
| 语言导航 | `src/lib/language/navigation.ts` | createNavigation(routing) 生成 Link/redirect/usePathname/useRouter/getPathname |

### 前端组件

| 文件 | 路径 | 职责 |
|------|------|------|
| 根布局 | `src/app/layout.tsx` | 空壳布局，仅返回 children（html/body 在 [language]/layout.tsx 渲染） |
| 语言布局 | `src/app/[language]/layout.tsx` | 渲染 html/body（per-locale lang 属性）、加载字体（Inter/Noto_Sans_SC/JetBrains_Mono）、Provider 嵌套（SessionProvider→QueryProvider→NextIntlClientProvider→SiteLayout）、Toaster（sonner）、metadata（TRAE DEMO WALL） |
| 首页 | `src/app/[language]/page.tsx` | 首页（作品列表展示） |
| 管理后台布局 | `src/app/[language]/console/layout.tsx` | 管理后台布局 |
| 管理后台概览 | `src/app/[language]/console/page.tsx` | 管理后台概览页 |
| 认证日志页 | `src/app/[language]/console/auth-logs/page.tsx` | 认证日志查看页 |
| 城市管理页 | `src/app/[language]/console/cities/page.tsx` | 城市统计页 |
| 字典管理页 | `src/app/[language]/console/dictionaries/page.tsx` | 字典管理页 |
| 操作日志页 | `src/app/[language]/console/operation-logs/page.tsx` | 操作日志查看页 |
| 角色管理页 | `src/app/[language]/console/roles/page.tsx` | 角色管理页 |
| 标签管理页 | `src/app/[language]/console/tags/page.tsx` | 标签管理页 |
| 用户管理页 | `src/app/[language]/console/users/page.tsx` | 用户管理页 |
| 作品管理页 | `src/app/[language]/console/works/page.tsx` | 作品审核管理页 |
| 个人资料页 | `src/app/[language]/profile/page.tsx` | 个人资料编辑页 |
| 排行榜页 | `src/app/[language]/rankings/page.tsx` | 排行榜展示页 |
| 登录页 | `src/app/[language]/sign-in/[[...sign-in]]/page.tsx` | 登录页面 |
| 注册页 | `src/app/[language]/sign-up/[[...sign-up]]/page.tsx` | 注册页面 |
| 提交作品页 | `src/app/[language]/submit/page.tsx` | 作品提交页面入口 |
| 提交表单 | `src/app/[language]/submit/submission-form.tsx` | 四步提交表单容器 |
| 富文本编辑器 | `src/app/[language]/submit/editor/RichTextEditor.tsx` | Tiptap 富文本编辑器组件（Link/Underline/Placeholder 扩展） |
| 步骤指示器 | `src/app/[language]/submit/steps/StepIndicator.tsx` | 四步向导步骤指示器 |
| 步骤1-基本信息 | `src/app/[language]/submit/steps/Step1BasicInfo.tsx` | 基本信息填写（标题/简介/国家/城市/分类/开发状态/标签/封面） |
| 步骤2-视觉素材 | `src/app/[language]/submit/steps/Step2VisualAssets.tsx` | 视觉素材上传（截图） |
| 步骤3-内容介绍 | `src/app/[language]/submit/steps/Step3Content.tsx` | 内容填写（story富文本/highlights/scenarios/demoUrl/repoUrl） |
| 步骤4-团队信息 | `src/app/[language]/submit/steps/Step4Team.tsx` | 团队信息填写（成员/团队介绍/联系方式） |
| 用户公开主页 | `src/app/[language]/user/[id]/page.tsx` | 用户公开主页 |
| 作品详情页 | `src/app/[language]/works/[id]/page.tsx` | 作品详情展示页 |
| 作品编辑页 | `src/app/[language]/works/edit/[id]/page.tsx` | 作品编辑页面 |
| 登录表单 | `src/components/auth/sign-in-form.tsx` | 登录表单组件 |
| 注册表单 | `src/components/auth/sign-up-form.tsx` | 注册表单组件 |
| 操作按钮 | `src/components/common/action-button.tsx` | 通用操作按钮 |
| 表单选择器 | `src/components/common/form-select.tsx` | 通用表单选择组件 |
| Hero 横幅 | `src/components/common/hero-banner.tsx` | 首页 Hero Banner |
| 加载遮罩 | `src/components/common/loading-overlay.tsx` | 加载状态遮罩 |
| Query Provider | `src/components/common/query-provider.tsx` | React QueryClientProvider 封装 |
| CRUD 反馈 | `src/components/crud/crud-feedback.tsx` | CRUD 操作反馈组件 |
| CRUD 筛选栏 | `src/components/crud/crud-filter-bar.tsx` | CRUD 通用筛选栏 |
| CRUD 分页 | `src/components/crud/crud-pagination.tsx` | CRUD 通用分页组件 |
| 粒子背景 | `src/components/layout/particles-background.tsx` | @tsparticles/react 粒子动效背景 |
| 站点布局 | `src/components/layout/site-layout.tsx` | 站点整体布局（导航/内容区/页脚） |
| Badge | `src/components/ui/badge.tsx` | 徽章组件（shadcn/ui） |
| Button | `src/components/ui/button.tsx` | 按钮组件（shadcn/ui） |
| Card | `src/components/ui/card.tsx` | 卡片组件（shadcn/ui） |
| Checkbox | `src/components/ui/checkbox.tsx` | 复选框组件（shadcn/ui） |
| DatePicker | `src/components/ui/date-picker.tsx` | 日期选择器组件 |
| Dialog | `src/components/ui/dialog.tsx` | 对话框组件（shadcn/ui） |
| 点状光晕背景 | `src/components/ui/dotted-glow-background.tsx` | 装饰性点状光晕背景 |
| Input | `src/components/ui/input.tsx` | 输入框组件（shadcn/ui） |
| Label | `src/components/ui/label.tsx` | 标签组件（shadcn/ui） |
| Select | `src/components/ui/select.tsx` | 选择器组件（shadcn/ui） |
| Textarea | `src/components/ui/textarea.tsx` | 文本域组件（shadcn/ui） |
| 城市筛选 | `src/components/work/city-filter.tsx` | 作品列表城市筛选组件 |
| 编辑表单 | `src/components/work/edit-form.tsx` | 作品编辑表单 |
| 收藏作品 | `src/components/work/liked-works.tsx` | 用户点赞/收藏作品列表 |
| 作品卡片 | `src/components/work/work-card.tsx` | 作品卡片展示组件 |
| 作品管理 | `src/components/work/works-management.tsx` | 管理后台作品管理组件 |

### 中间件

| 文件 | 路径 | 职责 |
|------|------|------|
| 中间件 | `src/middleware.ts` | NextAuth auth wrapper + 三层中间件链：/api/auth 放行 → isProtectedRoute 未登录重定向 → /api 跳过i18n → 其余交给 next-intl middleware；matcher 跳过静态资源，始终匹配 /api 和 /trpc |

### 国际化（i18n）

| 文件 | 路径 | 职责 |
|------|------|------|
| 中文翻译 | `src/assets/translations/zh-CN.json` | 简体中文翻译文件 |
| 英文翻译 | `src/assets/translations/en-US.json` | 英文翻译文件 |
| 日文翻译 | `src/assets/translations/ja-JP.json` | 日文翻译文件 |
| 品牌资源 | `src/assets/brand/` | logo.png、logo.svg、品牌资源说明 |

### COS 对象存储

| 文件 | 路径 | 职责 |
|------|------|------|
| COS SDK 配置 | `src/lib/cos.ts` | cos-nodejs-sdk-v5 初始化（环境变量密钥）、COS_BUCKET/COS_REGION 导出 |
| 文件上传 API | `src/app/api/file/route.ts` | POST 服务端代理上传到 COS（路径 uploads/{date}/{uuid}.{ext}、5MB、图片类型白名单）、DELETE 删除 COS 对象（支持 path/url 参数解析 Key） |
| 头像上传 API | `src/app/api/avatar/route.ts` | POST 头像上传（路径 avatars/{userId}-{timestamp}.{ext}、2MB、jpg/png/webp/svg）、自动更新 SysUser.avatarUrl |

### Docker 部署

| 文件 | 路径 | 职责 |
|------|------|------|
| Dockerfile | `Dockerfile` | 三阶段构建：base（node:20-slim + openssl，清华镜像源）→ builder（python3/make/g++ 构建依赖、npm ci、prisma generate、next build）→ runner（standalone 输出 + .next/static + prisma + node_modules）；构建参数传入 COS/NEXTAUTH 环境变量，DATABASE_URL 占位 |
| 启动脚本 | `entrypoint.sh` | RUN_DB_INIT=true 时等待DB端口→prisma db push --accept-data-loss→seed（失败不中断）；START_SERVER≠true 则退出；否则 node server.js 启动 |
| Docker Compose（开发） | `docker-compose.yml` | 五服务编排：app（3000端口，依赖app-init）、app-init（初始化容器，restart:no）、db（postgres:16-alpine，5432端口，性能调优）、db-dev（postgres:16-alpine，5433端口）、redis（redis:7-alpine，6379端口，256MB LRU）、nginx（nginx:alpine，80端口，反向代理） |
| Docker Compose（2C8G） | `docker-compose.2c8g.yml` | 2核8G低配服务器配置 |
| Docker Compose（生产） | `docker-compose.prod.yml` | 生产环境配置 |
| Nginx 配置 | `nginx.conf` | 反向代理到 app:3000 的 Nginx 配置 |
| Nginx 负载均衡 | `nginx-lb.conf` | 负载均衡配置（多实例） |
| Nginx 负载均衡2 | `nginx-lb-2.conf` | 另一种负载均衡配置 |
| 环境变量示例 | `.env.example` | 开发环境变量模板（DATABASE_URL/NEXTAUTH_SECRET/COS_*） |
| Docker 环境示例 | `.env.docker.example` | Docker 环境变量模板 |
| Docker 忽略 | `.dockerignore` | Docker 构建忽略文件 |
