# Demo Wall 核心洞察与知识地图

I阶段产出：核心洞察四元组 + 知识地图设计

---

## 核心洞察（四元组）

### 洞察一：垂直分表的作品数据模型

**陈述**：作品（Work）数据采用垂直分表（Vertical Partitioning）设计，将一个逻辑上的"作品"拆分为五个物理表：WorkBase（核心标识与外键）、WorkDetail（富文本内容与链接）、WorkImage（截图集合，一对多）、WorkTeam（团队信息，一对一）、WorkStatistic（审核状态与计数，一对一）。各表通过 workId（BigInt）关联，所有子表对 WorkBase 设置 Cascade 级联删除。

**证据**：F-033（WorkBase 定义及索引）、F-034（WorkDetail 以 workId 为 PK 的一对一）、F-035（WorkImage 一对多含 sortOrder）、F-036（WorkTeam 一对一含 JSON members）、F-037（WorkStatistic 双状态+计数器）、F-071（PUT /api/works 事务内多表更新）、F-079（POST /api/submit 事务内五表同建）

**反常识**：直觉上"一个作品就是一张表"，把所有字段（标题、描述、截图、团队、统计）塞进一个 Work 表更简单。但项目选择五表分离，原因有三：
1. **字段访问频率差异极大**——列表页只需要 WorkBase 的标题/封面/分类，加载 WorkDetail 的大文本 story 或 WorkImage 的多条截图会浪费带宽；
2. **写入模式不同**——WorkStatistic 的 viewCount/likeCount 是高频写操作（每次浏览/点赞都更新），与低频写的作品内容分离避免锁竞争；
3. **一对多关系天然独立**——截图（WorkImage）是多条记录，无法用单表字段承载；团队成员（members）用 JSON 存储在 WorkTeam 中，避免了复杂的成员子表。
这不是"过度设计"，而是对读写频率和数据关系的精准切分。

**行动**：
- **先看** schema.prisma 中 WorkBase→WorkStatistic 的五个 model，理解外键关系和级联策略；
- **再看** submit/route.ts 的事务创建逻辑，理解五表如何在一次事务中原子性创建；
- **扩展点**：若需新增作品属性（如视频链接、附件），判断归属表：高频列表字段→WorkBase，大文本/低频字段→WorkDetail，集合型→新建子表，计数型→WorkStatistic；
- **常见误区**：不要在 WorkBase 上加入大文本字段（如 story），会拖慢列表查询；不要在 WorkStatistic 上加入业务字段，它是纯状态+计数器表。

---

### 洞察二：RBAC + 字典驱动的可配置分类系统

**陈述**：系统采用"RBAC 三角色 + SysDict/SysDictItem 动态字典"双层权限与分类架构。角色固定为 root/admin/common 三级（不可通过 API 增删改），而分类数据（审核状态、开发状态、作品分类、荣誉类型、国家城市、封禁名单、屏蔽域名）全部存储在 SysDict/SysDictItem 两张表中，通过 dictCode 分组，支持 labelI18n 多语言标签、parentValue 层级关系、sortOrder 排序。字典项可通过管理后台 API 动态增删改，无需改代码或重启。

**证据**：F-028~F-029（SysDict/SysDictItem 模型含 labelI18n/parentValue/sortOrder）、F-031~F-032（SysRole/SysUserRole 三角色）、F-048~F-055（seed 初始化 6 个系统字典+国家城市）、F-049（banned_users 和 blocked_email_domains 也是字典）、F-084（角色 API 只允许 GET，POST/PUT/DELETE 返回 403）、F-085（字典 CRUD API 支持 dict/item 双类型）、F-129（API 返回时根据 lang 参数解析 labelI18n）

**反常识**：常见做法是用 TypeScript enum 或数据库 CHECK 约束定义分类（如 `category ENUM('utility','scenario','assistant')`），简单直接。但项目选择字典表驱动，代价是每次查询分类选项都要 JOIN 字典表，增加了查询复杂度。其价值在于：
1. **运营可配**：新增分类（如新增"AI Agent"类别）不需要改代码发版，管理员后台即可操作；
2. **多语言原生支持**：labelI18n 字段存储 JSON 多语言标签，API 按 lang 参数动态返回，比在代码里维护 i18n key 更灵活；
3. **同一机制复用为黑名单**：封禁用户列表（banned_users）和屏蔽邮箱域名（blocked_email_domains）也复用字典表，省掉了额外的黑名单表设计。
但角色（Role）选择了硬编码三级（root/admin/common）而非字典，因为角色与代码权限检查强耦合（isAdmin() 直接判断字符串），动态化会导致安全漏洞。

**行动**：
- **先看** prisma/seed.ts 中 6 个系统字典的初始化，理解 dictCode 和 itemValue 的设计；
- **再看** dictionaries/route.ts 的 CRUD 逻辑和 lib/ban.ts 如何复用字典实现封禁/域名屏蔽；
- **扩展点**：新增业务分类时，先决定是否需要运营动态配置——是则走字典表，否则用 enum/常量；注意 labelI18n 需要同步维护多语言翻译；
- **常见误区**：不要把需要代码逻辑判断的"类型"做成字典（如角色），字典适合"展示型/筛选型"分类；不要忘记字典项的 sortOrder 和 status 字段控制。

---

### 洞察三：Next.js App Router + next-intl 的国际化路由架构

**陈述**：国际化采用 next-intl 的 `[language]` 动态路由段方案，URL 结构为 `/{locale}/...`，所有页面路由嵌套在 `src/app/[language]/` 下。中间件链分三层：(1) NextAuth auth wrapper 处理会话；(2) 受保护路由正则检查 `/^(zh-CN|en-US)\/(submit|console|profile)/`，未登录重定向到登录页；(3) 其余路径交给 next-intl createMiddleware 处理语言检测与重定向。API 路由（`/api/*`）跳过 i18n 中间件直接处理。根 layout.tsx 不渲染 html/body，由 `[language]/layout.tsx` 渲染以设置 per-locale `lang` 属性。

**证据**：F-016~F-017（[language] 动态段下所有页面路由）、F-110~F-112（routing 配置 locales/defaultLocale、request.ts 动态 import 翻译、navigation.ts 生成 Link/redirect）、F-113~F-116（middleware 三层逻辑：auth wrapper → 受保护路由检查 → next-intl i18n 中间件；matcher 跳过静态资源）、F-117~F-118（双层 layout 设计、Provider 嵌套、字体加载）、F-126~F-129（3 种语言、翻译文件位置、labelI18n 动态解析）

**反常识**：直觉上国际化可以用 subdomain（en.example.com）或 query 参数（?lang=en），或在前端用 Context 切换语言不改 URL。但项目选择 URL 前缀（/zh-CN/...、/en-US/...），代价是：
1. **所有页面路由都要嵌套在 [language] 下**，文件结构更深；
2. **需要双层 layout**（根 layout 空壳，[language]/layout 才渲染 html/body），增加了理解成本；
3. **API 路由必须在中间件中特殊放行**，否则会被 i18n 中间件拦截。
但这个选择的收益是：URL 本身携带语言信息，SEO 友好、分享链接自带语言、next-intl 官方推荐方案、与 Next.js App Router 深度集成。更反直觉的是根 layout 不渲染 html/body——这是为了让 [language]/layout 能设置 `<html lang={locale}>`，这是 per-locale SEO 和 accessibility 的必要做法。

**行动**：
- **先看** middleware.ts 理解三层中间件的执行顺序和 matcher 配置；
- **再看** lib/language/ 下的 routing.ts/request.ts/navigation.ts 三件套，以及 [[language]/layout.tsx](file:///d:/spaces/SpecWeave/external/libs/ai/trae-community/trae-co-creation-demo-wall/src/app/%5Blanguage%5D/layout.tsx) 的 Provider 嵌套；
- **扩展点**：新增语言需要：在 routing.ts 添加 locale、创建翻译 JSON 文件、注意 isProtectedRoute 正则要同步更新（intl 版暴露了遗漏问题 F-160）；
- **常见误区**：不要在根 layout.tsx 里渲染 html/body 标签；不要在 API 路由上走 i18n 中间件；不要忘记翻译文件缺失时的 fallback 处理。

---

### 洞察四：服务端/客户端三层数据访问分离

**陈述**：数据访问层明确分为三层，各司其职不越界：(1) **服务端数据层**——Prisma Client 在 Server Component 和 Route Handler 中直接查询数据库，处理事务、权限、多表 JOIN、i18n 标签解析，返回净化后的 DTO；(2) **客户端缓存层（zustand）**——useWorksStore 用 Map 缓存作品列表和详情，key 为序列化查询参数，提供 setListCache/setDetailCache/getDetailCache 命令式缓存操作；(3) **服务端状态同步层（react-query）**——useWorks Hook 封装 useQuery，queryKey 为 `['works', params]`，staleTime=2 分钟，自动处理 loading/error/缓存失效/后台刷新。表单状态由 react-hook-form + zod 独立管理。

**证据**：F-098（Prisma 单例 globalThis 缓存）、F-107（zustand works-store 双 Map 缓存设计）、F-109（useWorks react-query Hook，staleTime=2min）、F-105（work-form.ts zod schema 构建）、F-070~F-079（API 路由中 Prisma 事务、zod 校验、sanitize 处理）、F-119（状态管理总结）、F-118（Provider 嵌套：SessionProvider→QueryProvider→NextIntlClientProvider）

**反常识**：很多 Next.js 项目要么全用 Server Component 直接查数据库（无客户端缓存），要么全用客户端 fetch + SWR/react-query（服务端只做 API proxy）。本项目选择三层分离，看似复杂，实则解决了不同场景的需求：
1. **为什么需要 zustand？** react-query 是声明式缓存（随组件挂载/卸载自动管理），但作品详情在列表页点击后需要"跳转前缓存"避免闪烁，zustand 的命令式 setDetailCache 可以在列表点击时预填缓存，实现"秒开"详情页；
2. **为什么不直接用 Prisma 在客户端？** Prisma 是服务端 ORM，不能在客户端运行，必须通过 API 路由暴露；但 Server Component 可以直接 import prisma 查询，减少 API 层开销；
3. **staleTime 为什么是 2 分钟？** 这是数据新鲜度与性能的权衡——2 分钟内用户切换筛选条件不会重复请求，后台刷新保证最终一致性。

**行动**：
- **先看** lib/prisma.ts 单例模式和 lib/works-store.ts zustand 缓存设计；
- **再看** lib/use-works.ts react-query Hook 和 app/api/works/route.ts 服务端查询逻辑；
- **扩展点**：新增数据实体时，按三层添加：Prisma model → API Route（zod 校验+事务+sanitize）→ react-query Hook（或 zustand store 用于跨页面命令式缓存）；
- **常见误区**：不要在客户端组件直接 import prisma；不要用 zustand 存储服务端持久化数据（它是缓存不是数据源）；不要忘记 Provider 嵌套顺序（QueryClientProvider 必须包裹使用 react-query 的组件）。

---

### 洞察五：富文本 + COS 直传的内容提交管线

**陈述**：作品提交是一条多步骤管线（4 步表单：基本信息→视觉素材→内容介绍→团队信息），核心管线为：Tiptap 富文本编辑器 → sanitize-html 白名单净化 → COS 签名直传图片 → 事务写入五张表。富文本净化采用严格白名单（仅允许 p/br/strong/em/u/s/h2/h3/ul/ol/li/a/blockquote/code，a 标签仅允许 http/https/mailto 协议），COS 上传通过服务端 API 代理（PUT 到 COS，路径按日期+UUID 组织），图片上传限制 5MB/类型白名单，头像限制 2MB。提交时根据标签自动审核规则（isAutoAudit + 时间窗口）决定作品自动通过还是进入待审。

**证据**：F-007（Tiptap + sanitize-html 依赖）、F-019（submit/ 下 4 个 Step 组件+RichTextEditor）、F-086（/api/file COS 上传：5MB限制、类型白名单、uploads/{date}/{uuid} 路径）、F-087（/api/avatar 头像上传：2MB、avatars/{userId}-{timestamp} 路径）、F-104（rich-text.ts 白名单配置+stripHtmlTags+sanitizeRichText）、F-079（POST /api/submit 事务五表写入+自动审核逻辑）、F-071（PUT /api/works 更新时重新 sanitize 并重建标签/截图关联）、F-105（work-form.ts zod 校验：story 20-2000 纯文本、highlights 1-5、screenshots 1-5）、F-099/F-130~F-132（COS SDK 初始化与删除）

**反常识**：
1. **为什么不直接从前端直传 COS？** 直传需要前端持有 COS 密钥或使用预签名 URL，本项目选择服务端代理上传（/api/file 接收文件后 PUT 到 COS），虽然增加了服务器带宽开销，但避免了密钥泄露风险和前端 CORS 配置复杂度；
2. **为什么 sanitize 在服务端做而不是前端？** 前端 sanitize 可以被绕过（直接发 HTTP 请求），**服务端 sanitize 是安全底线**，前端 sanitize 只是用户体验优化（实时预览净化效果）；
3. **为什么标签关联用"删后重建"而不是增量更新？** 更新作品标签时先删 WorkTagRelation 再重建，虽然简单粗暴，但避免了复杂的 diff 逻辑，且标签数量有限（1-5 个），性能影响可忽略。

**行动**：
- **先看** lib/rich-text.ts 白名单配置和 app/api/file/route.ts COS 上传逻辑；
- **再看** submit/submission-form.tsx 和 4 个 Step 组件理解多步表单流程，以及 app/api/submit/route.ts 的事务+自动审核逻辑；
- **扩展点**：新增富文本格式（如表格、图片内嵌）需要同步更新 RICH_TEXT_SANITIZE_OPTIONS 白名单；换用其他对象存储（S3/OSS）只需替换 cos.ts 实现；
- **常见误区**：永远不要信任前端提交的 HTML，服务端 sanitize 是必须的；不要放宽 a 标签的协议白名单（javascript: 是 XSS 入口）；COS 密钥必须通过环境变量注入，不能硬编码。

---

### 洞察六：Docker 三阶段构建 + Nginx 反向代理的容器化部署

**陈述**：部署方案采用 Docker 三阶段构建（base→builder→runner）+ docker-compose 多服务编排。三阶段构建：base（node:20-slim + openssl）、builder（安装构建依赖 + npm ci + prisma generate + next build）、runner（仅复制 standalone 输出 + .next/static + prisma + 必要 node_modules，镜像体积极小）。docker-compose 编排 5 个服务：app（主应用，端口 3000，依赖 app-init 完成）、app-init（初始化容器，RUN_DB_INIT=true 执行 prisma db push + seed，完成后退出）、db（postgres:16-alpine，性能调优）、redis（redis:7-alpine，256MB LRU）、nginx（nginx:alpine，端口 80，反向代理到 app）。entrypoint.sh 支持"仅初始化"和"初始化+启动"两种模式，通过环境变量切换。

**证据**：F-134（三阶段 Dockerfile）、F-135（自定义镜像源加速国内构建）、F-136（构建参数传递 COS/NEXTAUTH 环境变量，DATABASE_URL 占位）、F-137（entrypoint.sh：等待 DB → prisma db push → seed → 条件启动）、F-138~F-139（docker-compose 五服务定义+数据库连接串配置）、F-125（next.config.ts output='standalone' 为 Docker 优化）、F-140~F-141（多 compose 配置文件、nginx 多配置、volumes/network 定义）

**反常识**：
1. **为什么需要 app-init 单独容器？** 很多项目在 app 容器启动脚本里顺跑 migration，但如果部署多个 app 实例（水平扩展），多个容器同时执行 prisma migrate 会冲突。app-init 用 `restart: no` 确保只执行一次，成功后退出，app 容器通过 depends_on 等待它完成再启动。
2. **为什么 output='standalone'？** Next.js 默认输出包含所有 node_modules（数百 MB），standalone 模式自动追踪用到的依赖，输出仅几十 MB，大幅减小镜像体积。配合 outputFileTracingExcludes 排除 SWC 二进制，进一步压缩。
3. **为什么 Redis 是可选的？** docker-compose 包含 redis 服务，但应用代码中并未看到 Redis 作为缓存/会话存储的使用——它可能是为 NextAuth 速率限制或未来功能预留的基础设施。

**行动**：
- **先看** Dockerfile 三阶段构建和 entrypoint.sh 启动逻辑；
- **再看** docker-compose.yml 五服务编排和 nginx.conf 反向代理配置；
- **扩展点**：生产部署使用 docker-compose.prod.yml；2C8G 低配服务器使用 docker-compose.2c8g.yml；需要负载均衡时使用 nginx-lb.conf 或 nginx-lb-2.conf；
- **常见误区**：构建时不要传入真实 DATABASE_URL（构建不需要数据库连接，用占位符即可）；app-init 必须在 app 之前完成（depends_on + healthcheck）；不要在 runner 阶段复制 devDependencies。

---

### 洞察七：双状态审核 + 三类审计日志的治理闭环

**陈述**：内容审核采用 WorkStatistic 双状态机：auditStatus（0=待审/1=通过/2=拒绝）控制内容合规性，displayStatus（0=下架/1=上架）控制内容可见性，两个维度正交独立（通过的内容可以下架，拒绝的内容不影响作者查看）。审核操作记录到 WorkAuditLog（记录 prevStatus→newStatus 变更、审核人、原因、时间）。全系统还有两类系统级日志：SysAuthLog（认证事件：登录/注册/登出的成功失败、IP、UA、metadata）和 SysOperationLog（操作事件：模块+动作+目标+操作者+IP+UA+payload+成功/失败）。封禁机制也通过字典表实现：banned_users 字典存储被封禁用户 ID，登录时和 JWT 回调时双重检查，封禁后清空存量 session。

**证据**：F-037（WorkStatistic 双状态字段+lastAuditAt）、F-039（WorkAuditLog 记录 prevStatus/newStatus/reason/auditorId）、F-043（SysAuthLog 含 authType/authChannel/authStatus/IP/UA/metadata/clerkId 多索引）、F-044（SysOperationLog 含 module/action/targetType/targetId/success/errorMessage/Method/Path/payload 多索引）、F-060（authorize 回调检查 isUserBanned）、F-062（jwt callback 在 Node.js runtime 检查封禁并清空 token.id）、F-064（signIn event 写入认证日志）、F-073（点赞记录操作日志）、F-074（浏览量记录操作日志）、F-079（提交作品记录操作日志+自动审核写 auditLog）、F-083（封禁/解封 API 禁止 admin/root）、F-102（audit-log.ts 工具函数：BigInt 序列化/IP 提取/UA 捕获/不抛异常）、F-103（ban.ts 60 秒内存缓存+自动 ensureDict）、F-092~F-093（管理后台日志查询 API 支持筛选/日期范围/分页）

**反常识**：
1. **为什么需要 displayStatus 和 auditStatus 两个状态？** 直觉上"审核通过=可见"一个状态就够了。但实际运营中存在"审核通过但需要临时下架"（如收到投诉、内容需要修改）和"审核拒绝但允许作者查看编辑重新提交"的场景，单状态无法表达这些组合。
2. **为什么日志记录在 lib/audit-log.ts 中封装而不是在每个 route 里直接写？** 统一封装保证了日志格式一致、BigInt 安全序列化、IP/UA 自动提取、失败不影响主流程（try-catch 不抛异常）。
3. **为什么封禁检查在两个地方做？** authorize 回调阻止新登录，jwt callback 清空存量 session——如果只检查 authorize，已登录的封禁用户仍可操作直到 JWT 过期；如果只检查 jwt，新的登录尝试不会被拦截。双重检查形成完整闭环。
4. **Edge Runtime 下不做封禁检查？** jwt callback 明确标注 Edge Runtime 下跳过（因为 Prisma 无法在 Edge 运行），这是一个已知的安全权衡：Edge 部署下封禁生效有延迟。

**行动**：
- **先看** lib/audit-log.ts 日志工具的 IP 提取、BigInt 序列化、不抛异常设计；
- **再看** lib/ban.ts 封禁机制的字典复用和 60 秒缓存，以及 lib/auth-nextauth.ts 的双重封禁检查；
- **扩展点**：新增需要审计的操作时，调用 writeOperationLog 并传入 module/action/targetType/targetId；新增审核动作需要同步写 WorkAuditLog 记录状态变更；
- **常见误区**：审计日志写入必须用 try-catch 包裹（不能因日志失败阻断主流程）；禁止封禁 admin/root 用户（F-083）；不要依赖前端传递的 IP/UA，必须从服务端 Request headers 获取。

---

## 知识地图

### 学习路径（分层次）

#### 🟢 入门层（理解项目是什么）
1. **项目概览**：读 package.json（F-001~F-014）了解技术栈和 npm scripts
2. **目录导航**：读 F-015~F-026 了解 src/ 结构和 API 路由分布
3. **本地启动**：npm install → prisma generate → prisma db push → npm run seed → npm run dev
4. **页面浏览**：访问首页、作品列表、排行榜、登录/注册，建立全局感性认识

#### 🟡 核心架构层（理解怎么设计的）
5. **数据模型**：读 schema.prisma（F-027~F-047），重点理解 Work 五表分表（洞察一）和 SysDict/SysDictItem（洞察二）
6. **认证与权限**：读 auth-nextauth.ts + auth.ts（F-058~F-067），理解 NextAuth Credentials 流程和角色检查
7. **国际化路由**：读 middleware.ts + language/ 三件套（洞察三），理解 [language] 动态段和三层中间件
8. **API 层**：选读 works/route.ts 和 submit/route.ts（F-070~F-079），理解服务端 Prisma CRUD + zod 校验 + 事务模式

#### 🔴 扩展机制层（理解怎么改）
9. **数据访问三层**：读 prisma.ts + works-store.ts + use-works.ts（洞察四），理解服务端→zustand→react-query 分层
10. **内容提交管线**：读 rich-text.ts + file/route.ts + submit 表单（洞察五），理解 sanitize + COS 上传 + 事务写入
11. **字典与配置**：读 ban.ts + dictionaries API（洞察二/七），理解如何复用字典表实现可配置功能
12. **审核与日志**：读 audit-log.ts + console/works 审核 API（洞察七），理解双状态机和审计闭环

#### 🟣 部署运维层（理解怎么跑）
13. **Docker 部署**：读 Dockerfile + entrypoint.sh + docker-compose.yml（洞察六），理解三阶段构建和五服务编排
14. **环境变量**：读 .env.example 了解必需的环境变量（DATABASE_URL、NEXTAUTH_SECRET、COS_*）
15. **生产配置**：对比 docker-compose.yml / docker-compose.prod.yml / docker-compose.2c8g.yml，了解不同规模下的配置差异

---

### 概念文档与事实映射表

| 概念文档 | 覆盖事实编号 | 核心内容 |
|---|---|---|
| 项目概览与技术栈 | F-001~F-014 | Next.js 15 + React 18 + Prisma + NextAuth + next-intl + Tiptap + COS |
| 目录结构与文件组织 | F-015~F-026 | src/ 五大子目录、API 路由分布、组件分层、配置文件 |
| 数据模型设计（Work 五表） | F-033~F-042, F-071, F-079 | WorkBase/Detail/Image/Team/Statistic 垂直分表与级联策略 |
| RBAC 权限模型 | F-031~F-032, F-048, F-065~F-067, F-082~F-084 | root/admin/common 三角色与权限检查 |
| 动态字典系统 | F-028~F-029, F-049~F-055, F-085, F-129 | SysDict/SysDictItem 设计、labelI18n、CRUD API |
| NextAuth 认证流程 | F-058~F-064, F-068~F-069 | Credentials provider、JWT session、signIn event |
| 用户封禁机制 | F-049, F-060, F-062, F-083, F-103 | 字典复用、双重检查、内存缓存 |
| 国际化架构 | F-110~F-118, F-126~F-129 | [language] 动态段、next-intl 三件套、双层 layout |
| 中间件链 | F-113~F-116 | auth wrapper → 受保护路由 → i18n middleware |
| 作品 CRUD API | F-070~F-079, F-095~F-097 | 列表/详情/提交/更新/点赞/浏览/统计/审核 |
| 富文本安全 | F-007, F-104, F-071, F-079 | Tiptap 编辑器、sanitize-html 白名单、stripHtmlTags |
| COS 对象存储 | F-009, F-099, F-086~F-087, F-130~F-133 | 服务端代理上传、路径规则、类型/大小限制、删除 |
| 状态管理三层 | F-098, F-107, F-109, F-118~F-119 | Prisma/zustand/react-query 分层与职责 |
| 表单校验 | F-105, F-008, F-071, F-079 | zod schema 构建、react-hook-form 集成 |
| 审计日志 | F-043~F-044, F-102, F-092~F-094 | SysAuthLog/SysOperationLog/WorkAuditLog 三类日志 |
| Docker 部署 | F-134~F-141 | 三阶段构建、entrypoint 初始化、compose 五服务、Nginx |
| UI 组件体系 | F-006, F-021, F-120~F-123 | shadcn/ui + Radix UI + Tailwind + 粒子背景 |

---

### 示例文档规划表

| 示例名 | 内容描述 |
|---|---|
| 01-快速启动.md | 从零到一：环境准备 → 数据库初始化 → seed → 启动开发服务器 → 访问首页 |
| 02-提交作品全流程.md | 以用户视角走通作品提交流程：注册 → 登录 → 四步表单 → 提交 → 等待审核 |
| 03-添加新分类.md | 演示如何通过管理后台字典 API 新增一个作品分类（无需改代码） |
| 04-扩展作品字段.md | 演示如何为作品新增一个"视频链接"字段：schema.prisma 修改 → API 更新 → 前端表单 |
| 05-新增语言支持.md | 演示如何添加第四种语言（如韩语 ko-KR）：routing.ts → 翻译文件 → 中间件正则 |
| 06-自定义富文本格式.md | 演示如何在 Tiptap 中扩展表格支持，并同步更新 sanitize 白名单 |
| 07-Docker生产部署.md | 演示生产环境部署：环境变量配置 → docker-compose.prod.yml → Nginx HTTPS |
| 08-审核操作指南.md | 演示管理员审核流程：查看待审列表 → 通过/拒绝（填写原因）→ 上架/下架 → 查看日志 |

---

### 引用文档规划表

| 文档名 | 来源/位置 | 用途 |
|---|---|---|
| Prisma 官方文档 | https://www.prisma.io/docs | ORM 查询、事务、迁移、relation 查询参考 |
| Next.js App Router 文档 | https://nextjs.org/docs/app | RSC、Server Actions、Route Handler、middleware 参考 |
| NextAuth v5 文档 | https://authjs.dev/ | Credentials provider、JWT session、callbacks 参考 |
| next-intl 文档 | https://next-intl.dev/ | 国际化路由、Server/Client 组件翻译、middleware 参考 |
| Tiptap 文档 | https://tiptap.dev/docs | 富文本编辑器扩展、命令、节点配置参考 |
| sanitize-html 文档 | https://github.com/apostrophecms/sanitize-html | HTML 白名单配置、允许标签/属性参考 |
| 腾讯云 COS SDK 文档 | https://cloud.tencent.com/document/product/436 | 对象存储上传/删除/签名 URL 参考 |
| Tailwind CSS 文档 | https://tailwindcss.com/docs | 工具类、暗色模式、自定义主题参考 |
| shadcn/ui 文档 | https://ui.shadcn.com/ | 组件安装、主题配置、变体参考 |
| Docker 多阶段构建文档 | https://docs.docker.com/build/building/multi-stage/ | 三阶段构建最佳实践参考 |
| react-query 文档 | https://tanstack.com/query/latest | useQuery/useMutation、缓存策略、staleTime 参考 |
| zustand 文档 | https://zustand.docs.pmnd.rs/ | 客户端状态管理、Map 缓存模式参考 |
| zod 文档 | https://zod.dev/ | Schema 校验、类型推断、错误处理参考 |
