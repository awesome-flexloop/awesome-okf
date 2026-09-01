# Demo Wall Intl 源码事实清单

R阶段产出：编号事实清单 F-001~F-095，零推测纯客观描述。
> 本清单基于中文版 demo-wall 的核心架构，标注国际版独有差异。与中文版共享的事实以「同中文版」标注，差异点以「【intl差异】」标注。

---

## a. 项目基本信息

**F-001**: 项目名称为 `dem`（中文版为 `trae-co-creation-demo-wall`），private 为 true。【intl差异】文件：package.json

**F-002**: 核心框架依赖同中文版：`next@^15.3.3`、`react@^18.3.1`、`react-dom@^18.3.1`。

**F-003**: 认证依赖同中文版：`next-auth@^5.0.0-beta.30`、`@auth/prisma-adapter@^2.11.1`、`bcryptjs@^3.0.3`。

**F-004**: 国际化依赖同中文版：`next-intl@^4.8.3`。

**F-005**: 数据库 ORM 同中文版：`prisma@5.10.2`、`@prisma/client@5.10.2`，provider 为 `postgresql`。

**F-006**: UI 组件依赖同中文版：Radix UI、lucide-react、class-variance-authority、tailwind-merge、clsx、sonner。

**F-007**: 富文本编辑器依赖同中文版：Tiptap 全家桶 + sanitize-html。

**F-008**: 状态管理与数据获取同中文版：zustand、@tanstack/react-query、react-hook-form、@hookform/resolvers。

**F-009**: 对象存储依赖同中文版：`cos-nodejs-sdk-v5`（腾讯云 COS SDK）。

**F-010**: 校验依赖同中文版：`zod@^4.3.6`。

**F-011**: 【intl差异】新增依赖 `@vercel/edge-config@^1.4.3`（Vercel Edge Config SDK），中文版无此依赖。文件：package.json#L43

**F-012**: 【intl差异】缺少 qrcode、qrcode-generator 依赖（中文版有）。

**F-013**: npm scripts 定义同中文版，包含 dev/build/postinstall/start/lint/seed/test:* 等。

---

## b. 目录结构

**F-014**: src/ 下一级目录同中文版：`app/`、`assets/`、`components/`、`lib/`、`middleware.ts`。

**F-015**: src/app/ 结构同中文版，但新增 `/api/sync-edge-config/` 和 `/api/console/works/export/` 路由。

**F-016**: 【intl差异】src/lib/ 下新增 `edge-config.ts` 文件，无 `ban.ts` 文件。

**F-017**: src/app/api/users/ 下无 `[id]/ban/` 子目录（中文版有封禁路由）。【intl差异】

**F-018**: 【intl差异】src/assets/ 下无 `brand/` 目录（中文版有 brand/logo.png、brand/logo.svg）。翻译文件包含 5 个：en-US.json、zh-CN.json、ja-JP.json、id-ID.json、vi-VN.json。

**F-019**: 【intl差异】项目根目录存在 `test/` 目录（含 filter-options-sort.test.ts），中文版无此目录。

**F-020**: 【intl差异】存在 `.github/workflows/sync-cnb.yml` CI 工作流文件。

---

## c. 数据模型（Prisma）

**F-021**: Prisma schema 定义的 model 集合基本同中文版，但外键策略有差异。【intl差异】

**F-022**: Work 五表垂直分表模型同中文版：WorkBase、WorkDetail、WorkImage、WorkTeam、WorkStatistic。

**F-023**: RBAC 模型同中文版：SysUser、SysRole、SysUserRole，三角色 root/admin/common。

**F-024**: 字典驱动模型同中文版：SysDict/SysDictItem，支持 labelI18n 多语言标签。

**F-025**: 审核与日志模型同中文版：WorkAuditLog、SysAuthLog、SysOperationLog。

**F-026**: 【intl差异】SysAuthLog 的 user 关系 onDelete 为 SetNull（中文版为 Cascade）。文件：schema.prisma#L380

**F-027**: 【intl差异】SysOperationLog 的 operator 关系 onDelete 为 SetNull（中文版为 Cascade）。文件：schema.prisma#L405

**F-028**: 【intl差异】DateTime 字段精度为 @db.Timestamptz（无精度参数 6）；中文版为 @db.Timestamptz(6)。

**F-029**: seed 数据同中文版（系统字典、角色、默认管理员、国家城市数据）。

---

## d. 认证系统

**F-030**: NextAuth 配置同中文版：PrismaAdapter + JWT session 策略，Credentials provider。

**F-031**: 【intl差异】authorize 回调不检查 isUserBanned（中文版检查封禁状态并在封禁时返回 null）。文件：auth-nextauth.ts#L16-L44

**F-032**: 【intl差异】jwt callback 不做封禁检查和 token.id 清空（中文版在 Node.js runtime 下检查封禁状态并清空 token）。

**F-033**: session callback 同中文版：将 token.id 赋值给 session.user.id。

**F-034**: signIn event 同中文版：写入认证日志，更新 lastSignInAt。

**F-035**: auth.ts 导出同中文版：AuthUser 类型、getAuthUser()、hasAnyRole()、isAdmin()。

**F-036**: 【intl差异】注册 API 不检查 isEmailDomainBlocked（因无 ban.ts 模块）。

---

## e. API 路由

**F-037**: 核心 CRUD API 同中文版：/api/works（GET列表/PUT更新）、/api/works/[id]（GET详情）、/api/works/[id]/like、/api/works/[id]/view、/api/works/[id]/stats、/api/works/likes、/api/works/filter-options、/api/submit。

**F-038**: 管理后台 API 同中文版：/api/console/overview、/api/console/works、/api/console/works/[id]/likes、/api/console/cities/stats、/api/dictionaries、/api/tags、/api/users、/api/roles、/api/logs/auth、/api/logs/operations。

**F-039**: 【intl差异】无 /api/users/[id]/ban 路由（移除用户封禁功能）。

**F-040**: 文件上传 API 同中文版：/api/file（COS上传/删除）、/api/avatar（头像上传）。

**F-041**: 个人资料 API 同中文版：/api/profile、/api/profile/[id]、/api/profile/change-password。

**F-042**: 排行榜 API 同中文版：/api/rankings。

**F-043**: 【intl差异】新增 POST /api/sync-edge-config 路由，将 country/city/category/honor 字典数据 PATCH 到 Vercel Edge Config，需要 EDGE_CONFIG_ID 和 VERCEL_API_TOKEN 环境变量。文件：sync-edge-config/route.ts

**F-044**: 【intl差异】新增 GET /api/console/works/export 路由，导出作品为 CSV（管理员），支持 ids 参数或筛选条件导出，硬上限 5000 条，带 UTF-8 BOM，文件名 works_export_YYYYMMDD_HHMMSS.csv。文件：export/route.ts

---

## f. 工具模块（lib/）

**F-045**: prisma 单例、cos 实例、crud 工具、utils、audit-log、rich-text、work-form、types、works-store（zustand）、use-feedback、use-works（react-query）均同中文版。

**F-046**: 【intl差异】无 ban.ts 模块（移除用户封禁和邮箱域名屏蔽功能，中文版 ban.ts 提供 clearBanCache/getBannedUserIds/isUserBanned/banUser/unbanUser/isEmailDomainBlocked 及 60 秒内存缓存）。

**F-047**: 【intl差异】新增 edge-config.ts，导出 getDictionaries() 函数，使用 @vercel/edge-config 的 get('dictionaries') 获取缓存的字典数据，失败时返回 null（优雅降级）。文件：edge-config.ts

**F-048**: 【intl差异】language/routing.ts 配置 locales 为 ['en-US', 'zh-CN', 'ja-JP', 'id-ID', 'vi-VN']，defaultLocale 为 'en-US'（中文版为 ['zh-CN', 'en-US', 'ja-JP']，默认 'zh-CN'）。文件：routing.ts#L3-L6

---

## g. 中间件

**F-049**: 中间件使用 next-auth 的 auth() wrapper 包裹，同中文版。

**F-050**: 【intl差异·注意】isProtectedRoute 正则仍为 `/^\/(zh-CN|en-US)\/(submit|console|profile)/`，未包含 id-ID 和 vi-VN 语言前缀（与中文版相同，这是一个已知限制——新增语言的受保护路由可能无法正确触发认证检查）。文件：middleware.ts#L9-L11

**F-051**: 中间件其余逻辑同中文版：/api/auth 放行、受保护路由未登录重定向、/api 路径跳过 i18n 中间件、其余路径交给 next-intl middleware。

---

## h. 前端架构

**F-052**: 前端架构同中文版：App Router 双层 layout（根 layout 仅返回 children，[language]/layout 渲染 html/body + Provider 嵌套）。

**F-053**: Provider 嵌套顺序同中文版：SessionProvider → QueryProvider → NextIntlClientProvider → SiteLayout + Toaster。

**F-054**: UI 框架同中文版：Tailwind CSS（darkMode: class）、shadcn/ui、Radix UI、lucide-react，品牌绿色板。

**F-055**: 状态管理三层分离同中文版：Prisma 服务端 CRUD、zustand 客户端缓存、react-query 服务端数据获取（staleTime=2分钟）。

---

## i. 国际化

**F-056**: 【intl差异】支持 5 种语言：en-US（默认）、zh-CN、ja-JP、id-ID（印尼语）、vi-VN（越南语）；中文版支持 3 种，默认 zh-CN。

**F-057**: 翻译文件 5 个：en-US.json、zh-CN.json、ja-JP.json、id-ID.json、vi-VN.json；中文版为 3 个。

**F-058**: URL 结构同中文版：/{locale}/...，使用 next-intl [language] 动态路由段。

**F-059**: 字典数据 labelI18n 多语言机制同中文版，API 根据 lang 参数选择对应语言标签。

---

## j. COS 存储

**F-060**: COS 存储方案同中文版：环境变量配置、文件/头像上传路径规则、类型/大小限制、删除 API。

---

## k. Docker 部署

**F-061**: Dockerfile 三阶段构建同中文版：base → builder → runner。

**F-062**: 【intl差异】构建阶段使用 `npm install`（中文版使用 `npm ci`，npm ci 更严格要求 lockfile 一致，npm install 更宽松）。文件：Dockerfile#L51

**F-063**: entrypoint.sh 逻辑同中文版：可选 DB 初始化 + seed + 启动 server。

**F-064**: 【intl差异】entrypoint.sh 中 prisma db push 不带 `--accept-data-loss` 参数（中文版带此参数，允许非破坏性 schema 变更时自动接受数据丢失风险）。文件：entrypoint.sh#L13

**F-065**: docker-compose.yml 服务定义同中文版（app、app-init、db、redis），但【intl差异】不含 nginx 服务（中文版有 nginx 反向代理和端口 80 映射，intl 版直接暴露 3000 端口，面向 Vercel 部署优化）。

**F-066**: 【intl差异】next.config.ts 的 outputFileTracingExcludes 注释说明是为了避免 Vercel Lambda 100MB 限制（中文版注释是减小 Docker 镜像体积），体现部署目标从 Docker 转向 Vercel。文件：next.config.ts#L9-L11

---

## l. Vercel Edge Config 缓存层（intl 新增）

**F-067**: Edge Config 缓存的目标是将字典数据（country/city/category/honor）从数据库查询前移到 Vercel 边缘网络，降低冷启动数据库查询延迟。这是面向海外 Vercel 部署的性能优化。

**F-068**: 缓存同步机制为管理员手动触发 POST /api/sync-edge-config，将四类字典序列化后（BigInt 转 string）通过 Vercel API PATCH 到 Edge Config。

**F-069**: 缓存读取通过 getDictionaries() 函数，使用 @vercel/edge-config SDK，失败时返回 null 实现优雅降级（回退到数据库查询）。

---

## m. CSV 导出功能（intl 新增）

**F-070**: CSV 导出为管理员功能，支持选中导出（ids 参数）和按筛选条件导出。

**F-071**: 导出硬上限 5000 条防止内存溢出，包含 UTF-8 BOM 以兼容 Excel 直接打开。

**F-072**: CSV 导出包含完整作品字段及 i18n 标签解析，审核状态和展示状态映射为中文标签（AUDIT_STATUS_LABEL/DISPLAY_STATUS_LABEL），包含 escapeCsv 防注入处理。

---

## n. 测试与 CI

**F-073**: 【intl差异】存在 test/filter-options-sort.test.ts 单元测试文件（中文版无此测试）。

**F-074**: 【intl差异】存在 .github/workflows/sync-cnb.yml CI 工作流（中文版有 .github/ISSUE_TEMPLATE/ 但无此 CI 配置）。
