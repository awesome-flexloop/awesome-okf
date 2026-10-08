---
type: spec
title: "Demo Wall 源码事实清单"
---

# Demo Wall 源码事实清单

R阶段产出：编号事实清单 F-001~F-xxx，零推测纯客观描述

---

## a. 项目基本信息

**F-001**: 项目名称为 `trae-co-creation-demo-wall`，private 为 true，版本 `0.0.0`。文件：package.json

**F-002**: 核心框架依赖：`next@^15.3.3`、`react@^18.3.1`、`react-dom@^18.3.1`。文件：package.json

**F-003**: 认证依赖：`next-auth@^5.0.0-beta.30`、`@auth/prisma-adapter@^2.11.1`、`bcryptjs@^3.0.3`。文件：package.json

**F-004**: 国际化依赖：`next-intl@^4.8.3`。文件：package.json

**F-005**: 数据库 ORM：`prisma@5.10.2`（devDependencies）、`@prisma/client@5.10.2`（devDependencies）。数据源 provider 为 `postgresql`。文件：package.json、schema.prisma

**F-006**: UI 组件依赖：`@radix-ui/react-checkbox@^1.3.3`、`@radix-ui/react-dialog@^1.1.15`、`@radix-ui/react-label@^2.1.8`、`@radix-ui/react-select@^2.2.6`、`@radix-ui/react-separator@^1.1.7`、`@radix-ui/react-slot@^1.1.2`、`lucide-react@^0.511.0`、`class-variance-authority@^0.7.1`、`tailwind-merge@^3.0.2`、`clsx@^2.1.1`、`sonner@^2.0.7`。文件：package.json

**F-007**: 富文本编辑器依赖：`@tiptap/react@^3.20.4`、`@tiptap/starter-kit@^3.20.4`、`@tiptap/extension-link@^3.20.4`、`@tiptap/extension-placeholder@^3.20.4`、`@tiptap/extension-underline@^3.20.4`、`sanitize-html@^2.17.2`。文件：package.json

**F-008**: 状态管理与数据获取：`zustand@^5.0.3`、`@tanstack/react-query@^5.95.2`、`react-hook-form@^7.71.2`、`@hookform/resolvers@^5.2.2`。文件：package.json

**F-009**: 对象存储依赖：`cos-nodejs-sdk-v5@^2.15.4`（腾讯云 COS SDK）。文件：package.json

**F-010**: 校验依赖：`zod@^4.3.6`。文件：package.json

**F-011**: 其他依赖：`@supabase/supabase-js@^2.98.0`、`@tsparticles/react@^3.0.0`、`@tsparticles/slim@^3.9.1`、`pg@^8.19.0`、`qrcode@^1.5.4`、`qrcode-generator@^2.0.4`、`uuid@^13.0.0`、`svix@^1.86.0`。文件：package.json

**F-012**: npm scripts 定义：`dev: next dev`、`build: prisma generate && next build`、`postinstall: prisma generate`、`start: next start`、`lint: eslint .`、`seed: tsx prisma/seed.ts`、`test:docker-deps`、`test:docker-runtime`、`test:seed`、`test:deploy-config`。文件：package.json

**F-013**: prisma seed 配置：`"seed": "tsx prisma/seed.ts"`。文件：package.json

**F-014**: optionalDependencies 包含 `@parcel/watcher-linux-x64-glibc@2.5.6` 和 `@swc/core-linux-x64-gnu@1.15.18`。文件：package.json

---

## b. 目录结构

**F-015**: src/ 下一级目录为：`app/`、`assets/`、`components/`、`lib/`、`middleware.ts`。文件：目录结构 src/

**F-016**: src/app/ 下包含 `[language]/`（动态语言路由）、`api/`、`layout.tsx`。文件：目录结构 src/app/

**F-017**: src/app/[language]/ 下包含页面路由：`page.tsx`（首页）、`layout.tsx`、`console/`（管理后台）、`profile/`（个人资料）、`rankings/`（排行榜）、`sign-in/[[...sign-in]]/page.tsx`、`sign-up/[[...sign-up]]/page.tsx`、`submit/`（提交作品）、`user/[id]/`（用户公开主页）、`works/[id]/`（作品详情）、`works/edit/[id]/`（编辑作品）。文件：目录结构 [src/app/[language]/](file:///d:/spaces/SpecWeave/external/libs/ai/trae-community/trae-co-creation-demo-wall/src/app/[language]/)

**F-018**: src/app/[language]/console/ 下包含：`page.tsx`（概览）、`layout.tsx`、`auth-logs/page.tsx`、`cities/page.tsx`、`dictionaries/page.tsx`、`operation-logs/page.tsx`、`roles/page.tsx`、`tags/page.tsx`、`users/page.tsx`、`works/page.tsx`。文件：目录结构 [src/app/[language]/console/](file:///d:/spaces/SpecWeave/external/libs/ai/trae-community/trae-co-creation-demo-wall/src/app/[language]/console/)

**F-019**: src/app/[language]/submit/ 下包含：`page.tsx`、`submission-form.tsx`、`editor/RichTextEditor.tsx`、`steps/Step1BasicInfo.tsx`、`steps/Step2VisualAssets.tsx`、`steps/Step3Content.tsx`、`steps/Step4Team.tsx`、`steps/StepIndicator.tsx`。文件：目录结构 [src/app/[language]/submit/](file:///d:/spaces/SpecWeave/external/libs/ai/trae-community/trae-co-creation-demo-wall/src/app/[language]/submit/)

**F-020**: src/app/api/ 下包含路由目录：`auth/[...nextauth]/`、`auth/register/`、`avatar/`、`console/overview/`、`console/cities/stats/`、`console/works/`、`console/works/[id]/likes/`、`dictionaries/`、`file/`、`logs/auth/`、`logs/operations/`、`profile/`、`profile/[id]/`、`profile/change-password/`、`rankings/`、`roles/`、`submit/`、`tags/`、`tags/all/`、`users/`、`users/[id]/ban/`、`works/`、`works/[id]/`、`works/[id]/like/`、`works/[id]/stats/`、`works/[id]/view/`、`works/filter-options/`、`works/likes/`。文件：目录结构 src/app/api/

**F-021**: src/components/ 下包含子目录：`auth/`（sign-in-form.tsx、sign-up-form.tsx）、`common/`（action-button.tsx、form-select.tsx、hero-banner.tsx、loading-overlay.tsx、query-provider.tsx）、`crud/`（crud-feedback.tsx、crud-filter-bar.tsx、crud-pagination.tsx）、`layout/`（particles-background.tsx、site-layout.tsx）、`ui/`（badge.tsx、button.tsx、card.tsx、checkbox.tsx、date-picker.tsx、dialog.tsx、dotted-glow-background.tsx、input.tsx、label.tsx、select.tsx、textarea.tsx）、`work/`（city-filter.tsx、edit-form.tsx、liked-works.tsx、work-card.tsx、works-management.tsx）。文件：目录结构 src/components/

**F-022**: src/lib/ 下包含文件：`auth.ts`、`auth-nextauth.ts`、`prisma.ts`、`cos.ts`、`crud.ts`、`types.ts`、`utils.ts`、`audit-log.ts`、`ban.ts`、`rich-text.ts`、`work-form.ts`、`works-store.ts`、`use-feedback.ts`、`use-works.ts`、`language/request.ts`、`language/routing.ts`、`language/navigation.ts`。文件：目录结构 src/lib/

**F-023**: src/assets/ 下包含：`brand/`（logo.png、logo.svg、README.md）、`translations/`（zh-CN.json、en-US.json、ja-JP.json）、`globals.css`、`logo.svg`。文件：目录结构 src/assets/

**F-024**: prisma/ 下包含：`schema.prisma`、`seed.ts`、`seed-data-countries.ts`、`README.md`。文件：目录结构 prisma/

**F-025**: public/ 下包含：`images/work-placeholder.svg`、`_redirects`、`favicon.svg`、`trae.ico`。

**F-026**: 根目录配置文件：`next.config.ts`、`tsconfig.json`、`tailwind.config.js`、`postcss.config.js`、`eslint.config.js`、`components.json`、`Dockerfile`、`docker-compose.yml`、`docker-compose.2c8g.yml`、`docker-compose.prod.yml`、`entrypoint.sh`、`nginx.conf`、`nginx-lb.conf`、`nginx-lb-2.conf`、`.env.example`、`.env.docker.example`、`.dockerignore`、`.gitignore`、`LICENSE`、`README.md`、`CONTRIBUTING.md`。

---

## c. 数据模型（Prisma）

**F-027**: Prisma schema 共定义 17 个 model：SysDict、SysDictItem、SysUser、SysRole、SysUserRole、WorkBase、WorkDetail、WorkImage、WorkTeam、WorkStatistic、WorkHonor、WorkAuditLog、WorkTag、WorkTagRelation、WorkLike、SysAuthLog、SysOperationLog、Account、Session、VerificationToken。文件：schema.prisma

**F-028**: model SysDict 字段：id(BigInt, PK, autoincrement)、dictCode(String, unique, VarChar(50), @map("dict_code"))、dictName(String, VarChar(50), @map("dict_name"))、description(String?, VarChar(255))、isSystem(Boolean?, default(false), @map("is_system"))、items(SysDictItem[])。@@map("sys_dict")。文件：schema.prisma#L12-L26

**F-029**: model SysDictItem 字段：id(BigInt, PK, autoincrement)、dictCode(String, VarChar(50), @map("dict_code"))、itemLabel(String, VarChar(100), @map("item_label"))、labelI18n(Json?, @map("label_i18n"))、itemValue(String, VarChar(100), @map("item_value"))、parentValue(String?, VarChar(100), @map("parent_value"))、sortOrder(Int?, default(0), @map("sort_order"))、status(Boolean?, default(true))、dict(SysDict, relation on delete Cascade)、workHonors(WorkHonor[])。@@unique([dictCode, itemValue])，@@map("sys_dict_item")。文件：schema.prisma#L29-L51

**F-030**: model SysUser 字段：id(BigInt, PK, autoincrement)、username(String, VarChar(255))、email(String, unique, VarChar(255))、emailVerified(DateTime?, @map("email_verified"), Timestamptz(6))、phone(String?, VarChar(50))、clerk_id(String?, unique, VarChar(255))、passwordHash(String?, @map("password_hash"), VarChar(255))、avatarUrl(String?, @map("avatar_url"), VarChar(255))、bio(String?)、lastSignInAt(DateTime?, @map("last_sign_in_at"), Timestamptz(6))、identities(Json?)、createdAt(DateTime?, default(now), @map("created_at"), Timestamptz(6))、updatedAt(DateTime?, default(now), @updatedAt, @map("updated_at"), Timestamptz(6))。关系：accounts(Account[])、sessions(Session[])、authLogs(SysAuthLog[])、operationLogs(SysOperationLog[])、roles(SysUserRole[])、auditedLogs(WorkAuditLog[] @relation("Auditor"))、works(WorkBase[])、grantedHonors(WorkHonor[] @relation("GrantedBy"))、likes(WorkLike[])。@@map("sys_user")。文件：schema.prisma#L54-L91

**F-031**: model SysRole 字段：id(Int, PK, autoincrement)、roleCode(String, unique, VarChar(50), @map("role_code"))、roleName(String, VarChar(50), @map("role_name"))、description(String?, VarChar(255))、users(SysUserRole[])。@@map("sys_role")。文件：schema.prisma#L94-L106

**F-032**: model SysUserRole 字段：id(BigInt, PK, autoincrement)、userId(BigInt, @map("user_id"))、roleId(Int, @map("role_id"))。关系：role(SysRole, Cascade)、user(SysUser, Cascade)。@@unique([userId, roleId])，@@map("sys_user_role")。文件：schema.prisma#L109-L121

**F-033**: model WorkBase 字段：id(BigInt, PK, autoincrement)、userId(BigInt, @map("user_id"))、title(String, VarChar(255))、summary(String?, VarChar(255))、coverUrl(String?, @map("cover_url"), VarChar(255))、countryCode(String?, @map("country_code"), VarChar(100))、cityCode(String?, @map("city_code"), VarChar(100))、categoryCode(String?, @map("category_code"), VarChar(100))、devStatusCode(String?, @map("dev_status_code"), VarChar(100))、createdAt(DateTime?, default(now), @map("created_at"), Timestamptz(6))、updatedAt(DateTime?, default(now), @updatedAt, @map("updated_at"), Timestamptz(6))。关系：auditLogs(WorkAuditLog[])、user(SysUser, Cascade)、detail(WorkDetail?)、honors(WorkHonor[])、images(WorkImage[])、likes(WorkLike[])、statistic(WorkStatistic?)、tags(WorkTagRelation[])、team(WorkTeam?)。索引：@@index([userId])、@@index([countryCode])、@@index([cityCode])、@@index([categoryCode])。@@map("work_base")。文件：schema.prisma#L124-L162

**F-034**: model WorkDetail 字段：workId(BigInt, PK, @map("work_id"))、story(String?)、highlights(Json?)、scenarios(Json?)、demoUrl(String?, @map("demo_url"), VarChar(255))、repoUrl(String?, @map("repo_url"), VarChar(255))、work(WorkBase, Cascade)。@@map("work_detail")。文件：schema.prisma#L165-L181

**F-035**: model WorkImage 字段：id(BigInt, PK, autoincrement)、workId(BigInt, @map("work_id"))、imageUrl(String, @map("image_url"), VarChar(255))、imageType(String?, @map("image_type"), VarChar(50))、sortOrder(Int?, default(0), @map("sort_order"))、createdAt(DateTime?, default(now), @map("created_at"), Timestamptz(6))、work(WorkBase, Cascade)。@@index([workId])，@@map("work_image")。文件：schema.prisma#L184-L201

**F-036**: model WorkTeam 字段：id(BigInt, PK, autoincrement)、workId(BigInt, unique, @map("work_id"))、teamIntro(String?, @map("team_intro"))、members(Json?)、contactPhone(String?, @map("contact_phone"), VarChar(50))、contactEmail(String?, @map("contact_email"), VarChar(255))、work(WorkBase, Cascade)。@@index([workId])，@@map("work_team")。文件：schema.prisma#L204-L221

**F-037**: model WorkStatistic 字段：workId(BigInt, PK, @map("work_id"))、auditStatus(Int?, default(0), @map("audit_status"))、displayStatus(Int?, default(0), @map("display_status"))、viewCount(BigInt?, default(0), @map("view_count"))、likeCount(BigInt?, default(0), @map("like_count"))、lastAuditAt(DateTime?, @map("last_audit_at"), Timestamptz(6))、work(WorkBase, Cascade)。@@map("work_statistic")。auditStatus 值：0=待审, 1=通过, 2=拒绝。displayStatus 值：0=下架, 1=上架。文件：schema.prisma#L224-L240

**F-038**: model WorkHonor 字段：id(BigInt, PK, autoincrement)、workId(BigInt, @map("work_id"))、honorItemId(BigInt, @map("honor_item_id"))、grantedAt(DateTime?, default(now), @map("granted_at"), Timestamptz(6))、grantedBy(BigInt?, @map("granted_by"))、granter(SysUser? @relation("GrantedBy"))、dictItem(SysDictItem)、work(WorkBase, Cascade)。@@index([workId])，@@map("work_honor")。文件：schema.prisma#L243-L260

**F-039**: model WorkAuditLog 字段：id(BigInt, PK, autoincrement)、workId(BigInt, @map("work_id"))、auditorId(BigInt?, @map("auditor_id"))、prevStatus(Int?, @map("prev_status"))、newStatus(Int?, @map("new_status"))、reason(String?, VarChar(255))、createdAt(DateTime?, default(now), @map("created_at"), Timestamptz(6))、auditor(SysUser? @relation("Auditor"))、work(WorkBase, Cascade)。@@index([workId])，@@map("work_audit_log")。文件：schema.prisma#L263-L283

**F-040**: model WorkTag 字段：id(Int, PK, autoincrement)、name(String, unique, VarChar(100))、isAutoAudit(Boolean?, default(false), @map("is_auto_audit"))、auditStartTime(DateTime?, @map("audit_start_time"), Timestamptz(6))、auditEndTime(DateTime?, @map("audit_end_time"), Timestamptz(6))、works(WorkTagRelation[])。@@map("work_tag")。文件：schema.prisma#L286-L300

**F-041**: model WorkTagRelation 字段：workId(BigInt, @map("work_id"))、tagId(Int, @map("tag_id"))、tag(WorkTag, Cascade)、work(WorkBase, Cascade)。@@id([workId, tagId])，@@map("work_tag_relation")。文件：schema.prisma#L303-L313

**F-042**: model WorkLike 字段：id(BigInt, PK, autoincrement)、userId(BigInt, @map("user_id"))、workId(BigInt, @map("work_id"))、createdAt(DateTime?, default(now), @map("created_at"), Timestamptz(6))、user(SysUser, Cascade)、work(WorkBase, Cascade)。@@unique([userId, workId])、@@index([workId])、@@index([userId])，@@map("work_like")。文件：schema.prisma#L316-L332

**F-043**: model SysAuthLog 字段：id(BigInt, PK, autoincrement)、userId(BigInt?, @map("user_id"))、clerkId(String?, @map("clerk_id"), VarChar(255))、authType(String, @map("auth_type"), VarChar(50))、authChannel(String?, @map("auth_channel"), VarChar(50))、authStatus(String, @map("auth_status"), VarChar(20))、ipAddress(String?, @map("ip_address"), VarChar(64))、userAgent(String?, @map("user_agent"), VarChar(512))、metadata(Json?)、createdAt(DateTime?, default(now), @map("created_at"), Timestamptz(6))、user(SysUser? @relation("UserAuthLogs"))。@@index([userId])、@@index([clerkId])、@@index([authType])、@@index([createdAt])，@@map("sys_auth_log")。文件：schema.prisma#L334-L352

**F-044**: model SysOperationLog 字段：id(BigInt, PK, autoincrement)、operatorId(BigInt?, @map("operator_id"))、module(String, VarChar(50))、action(String, VarChar(50))、targetType(String?, @map("target_type"), VarChar(50))、targetId(String?, @map("target_id"), VarChar(255))、success(Boolean?, default(true))、errorMessage(String?, @map("error_message"), VarChar(500))、requestMethod(String?, @map("request_method"), VarChar(16))、requestPath(String?, @map("request_path"), VarChar(255))、ipAddress(String?, @map("ip_address"), VarChar(64))、userAgent(String?, @map("user_agent"), VarChar(512))、payload(Json?)、createdAt(DateTime?, default(now), @map("created_at"), Timestamptz(6))、operator(SysUser? @relation("UserOperationLogs"))。@@index([operatorId])、@@index([module, action])、@@index([createdAt])，@@map("sys_operation_log")。文件：schema.prisma#L354-L375

**F-045**: model Account（NextAuth）字段：id(BigInt, PK, autoincrement)、userId(BigInt, @map("user_id"))、type(String)、provider(String)、providerAccountId(String, @map("provider_account_id"))、refresh_token(String?)、access_token(String?)、expires_at(Int?)、token_type(String?)、scope(String?)、id_token(String?)、session_state(String?)、user(SysUser, Cascade)。@@unique([provider, providerAccountId])，@@map("account")。文件：schema.prisma#L377-L394

**F-046**: model Session（NextAuth）字段：id(BigInt, PK, autoincrement)、sessionToken(String, unique, @map("session_token"))、userId(BigInt, @map("user_id"))、expires(DateTime)、user(SysUser, Cascade)。@@map("session")。文件：schema.prisma#L396-L404

**F-047**: model VerificationToken（NextAuth）字段：identifier(String)、token(String, unique)、expires(DateTime)。@@unique([identifier, token])，@@map("verification_token")。文件：schema.prisma#L406-L413

**F-048**: seed.ts 初始化的系统角色：root（根用户）、admin（管理员）、common（普通角色）。文件：seed.ts#L26-L30

**F-049**: seed.ts 初始化的系统字典：audit_status（审核状态）、dev_status（开发状态）、category_code（作品分类）、honor_type（荣誉类型）、banned_users（封禁用户黑名单）、blocked_email_domains（注册屏蔽域名）。isSystem 均为 true。文件：seed.ts#L32-L39

**F-050**: seed.ts 初始化审核状态字典项：0=待审核、1=已通过、2=已拒绝。文件：seed.ts#L41-L45

**F-051**: seed.ts 初始化开发状态字典项：ideation=创意构思、prototype=初步原型、completed=功能完成、released=已可体验。文件：seed.ts#L47-L52

**F-052**: seed.ts 初始化作品分类字典项：utility=实用工具、scenario=场景应用、assistant=智能助手、content=内容创作、creative=创意实验、other=其他类型。文件：seed.ts#L54-L61

**F-053**: seed.ts 初始化荣誉类型字典项：community_choice=社区精选、city_star=城市人气、best_of_year=城市推荐。文件：seed.ts#L63-L67

**F-054**: seed.ts 初始化默认屏蔽邮箱域名：example.com、example.org、example.net。文件：seed.ts#L70-L74

**F-055**: seed.ts 从 `./seed-data-countries` 导入 `countryCityItems`，创建 country（省份）和 city（城市）字典及对应字典项。文件：seed.ts#L3、seed.ts#L182-L226

**F-056**: seed.ts 创建默认管理员账号：username=trae、email=trae@example.com、password=trae1234（bcrypt hash, salt rounds=10），并分配 root 角色。文件：seed.ts#L233-L300

**F-057**: seed.ts 定义辅助函数 `addItem(dictCode, item, stats)`，执行幂等 upsert 操作（先查后创建）。文件：seed.ts#L326-L355

---

## d. 认证系统

**F-058**: NextAuth 配置位于 src/lib/auth-nextauth.ts，导出 `handlers`、`auth`、`signIn`、`signOut`，使用 `PrismaAdapter(prisma)` 和 JWT session 策略。文件：auth-nextauth.ts#L106-L110

**F-059**: NextAuth providers 仅配置 Credentials provider，接受 email 和 password 字段。文件：auth-nextauth.ts#L11-L57

**F-060**: authorize 回调逻辑：通过 email 查找 SysUser，验证 passwordHash 是否存在，使用 bcryptjs compare 校验密码；若用户被封禁（isUserBanned）返回 null 并记录失败认证日志。文件：auth-nextauth.ts#L17-L56

**F-061**: signIn 页面路径配置为 `/sign-in`（不带语言前缀，经 middleware 处理会重定向到 /{lang}/sign-in）。文件：auth-nextauth.ts#L59-L61

**F-062**: jwt callback：当 user 存在时设置 token.id = user.id；在 Node.js runtime 下检查封禁状态，若已封禁则清空 token.id 使存量会话失效。Edge Runtime 下跳过封禁检查（Prisma 无法运行）。文件：auth-nextauth.ts#L63-L79

**F-063**: session callback：将 token.id 赋值给 session.user.id。文件：auth-nextauth.ts#L80-L85

**F-064**: signIn event：写入认证日志（authType=sign_in, authChannel=credentials, authStatus=success），更新 SysUser.lastSignInAt。文件：auth-nextauth.ts#L87-L103

**F-065**: src/lib/auth.ts 导出类型 AuthUser（userId: bigint, email: string, username: string, roles: string[]），导出函数 getAuthUser()、hasAnyRole()、isAdmin()。文件：auth.ts#L4-L68

**F-066**: getAuthUser() 从 NextAuth session 获取 user.id，查询数据库获取用户及角色列表，返回 AuthUser 对象；session 不存在或查询失败返回 null。文件：auth.ts#L15-L53

**F-067**: isAdmin() 判断用户角色是否包含 'admin' 或 'root'。文件：auth.ts#L66-L68

**F-068**: 注册 API 为 POST /api/auth/register，接受 email、password、username，校验必填字段，检查邮箱域名是否被屏蔽，检查邮箱是否已注册，使用 bcrypt hash(password, 10) 创建用户，分配 common 角色，记录注册认证日志。文件：register/route.ts

**F-069**: NextAuth handlers 挂载在 GET/POST /api/auth/[...nextauth]，直接导出 handlers.GET 和 handlers.POST。文件：[[...nextauth]/route.ts](file:///d:/spaces/SpecWeave/external/libs/ai/trae-community/trae-co-creation-demo-wall/src/app/api/auth/[...nextauth]/route.ts)

---

## e. API 路由

**F-070**: GET /api/works — 作品列表查询。支持参数：page、pageSize、search、city、country、category、tags（逗号分隔）、lang（默认zh-CN）、sort（newest/likes/views，默认newest）、date（YYYY-MM-DD）、honor。过滤条件：auditStatus=1 且 displayStatus=1。返回 items、total、page、pageSize、totalPages。支持多语言标签解析（labelI18n）。文件：works/route.ts#L48-L247

**F-071**: PUT /api/works — 更新作品（认证用户）。需登录，验证作品所有权（userId 匹配），使用 zod updateSchema 校验输入，sanitizeRichText 清理 story HTML，事务内更新 WorkBase、WorkTagRelation（删后重建）、WorkDetail（upsert）、WorkImage（删 screenshot 类型后重建）、WorkTeam（upsert）。文件：works/route.ts#L249-L381

**F-072**: GET /api/works/[id] — 作品详情。支持 lang 参数。获取当前用户（可未登录）。权限检查：非作者/非管理员只能查看 auditStatus=1 且 displayStatus=1 的作品。返回完整作品数据（含 user、statistic、tags、honors、detail、images、team），字段做 i18n 标签解析和 HTML sanitize。文件：[works/[id]/route.ts](file:///d:/spaces/SpecWeave/external/libs/ai/trae-community/trae-co-creation-demo-wall/src/app/api/works/[id]/route.ts)

**F-073**: POST /api/works/[id]/like — 切换点赞状态。需登录，已赞则取消（删除 WorkLike 并 decrement likeCount），未赞则点赞（事务创建 WorkLike + upsert WorkStatistic increment likeCount），记录操作日志。返回 { liked: boolean }。文件：[works/[id]/like/route.ts](file:///d:/spaces/SpecWeave/external/libs/ai/trae-community/trae-co-creation-demo-wall/src/app/api/works/[id]/like/route.ts)

**F-074**: POST /api/works/[id]/view — 记录浏览量。无需登录，upsert WorkStatistic 使 viewCount+1，记录操作日志（未登录用户 operatorId 为空）。文件：[works/[id]/view/route.ts](file:///d:/spaces/SpecWeave/external/libs/ai/trae-community/trae-co-creation-demo-wall/src/app/api/works/[id]/view/route.ts)

**F-075**: GET /api/works/[id]/stats — 获取作品统计（viewCount、likeCount）及当前用户是否已点赞。文件：[works/[id]/stats/route.ts](file:///d:/spaces/SpecWeave/external/libs/ai/trae-community/trae-co-creation-demo-wall/src/app/api/works/[id]/stats/route.ts)

**F-076**: GET /api/works/likes — 获取当前用户点赞的作品列表（分页），需登录。文件：works/likes/route.ts

**F-077**: GET /api/works/filter-options — 获取筛选项（countries、cities、categories、honors），仅返回有已审核作品的项，支持 lang 参数做多语言解析，通过 sortFilterOptions 排序。文件：works/filter-options/route.ts

**F-078**: sortFilterOptions 函数：先按 sortOrder 升序排序，sortOrder 相同时按 label.localeCompare(label, lang) 排序。文件：sort-filter-options.ts#L8-L14

**F-079**: POST /api/submit — 提交新作品。需登录，zod 校验，sanitizeRichText 清理 story，事务内创建 WorkBase、WorkTagRelation、WorkDetail、WorkImage（screenshot 类型）、WorkTeam、WorkStatistic。自动审核逻辑：检查标签中 isAutoAudit=true 且当前时间在 auditStartTime~auditEndTime 范围内，命中则 auditStatus=1、displayStatus=1 并写入 WorkAuditLog，否则 auditStatus=0、displayStatus=0。记录操作日志。文件：submit/route.ts

**F-080**: GET /api/tags — 标签列表（分页），支持 query 搜索、filter（all/auto/manual）。POST /api/tags — 创建标签（name, isAutoAudit, auditStartTime, auditEndTime）。PUT /api/tags — 更新标签。DELETE /api/tags?id=xx — 删除标签。POST/PUT/DELETE 调用 getAuthUser() 但未强制管理员校验（日志记录 operatorId）。文件：tags/route.ts

**F-081**: GET /api/tags/all — 获取所有标签（不分页），按 id 升序。文件：tags/all/route.ts

**F-082**: GET /api/users — 用户列表（管理员），支持 page、pageSize、query、roleCode 筛选，附带封禁状态（banned 字段）。POST /api/users — 创建用户（管理员），不设置 passwordHash。PUT /api/users — 更新用户（管理员），支持 roleIds 更新（禁止分配 root 角色），先删后建角色关联。DELETE /api/users?id=xx — 删除用户（管理员）。文件：users/route.ts

**F-083**: POST /api/users/[id]/ban — 封禁/解封用户（管理员），Body: { banned: boolean }。禁止封禁 admin/root 角色用户。调用 banUser() 或 unbanUser()。文件：[users/[id]/ban/route.ts](file:///d:/spaces/SpecWeave/external/libs/ai/trae-community/trae-co-creation-demo-wall/src/app/api/users/[id]/ban/route.ts)

**F-084**: GET /api/roles — 角色列表（管理员），支持分页和搜索。POST/PUT/DELETE 均返回 403（角色固定为 root/admin/common，不允许增删改）。文件：roles/route.ts

**F-085**: GET /api/dictionaries — 字典列表（分页），支持 code 参数获取单个字典（含 items），支持 lang 参数做多语言标签替换，支持 query 搜索、filter（all/system/custom）。POST /api/dictionaries — 创建字典或字典项（type: 'dict' | 'item'）。PUT /api/dictionaries — 更新字典或字典项。DELETE /api/dictionaries?type=dict|item&id=xx — 删除字典或字典项。文件：dictionaries/route.ts

**F-086**: POST /api/file — 文件上传到腾讯 COS（需登录），支持 FormData（field name="file"），限制 5MB，允许类型 image/jpeg、image/png、image/webp、image/gif。文件路径为 `uploads/{date}/{uuid}.{ext}`，返回 { success, url, path }。DELETE /api/file — 删除 COS 文件（需登录），接受 { path, url } 参数。文件：file/route.ts

**F-087**: POST /api/avatar — 头像上传（需登录），限制 2MB，允许类型 image/jpeg、image/png、image/webp、image/svg+xml。文件路径为 `avatars/{userId}-{timestamp}.{ext}`，上传成功后更新 SysUser.avatarUrl。文件：avatar/route.ts

**F-088**: GET /api/profile — 获取当前登录用户资料（需登录），返回 profile（含 roles、workCount、totalViews、totalLikes）和 works 列表。PUT /api/profile — 更新当前用户资料（username、bio、phone），username 长度 2-20。文件：profile/route.ts

**F-089**: GET /api/profile/[id] — 公开用户主页（无需登录），返回已审核可见作品及统计数据。文件：[profile/[id]/route.ts](file:///d:/spaces/SpecWeave/external/libs/ai/trae-community/trae-co-creation-demo-wall/src/app/api/profile/[id]/route.ts)

**F-090**: POST /api/profile/change-password — 修改密码（需登录），接受 oldPassword、newPassword、confirmPassword，验证旧密码（bcrypt compare），新密码不少于6字符，两次新密码一致，hash(newPassword, 10) 更新 passwordHash。文件：profile/change-password/route.ts

**F-091**: GET /api/rankings — 排行榜数据（公开）。返回 cityRanking（Top20 城市，按作品数/浏览量/点赞数排序）、worksRanking（byViews、byLikes 各 Top20）、creatorsRanking（byWorks、byViews、byLikes 各 Top20）、trendingWorks（7天内按浏览量 Top20）。文件：rankings/route.ts

**F-092**: GET /api/logs/auth — 认证日志列表（管理员），支持分页、query 搜索（IP/用户名/邮箱）、filter（authType）、startDate/endDate 日期范围。文件：logs/auth/route.ts

**F-093**: GET /api/logs/operations — 操作日志列表（管理员），支持分页、query 搜索、filter（success/failed）、module 筛选、startDate/endDate 日期范围，返回 modules 列表（distinct module）。文件：logs/operations/route.ts

**F-094**: GET /api/console/overview — 管理后台概览统计（管理员），支持 window 参数（7/30天）。返回 stats（totalWorks、activeUsers、registeredUsers、systemVisits 的值和环比变化率）、trend（每日 visits/registrations/uploads 时序数据）、distribution（登录/注册/上传/其他操作分布）、latestActivities（最近10条注册和上传活动）。使用原生 SQL 查询日聚合和去重活跃用户。文件：console/overview/route.ts

**F-095**: GET /api/console/works — 管理后台作品列表（需登录，管理员可看全部，普通用户只能看自己的），支持 id 参数获取单个作品详情，支持 page、pageSize、query、userId、category、country、honor、auditStatus 筛选。POST /api/console/works — 管理员创建作品（基础字段+初始 statistic 记录）。PUT /api/console/works — 更新作品（支持批量审核 ids[]、单个审核 auditStatus+auditReason、标签 tagIds、荣誉 honorIds、团队信息 teamMembers/teamIntro/contactPhone/contactEmail、基础字段）。批量审核仅管理员可用。DELETE /api/console/works?id=xx — 删除作品（作者本人或管理员）。文件：console/works/route.ts

**F-096**: GET /api/console/works/[id]/likes — 查询某作品点赞用户列表（管理员），分页返回，用于排查刷量。文件：[console/works/[id]/likes/route.ts](file:///d:/spaces/SpecWeave/external/libs/ai/trae-community/trae-co-creation-demo-wall/src/app/api/console/works/[id]/likes/route.ts)

**F-097**: GET /api/console/cities/stats — 城市统计（管理员），返回所有城市的 totalWorks、approvedCount、pendingCount、totalViews、totalLikes，按通过数/浏览量/点赞数排序。文件：console/cities/stats/route.ts

---

## f. 工具模块（lib/）

**F-098**: src/lib/prisma.ts 导出 prisma 单例实例，使用 globalThis 缓存避免开发环境热重载创建多个连接。开发环境日志级别为 ['query', 'error', 'warn']，生产环境为 ['error']。文件：prisma.ts

**F-099**: src/lib/cos.ts 导出 cos（COS 实例，使用 COS_SECRET_ID 和 COS_SECRET_KEY 环境变量）、COS_BUCKET、COS_REGION。文件：cos.ts

**F-100**: src/lib/crud.ts 导出 CRUD_QUERY_PARAMS 常量（page、pageSize、query、filter）、DICT_FILTERS（all/system/custom）、TAG_FILTERS（all/auto/manual）、normalizeFilter 函数。文件：crud.ts

**F-101**: src/lib/utils.ts 导出 cn() 函数，组合 clsx 和 tailwind-merge。文件：utils.ts

**F-102**: src/lib/audit-log.ts 导出 writeAuthLog() 和 writeOperationLog()。内部函数：normalizeId（将 bigint/number/string/null/undefined 统一转为 BigInt 或 null）、getHeaderValue（安全获取 header 值）、getClientIp（从 x-forwarded-for、x-real-ip、cf-connecting-ip、x-client-ip 获取客户端 IP）、toSafeJson（BigInt 安全序列化）、getRequestMeta（从 Request 对象提取 IP、UA、Method、Path）。writeAuthLog 写入 sys_auth_log 表，writeOperationLog 写入 sys_operation_log 表，均为 try-catch 不抛异常。文件：audit-log.ts

**F-103**: src/lib/ban.ts 导出 clearBanCache()、getBannedUserIds()、isUserBanned()、banUser()、unbanUser()、isEmailDomainBlocked()。常量：BANNED_USERS_DICT='banned_users'、BLOCKED_DOMAINS_DICT='blocked_email_domains'、DEFAULT_BLOCKED_DOMAINS=['example.com','example.org','example.net']、CACHE_TTL_MS=60000（60秒内存缓存）。banUser 自动 ensureDict（首次封禁自动创建字典），使用 upsert 写入 sys_dict_item，状态设为 status=true；unbanUser 删除对应 dictItem。isEmailDomainBlocked 合并默认域名和数据库中配置的域名（转小写）。文件：ban.ts

**F-104**: src/lib/rich-text.ts 导出 RICH_TEXT_SANITIZE_OPTIONS（允许标签 p/br/strong/em/u/s/h2/h3/ul/ol/li/a/blockquote/code；a 标签允许 href/target/rel 属性；允许 http/https/mailto 协议）、stripHtmlTags()（正则去除 HTML 标签）、sanitizeRichText()（使用 sanitize-html 清理）。文件：rich-text.ts

**F-105**: src/lib/work-form.ts 导出接口 WorkFormValues 和函数 buildWorkFormSchema(t, options)。buildWorkFormSchema 返回 zod 校验 schema，校验规则：name 2-50字符、intro 10-100字符、country/city/category/devStatus 必填、tags 1-5个、coverUrl 必填、story 纯文本 20-2000字符（HTML经strip）、highlights 1-5个每个1-30字符、scenarios 至少1个每个1-100字符、screenshots 1-5个、demoUrl/repoUrl 为合法URL或空字符串、team 至少1人每人1-20字符、teamIntro 默认必填1-500字符（requireTeamIntro 选项控制）、contactPhone 最多20字符、contactEmail 为合法邮箱或空字符串。文件：work-form.ts

**F-106**: src/lib/types.ts 导出接口 Work（作品前端数据结构，含 id/name/intro/city/country/category/team/teamIntro/contactEmail/coverUrl/story/features/scenarios/screenshots/techStack/demoUrl/repoUrl/isFeatured/isTrending/isCitySelection/isCommunityRecommended/createdAt/views/likes/tags/honors/author）、SubmissionFormData（提交表单数据结构，team/tags/screenshots 为字符串）、Tag（id/name）、DictionaryItem（id/dictCode/itemLabel/itemValue/parentValue/sortOrder/lang）。文件：types.ts

**F-107**: src/lib/works-store.ts（zustand store）导出 useWorksStore，状态包含 listCache（Map<string, ListCacheEntry>，key 为序列化查询参数字符串）、detailCache（Map<string, Work>）；方法：setListCache、setDetailCache、getDetailCache。ListCacheEntry 类型含 items、total、totalPages。文件：works-store.ts

**F-108**: src/lib/use-feedback.ts（'use client'）导出 useFeedback(timeout=2500) Hook，返回 { feedback, showFeedback }。showFeedback(type, message) 设置反馈状态并在 timeout 毫秒后自动清除。文件：use-feedback.ts

**F-109**: src/lib/use-works.ts 导出 useWorks(params) Hook，使用 @tanstack/react-query 的 useQuery，queryKey 为 ['works', params]，请求 GET /api/works?{params}，staleTime 为 2 分钟。参数接口 WorksParams 含 page/pageSize/search/sort/lang/city/country/category/tags/date/honor。文件：use-works.ts

**F-110**: src/lib/language/routing.ts 导出 routing 配置，locales 为 ['zh-CN', 'en-US', 'ja-JP']，defaultLocale 为 'zh-CN'。文件：language/routing.ts

**F-111**: src/lib/language/request.ts 使用 getRequestConfig 导出 next-intl 配置，动态 import `../../assets/translations/${locale}.json` 加载翻译文件。文件：language/request.ts

**F-112**: src/lib/language/navigation.ts 导出 createNavigation(routing) 生成的 Link、redirect、usePathname、useRouter、getPathname。文件：language/navigation.ts

---

## g. 中间件

**F-113**: src/middleware.ts 使用 next-auth 的 auth() wrapper 包裹中间件逻辑。文件：middleware.ts

**F-114**: isProtectedRoute 正则：`/^\/(zh-CN|en-US)\/(submit|console|profile)/`，匹配 /{lang}/submit、/{lang}/console、/{lang}/profile 路径。文件：middleware.ts#L9-L11

**F-115**: 中间件逻辑：/api/auth 路径直接放行；isProtectedRoute 且非 prefetch 请求时，未登录则重定向到 /{lang}/sign-in?callbackUrl={pathname}；/api 路径跳过 i18n 中间件直接放行；其余路径交给 next-intl middleware 处理语言路由。文件：middleware.ts#L16-L39

**F-116**: matcher 配置：跳过 _next 目录和静态文件（html/css/js/jpg/jpeg/webp/png/gif/svg/ttf/woff2/ico/csv/docx/xlsx/zip/webmanifest），始终匹配 /api 和 /trpc 路径。文件：middleware.ts#L41-L48

---

## h. 前端架构

**F-117**: 根 layout.tsx（src/app/layout.tsx）仅返回 children，html/body 标签在 [language]/layout.tsx 中渲染以支持 per-locale lang 属性。文件：app/layout.tsx

**F-118**: [language]/layout.tsx 加载字体 Inter（--font-sans）、Noto_Sans_SC（--font-chinese）、JetBrains_Mono（--font-mono）；Provider 嵌套顺序：SessionProvider → QueryProvider → NextIntlClientProvider → SiteLayout；包含 Toaster（sonner，position=top-center, theme=dark, richColors）。metadata title 为 'TRAE DEMO WALL'，icon 为 /trae.ico。文件：[[language]/layout.tsx](file:///d:/spaces/SpecWeave/external/libs/ai/trae-community/trae-co-creation-demo-wall/src/app/[language]/layout.tsx)

**F-119**: 状态管理：zustand（useWorksStore，客户端缓存作品列表和详情）；@tanstack/react-query（useWorks Hook，服务端数据获取，staleTime=2分钟）；react-hook-form + zod 表单校验；NextAuth SessionProvider 管理认证状态。

**F-120**: UI 框架：Tailwind CSS（darkMode: class）、shadcn/ui 组件（components.json 配置 style=default, rsc=true, tsx=true, baseColor=zinc）、Radix UI 基础组件、lucide-react 图标。文件：tailwind.config.js、components.json

**F-121**: 自定义 Tailwind 颜色：品牌绿色板 green-300=#9DF7C6、green-400=#32F08C、green-500=#1FDB79、green-600=#14B368；CSS 变量驱动的主题色（border/input/ring/background/foreground/primary/secondary/destructive/muted/accent/popover/card/sidebar/chart）。文件：tailwind.config.js#L13-L69

**F-122**: 组件目录结构：auth/（登录注册表单）、common/（通用组件如 QueryProvider、HeroBanner、LoadingOverlay、ActionButton、FormSelect）、crud/（CRUD 通用组件：CrudFeedback、CrudFilterBar、CrudPagination）、layout/（SiteLayout、ParticlesBackground）、ui/（基础 UI 组件：Badge、Button、Card、Checkbox、DatePicker、Dialog、DottedGlowBackground、Input、Label、Select、Textarea）、work/（作品相关：WorkCard、CityFilter、EditForm、LikedWorks、WorksManagement）。

**F-123**: @tsparticles/react + @tsparticles/slim 用于粒子背景效果（ParticlesBackground 组件）。文件：particles-background.tsx

**F-124**: tsconfig.json 配置：target=ES2017、strict=false、strictNullChecks=true、moduleResolution=bundler、jsx=preserve、paths 别名 @/* → ./src/*。文件：tsconfig.json

**F-125**: next.config.ts 配置：output='standalone'、images.unoptimized=true、outputFileTracingExcludes 排除 @next/swc-* 和 @swc/core-* 以减小 Docker 镜像体积。使用 next-intl plugin（request.ts 路径）。文件：next.config.ts

---

## i. 国际化

**F-126**: 支持语言：zh-CN、en-US、ja-JP，默认语言 zh-CN。文件：language/routing.ts#L3-L6

**F-127**: 翻译文件位于 src/assets/translations/，包含 zh-CN.json、en-US.json、ja-JP 三个 JSON 文件。文件：目录结构 translations/

**F-128**: URL 结构为 /{locale}/...，使用 next-intl 的 [language] 动态路由段，由 createMiddleware(routing) 处理语言检测和重定向。文件：middleware.ts#L7

**F-129**: 字典数据支持 labelI18n 字段（JSON 类型），存储多语言标签如 {"zh-CN": "中国", "en-US": "China"}，API 返回时根据 lang 参数选择对应语言标签，fallback 到 itemLabel。文件：works/route.ts#L144-L156

---

## j. COS 存储

**F-130**: COS SDK 初始化使用环境变量 COS_SECRET_ID、COS_SECRET_KEY。导出常量 COS_BUCKET、COS_REGION。文件：cos.ts

**F-131**: 文件上传 API（/api/file）PUT 到 COS，Key 为 `uploads/{YYYY-MM-DD}/{uuid}.{ext}`，返回公开 URL 格式 `https://{BUCKET}.cos.{REGION}.myqcloud.com/{Key}`。限制 5MB、图片类型（jpg/png/webp/gif）。文件：file/route.ts#L44-L73

**F-132**: 文件删除 API（/api/file）调用 cos.deleteObject，可从 path 或 url 参数解析 Key。文件：file/route.ts#L84-L146

**F-133**: 头像上传 API（/api/avatar）Key 为 `avatars/{userId}-{timestamp}.{ext}`，限制 2MB、图片类型（jpg/png/webp/svg），上传后自动更新用户 avatarUrl。文件：avatar/route.ts

---

## k. Docker 部署

**F-134**: Dockerfile 使用三阶段构建：base（node:20-slim，安装 openssl/ca-certificates，配置清华 Debian 镜像源）、builder（安装 python3/make/g++，npm ci，prisma generate，npm run build）、runner（复制 standalone 输出、.next/static、prisma、必要 node_modules，EXPOSE 3000，CMD ["sh", "entrypoint.sh"]）。文件：Dockerfile

**F-135**: Dockerfile 基础镜像使用自定义镜像源 `docker.cnb.cool/jaguarliu.cool/wenyuan-ai/docker-sync/node:20-slim_amd64`。文件：Dockerfile#L2

**F-136**: Dockerfile 构建参数：COS_SECRET_ID、COS_SECRET_KEY、COS_BUCKET、COS_REGION、NEXTAUTH_SECRET，构建时设为环境变量；DATABASE_URL 使用占位符（构建时不需要真实数据库连接）。文件：Dockerfile#L31-L44

**F-137**: entrypoint.sh 逻辑：若 RUN_DB_INIT=true，等待 db:5432 端口可用，执行 `prisma db push --accept-data-loss`，执行 `tsx prisma/seed.ts`（失败不中断）；若 START_SERVER≠true 则退出（初始化容器用）；否则执行 `node server.js` 启动应用。文件：entrypoint.sh

**F-138**: docker-compose.yml 定义 5 个服务：app（主应用，端口3000，依赖 app-init 完成）、app-init（初始化服务，RUN_DB_INIT=true、START_SERVER=false，restart:no，依赖 db 和 redis）、db（postgres:16-alpine，端口5432，数据库 trae_demo_wall，配置 max_connections=100、shared_buffers=256MB 等参数）、db-dev（postgres:16-alpine，端口5433，数据库 trae_demo_wall_dev）、redis（redis:7-alpine，端口6379，maxmemory 256mb allkeys-lru）、nginx（nginx:alpine，端口80，挂载 nginx.conf，反向代理到 app）。文件：docker-compose.yml

**F-139**: docker-compose 数据库连接串：DATABASE_URL=postgresql://postgres:postgres@db:5432/trae_demo_wall?schema=public&connection_limit=20&pool_timeout=20&connect_timeout=10，DIRECT_URL=postgresql://postgres:postgres@db:5432/trae_demo_wall。文件：docker-compose.yml#L16-L17

**F-140**: 存在额外 compose 文件：docker-compose.2c8g.yml（2核8G配置）、docker-compose.prod.yml（生产配置）。根目录还包含 nginx.conf、nginx-lb.conf、nginx-lb-2.conf 三个 Nginx 配置文件。

**F-141**: volumes：postgres-data、postgres-dev-data、redis-data；network：trae-network（bridge 驱动）。文件：docker-compose.yml#L142-L149

---

## l. intl 版本差异

**F-142**: intl 版本项目名称为 `dem`（中文版为 `trae-co-creation-demo-wall`）。文件：intl/package.json#L2

**F-143**: intl 版本新增依赖 `@vercel/edge-config@^1.4.3`，中文版无此依赖。文件：intl/package.json#L43

**F-144**: intl 版本缺少 qrcode、qrcode-generator 依赖（中文版有）。文件对比：中文版 package.json#L53-L54 vs intl package.json。

**F-145**: intl 版本支持语言为 ['en-US', 'zh-CN', 'ja-JP', 'id-ID', 'vi-VN']，默认语言 'en-US'；中文版为 ['zh-CN', 'en-US', 'ja-JP']，默认 'zh-CN'。文件：intl/routing.ts#L3-L6

**F-146**: intl 版本翻译文件包含 5 个：en-US.json、zh-CN.json、ja-JP.json、id-ID.json、vi-VN.json；中文版为 3 个（zh-CN/en-US/ja-JP）。

**F-147**: intl 版本缺少 src/lib/ban.ts 文件，不包含用户封禁和邮箱域名屏蔽功能。文件对比：中文版有 ban.ts，intl 版无。

**F-148**: intl 版本 auth-nextauth.ts 的 authorize 回调不检查 isUserBanned，jwt callback 也不做封禁检查和 token.id 清空（中文版有封禁检查逻辑）。文件：intl/auth-nextauth.ts#L16-L44 vs 中文版 auth-nextauth.ts#L39-L78。

**F-149**: intl 版本注册 API 不检查 isEmailDomainBlocked（因无 ban.ts）。

**F-150**: intl 版本新增 src/lib/edge-config.ts，导出 getDictionaries() 函数，使用 @vercel/edge-config 的 get('dictionaries') 获取缓存的字典数据。文件：intl/edge-config.ts

**F-151**: intl 版本新增 POST /api/sync-edge-config 路由，将 country/city/category/honor 字典数据 PATCH 到 Vercel Edge Config（需要 EDGE_CONFIG_ID 和 VERCEL_API_TOKEN 环境变量）。文件：intl/sync-edge-config/route.ts

**F-152**: intl 版本新增 GET /api/console/works/export 路由，导出作品为 CSV 文件（管理员），支持 ids 参数（选中导出）或筛选条件导出，硬上限 5000 条，带 UTF-8 BOM，文件名格式 works_export_YYYYMMDD_HHMMSS.csv。文件：intl/console/works/export/route.ts

**F-153**: intl 版本 API 路由中无 /api/users/[id]/ban 路由（中文版有）。文件对比：intl src/app/api/users/ 下无 [id]/ban/ 子目录。

**F-154**: intl 版本 prisma schema 中 SysAuthLog 和 SysOperationLog 的 user/operator 关系 onDelete 为 SetNull（中文版为 Cascade）。文件：intl/schema.prisma#L380、intl/schema.prisma#L405。

**F-155**: intl 版本 schema.prisma 中 DateTime 字段精度为 @db.Timestamptz（无精度参数 6）；中文版为 @db.Timestamptz(6)。文件对比：两版 schema.prisma。

**F-156**: intl 版本 Dockerfile 构建阶段使用 `npm install`（中文版使用 `npm ci`）。文件：intl/Dockerfile#L51 vs 中文版 Dockerfile#L51。

**F-157**: intl 版本 docker-compose.yml 不含 nginx 服务（中文版有 nginx 服务和端口 80 映射）。文件：intl/docker-compose.yml vs 中文版 docker-compose.yml。

**F-158**: intl 版本 entrypoint.sh 中 prisma db push 不带 --accept-data-loss 参数（中文版带 --accept-data-loss）。文件：intl/entrypoint.sh#L13 vs 中文版 entrypoint.sh#L16。

**F-159**: intl 版本 next.config.ts 的 outputFileTracingExcludes 注释说明是为了避免 Vercel Lambda 100MB 限制（中文版注释是减小 Docker 镜像体积）。文件：intl/next.config.ts#L9-L11。

**F-160**: intl 版本 middleware.ts 的 isProtectedRoute 正则仍为 `/^\/(zh-CN|en-US)\/(submit|console|profile)/`，未包含 id-ID 和 vi-VN 语言前缀（与中文版相同）。文件：intl/middleware.ts#L9-L11。

**F-161**: intl 版本 src/assets/ 下无 brand/ 目录（中文版有 brand/ 目录含 logo.png、logo.svg）。文件对比：目录结构。

**F-162**: intl 版本有 test/ 目录（含 filter-options-sort.test.ts）；中文版无 test/ 目录在 src/ 外，但有 test/ 脚本（package.json 中有 test:* 脚本）。文件对比：intl 有 test/filter-options-sort.test.ts。

**F-163**: intl 版本有 .github/workflows/sync-cnb.yml（CI 工作流）；中文版有 .github/ISSUE_TEMPLATE/（bug_report、feature_request、other_feedback、config.yml）。
