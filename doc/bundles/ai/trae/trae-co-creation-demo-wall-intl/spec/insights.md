# Demo Wall Intl 核心洞察与知识地图

I阶段产出：核心洞察四元组 + 知识地图设计

> **定位说明**：demo-wall-intl 是 demo-wall 中文版的**国际版变体**，共享核心架构（Next.js App Router + Prisma + NextAuth + next-intl + Tiptap + COS），针对海外 Vercel 部署场景做了定向调整。本文件重点阐述与中文版的**架构差异**及其设计意图，共享架构部分请参阅 [demo-wall/spec/insights.md](../../trae-co-creation-demo-wall/spec/insights.md)。

---

## 核心洞察（四元组）

### 洞察一：Vercel Edge Config 缓存层——海外冷启动性能优化

**陈述**：intl 版引入 Vercel Edge Config 作为字典数据（country/city/category/honor）的边缘缓存层。架构为：管理员通过 POST `/api/sync-edge-config` 手动触发同步，将四类字典序列化后（BigInt 转 string）通过 Vercel Management API PATCH 到 Edge Config；前端通过 `getDictionaries()` 函数（`@vercel/edge-config` SDK 的 `get('dictionaries')`）从边缘节点读取缓存，失败时返回 null 实现优雅降级回退到数据库查询。

**证据**：F-011（@vercel/edge-config 依赖）、F-016（新增 edge-config.ts）、F-043（sync-edge-config API 路由）、F-047（getDictionaries() 优雅降级设计）、F-066（next.config.ts 注释指向 Vercel Lambda 100MB 限制）、F-067~F-069（Edge Config 缓存目标、同步机制、读取降级）

**反常识**：
1. **为什么不用 Redis？** 中文版 docker-compose 里就有 Redis，但海外 Vercel 部署场景下，Redis 需要额外配置 Upstash 或自建实例，增加成本和延迟。Edge Config 是 Vercel 原生全球边缘网络，读取延迟 <50ms 全球一致，且与 Vercel 部署深度集成。
2. **为什么缓存字典而不是作品数据？** 字典数据（国家/城市/分类/荣誉）是**高频读取、低频变更**的典型缓存候选——每个列表页、筛选器、详情页都需要字典数据做标签解析，但字典变更仅在运营操作时发生。作品数据是高频变更的（浏览量、点赞数实时更新），不适合 Edge Config 这种最终一致的缓存。
3. **为什么是手动同步而不是自动？** 字典变更频率极低（可能数周才变一次），手动触发同步比 webhook/定时任务更简单可靠，避免了"字典改了但缓存没更新"的竞态问题。
4. **为什么优雅降级返回 null 而不是抛错？** Edge Config 不可用时（本地开发、未配置环境变量、网络故障），系统应回退到数据库查询而不是崩溃，这是弹性设计的基本要求。

**行动**：
- **先看** lib/edge-config.ts 的 getDictionaries() 实现和优雅降级模式；
- **再看** api/sync-edge-config/route.ts 的序列化逻辑（BigInt→string 是 Prisma JSON 序列化的关键细节）；
- **扩展点**：如需缓存其他低频变更数据（如系统配置、排行榜周榜），可在 sync-edge-config 中追加 key，在 getDictionaries() 同层添加 getter；
- **常见误区**：Edge Config 有大小限制（通常 1MB 以下），不要缓存大数据集；必须处理 get() 返回 null 的降级路径，不能假设缓存永远命中。

---

### 洞察二：用户治理简化——移除封禁功能的安全取舍

**陈述**：intl 版彻底移除了用户封禁功能：删除 `lib/ban.ts` 模块，移除 `/api/users/[id]/ban` 路由，authorize 回调不检查 `isUserBanned`，jwt callback 不做封禁后 session 失效处理，注册 API 不检查 `isEmailDomainBlocked`，封禁用户字典（banned_users）和屏蔽邮箱域名字典（blocked_email_domains）虽可能存在于 seed 数据中但无代码消费。

**证据**：F-016/F-046（lib 下无 ban.ts 模块，新增 edge-config.ts）、F-017（API 路由无 [id]/ban/ 子目录）、F-031~F-032（authorize/jwt 回调不做封禁检查）、F-036（注册 API 不检查邮箱域名屏蔽）、F-039（无 /api/users/[id]/ban 封禁路由）

**反常识**：移除封禁功能看似是安全退步——恶意用户无法被封禁，垃圾邮箱可以任意注册。但这个决策有其场景合理性：
1. **海外社区治理模式不同**：面向海外用户的社区通常依赖用户举报+人工审核内容，而非预防性封禁账号；
2. **降低运营复杂度**：国际版可能缺少专职运营团队，封禁功能需要配套的申诉、解封流程，移除后减少了运营负担；
3. **技术债考量**：ban.ts 的 60 秒内存缓存在多实例部署时存在一致性问题（封禁后最长需要 60 秒在所有实例生效），Edge Runtime 下还无法工作（中文版 F-062 也标注了此限制）；
4. **但这不是无条件的"简化"**：SysAuthLog 和 SysOperationLog 仍然保留，说明系统仍有审计能力，只是去掉了"主动封禁"这一动作。管理员仍可通过删除用户（DELETE /api/users）来处理严重违规。

**行动**：
- **先看**中文版 lib/ban.ts 理解被移除的功能全貌，再对比 intl 版 auth-nextauth.ts 的简化；
- **扩展点**：若国际版运营需要恢复封禁功能，需回加 ban.ts（注意适配 Edge Runtime 或接受 Node.js only）、ban API 路由、注册域名检查、authorize/jwt 双重检查；
- **常见误区**：移除封禁≠移除安全措施，内容审核（auditStatus/displayStatus 双状态机）仍然完整保留，这是最后一道防线；不要因为没有封禁功能就放松审核流程。

---

### 洞察三：语言扩展到 5 种与中间件正则遗漏缺陷

**陈述**：intl 版将支持语言从 3 种（zh-CN/en-US/ja-JP）扩展到 5 种（en-US 默认、zh-CN、ja-JP、id-ID 印尼语、vi-VN 越南语），翻译文件同步增加 id-ID.json 和 vi-VN.json，默认语言从 zh-CN 切换为 en-US。但 middleware.ts 中的 `isProtectedRoute` 正则仍硬编码为 `/^\/(zh-CN|en-US)\/(submit|console|profile)/`，未包含 id-ID 和 vi-VN，导致印尼语和越南语用户访问 `/id-ID/submit` 或 `/vi-VN/console` 时不会触发认证检查，可能造成未授权访问。

**证据**：F-018（5 个翻译文件：en-US/zh-CN/ja-JP/id-ID/vi-VN）、F-048（routing.ts 配置 5 种语言+默认 en-US）、F-050（isProtectedRoute 正则硬编码缺少 id-ID/vi-VN）、F-056~F-057（5 种语言清单及翻译文件）

**反常识**：
1. **为什么扩展东南亚语言？** id-ID 和 vi-VN 覆盖印尼和越南——东南亚是中国互联网产品出海的重点市场，人口基数大、增长快；
2. **为什么默认语言改为 en-US？** 面向国际用户，英语是最广泛的通用语，不认识中文/日文/印尼文/越南文的用户也能用英语访问；
3. **为什么正则硬编码是缺陷？** 这是一个典型的"新增语言时忘记同步修改"的 bug——routing.ts 是语言配置的单一数据源，middleware.ts 应该从 routing.ts 动态生成正则，而不是硬编码语言列表。中文版只有 3 种语言且不常变化所以没暴露问题，扩展到 5 种后就暴露了。
4. **这个 bug 的影响范围有限**——受影响的只是受保护路由（submit/console/profile），公开页面（首页/作品列表/排行榜/详情页）不受影响。但 /id-ID/console 如果没有认证检查，可能泄露管理后台数据。

**行动**：
- **先看** lib/language/routing.ts 的 locales 配置和 middleware.ts 的正则，定位遗漏点；
- **修复建议**：在 middleware.ts 中从 routing.locales 动态构建正则：`new RegExp(\`^/(${routing.locales.join('|')})/(submit|console|profile)\`)`；
- **扩展点**：新增语言时检查清单——routing.ts 添加 locale、创建翻译 JSON、labelI18n 字典数据补充、isProtectedRoute 正则同步（修复后此步自动完成）、管理后台字典翻译；
- **常见误区**：不要在多个文件中硬编码语言列表（违反 DRY）；翻译文件中的 key 必须与其他语言文件完全对齐，缺失 key 会导致运行时 fallback 或报错。

---

### 洞察四：CSV 导出——面向国际运营数据需求

**陈述**：intl 版新增管理员 CSV 导出功能（GET `/api/console/works/export`），支持选中导出（ids 参数）和按筛选条件导出，硬上限 5000 条防止内存溢出，输出带 UTF-8 BOM 以兼容 Excel，文件名含时间戳 `works_export_YYYYMMDD_HHMMSS.csv`。导出数据包含完整作品字段及 i18n 标签解析（pickI18nLabel 函数），审核状态和展示状态映射为可读标签（AUDIT_STATUS_LABEL/DISPLAY_STATUS_LABEL），实现 escapeCsv 防 CSV 注入。

**证据**：F-044/F-070~F-072（CSV 导出路由、5000 条上限、UTF-8 BOM、escapeCsv、i18n 标签解析）

**反常识**：
1. **为什么中文版没有 CSV 导出？** 国内运营通常直接登录数据库查询或使用内部 BI 工具，国际版运营人员可能没有数据库访问权限，需要通过界面导出数据做离线分析；
2. **为什么硬上限 5000 条？** 全量导出可能导致内存溢出（Node.js 单进程内存限制）和 Vercel Serverless Function 执行超时（10~60秒），5000 条是单次请求的安全上限，更大数据集需要分页导出或异步任务；
3. **为什么需要 UTF-8 BOM？** 不带 BOM 的 UTF-8 CSV 在 Excel（特别是 Windows 版）中会乱码（Excel 默认用系统编码 GBK/ANSI 打开），BOM（\uFEFF）告诉 Excel 这是 UTF-8 编码。Mac 版 Excel 和 Google Sheets 不需要 BOM 也能正确识别；
4. **为什么 escapeCsv 处理逗号/引号/换行？** CSV 格式中逗号是字段分隔符、引号是文本限定符、换行是记录分隔符，字段值包含这些字符时必须转义（双引号包裹+引号转双写），否则会导致列错位。更重要的是防 CSV 注入——字段值以 `=`/`+`/`-`/`@` 开头时 Excel 会当作公式执行。

**行动**：
- **先看** api/console/works/export/route.ts 的 escapeCsv、pickI18nLabel、formatDate 等工具函数和主查询逻辑；
- **扩展点**：可按相同模式新增用户导出、日志导出、标签导出等 CSV 端点；如需更大数据集导出，考虑改为异步生成+下载链接模式（写入 COS 后返回 URL）；
- **常见误区**：不要忘记 Content-Disposition 头设置中文文件名编码；不要在 CSV 中直接输出未转义的用户输入（XSS/CSV 注入风险）；5000 条上限是硬限制，不要随意调大。

---

### 洞察五：外键策略从 Cascade 改为 SetNull——日志数据留存哲学

**陈述**：intl 版将 SysAuthLog 的 `user` 关系和 SysOperationLog 的 `operator` 关系的 `onDelete` 从 Cascade 改为 SetNull。这意味着当用户被删除时，其认证日志和操作日志不会被级联删除，而是将 userId/operatorId 设为 null，日志记录本身保留。同时 DateTime 字段精度从 `@db.Timestamptz(6)`（微秒精度）改为 `@db.Timestamptz`（默认精度，通常毫秒）。

**证据**：F-026~F-027（SysAuthLog/SysOperationLog 外键 onDelete 改为 SetNull）、F-028（DateTime 精度简化）

**反常识**：
1. **为什么从 Cascade 改为 SetNull？** 这是一个**审计合规**决策——Cascade 删除意味着删除用户会销毁所有关联的登录日志和操作日志，在合规敏感的国际环境中（如 GDPR），审计日志的完整性可能是法律要求。SetNull 保留了"谁在什么时间做了什么"的记录，只是将操作者标识置为 null（"已删除的用户"），保证了审计链不断裂。
2. **为什么中文版用 Cascade？** 国内项目通常更注重"数据干净"——用户删除后其关联数据也清理掉，避免孤儿记录。但这牺牲了审计完整性。intl 版选择审计优先。
3. **DateTime 精度降低影响什么？** 微秒精度（6）到默认精度通常不影响业务——日志的 created_at 排序和筛选精确到秒已足够，降低精度可微幅减少存储和索引开销。

**行动**：
- **先看** intl 版 schema.prisma 中 SysAuthLog 和 SysOperationLog 的关系定义，对比中文版的 Cascade 设置；
- **扩展点**：设计数据模型时，对审计日志类表优先考虑 SetNull 或 Restrict（阻止删除有日志的用户），而非 Cascade；
- **常见误区**：SetNull 要求外键字段必须是 nullable（userId?/operatorId?），schema 设计时需要同步修改；SetNull 后查询日志时需要处理 null 用户（显示"已删除用户"而非报错）。

---

### 洞察六：部署目标从 Docker 转向 Vercel——平台化部署范式迁移

**陈述**：intl 版虽然保留了 Docker 部署能力，但多处改动表明部署目标从自托管 Docker 转向 Vercel 平台：(1) next.config.ts 的 outputFileTracingExcludes 注释从"减小 Docker 镜像体积"变为"避免 Vercel Lambda 100MB 限制"；(2) docker-compose.yml 移除 nginx 服务（Vercel 自带边缘 CDN 和 SSL）；(3) Dockerfile 构建阶段从 `npm ci` 改为更宽松的 `npm install`（Vercel 构建环境更灵活）；(4) entrypoint.sh 移除 `--accept-data-loss` 参数（更保守的迁移策略）；(5) 新增 Edge Config 集成（Vercel 原生服务）。整体定位是"Vercel 优先，Docker 兼容"。

**证据**：F-062（Dockerfile npm install 替代 npm ci）、F-064（entrypoint 移除 --accept-data-loss）、F-065（docker-compose 移除 nginx 服务）、F-066（next.config.ts 注释指向 Vercel Lambda 100MB 限制）、F-011/F-043/F-047（Edge Config Vercel 原生集成）、F-019/F-073~F-074（新增 test/ 目录和 CI 工作流，Vercel 部署通常配合 GitHub CI）

**反常识**：
1. **为什么不直接删除 Docker 配置？** Vercel 虽方便但有局限（数据库需外接、冷启动、Function 超时限制），保留 Docker 配置给了用户选择余地——可在 Vercel 上快速体验，在自有服务器上 Docker 部署生产环境。
2. **`npm install` 替代 `npm ci` 是退步吗？** npm ci 要求 lockfile 完全一致，适合 CI/CD 确定性构建；但 Vercel 构建环境有时会有依赖解析差异，npm install 更容错。在 Vercel 平台上 Vercel 自己会处理缓存和确定性，Docker 场景下用户可自行改回 npm ci。
3. **移除 nginx 意味着什么？** Vercel 提供全球 CDN、自动 SSL、边缘缓存，不需要自建 Nginx 反向代理。这是 Serverless/PaaS 部署 vs IaaS 部署的典型差异——平台接管了基础设施层。
4. **移除 --accept-data-loss 更安全吗？** `prisma db push --accept-data-loss` 会在 schema 变更可能导致数据丢失时自动确认（如删除列），适合开发环境但生产环境有风险。移除后需要手动确认变更，更安全但初始化流程更保守。

**行动**：
- **先看**中文版 docker-compose.yml 的五服务编排（含 nginx），对比 intl 版的精简版；
- **再看** intl 版 next.config.ts 和 Dockerfile 注释，理解 Vercel 适配点；
- **扩展点**：Vercel 部署需要配置环境变量（DATABASE_URL 需指向外部 PostgreSQL 如 Neon/Supabase、NEXTAUTH_SECRET、COS_*、EDGE_CONFIG_ID、VERCEL_API_TOKEN），数据库不能用 Vercel 内置的（Vercel Postgres 已弃用方向）；
- **常见误区**：Vercel Serverless Function 有执行时间限制（Hobby 10s、Pro 60s），CSV 导出 5000 条上限要考虑这个限制；Edge Config 不是通用缓存，不要当 Redis 用；Vercel 部署的文件系统是只读的，文件上传必须走外部存储（COS），不能写本地磁盘。

---

## 知识地图

### 学习路径（分层次）

#### 🟢 入门层（与中文版共享基础）
1. **前置阅读**：先完成 [demo-wall 中文版入门层学习路径](../../trae-co-creation-demo-wall/spec/insights.md)，理解核心架构（五表分表、RBAC、i18n、三层数据、富文本管线、Docker 部署、审核日志）
2. **差异速览**：阅读本文件的六个洞察，快速把握 intl 版的五个核心差异点
3. **环境选择**：决定本地开发（Docker 或 npm run dev）还是直接 Vercel 部署体验

#### 🟡 核心差异层（intl 独有架构）
4. **Edge Config 缓存**：读 edge-config.ts + sync-edge-config API，理解边缘缓存模式和优雅降级（洞察一）
5. **治理模型简化**：对比中文版 ban.ts 和 intl 版 auth-nextauth.ts，理解移除封禁的安全影响（洞察二）
6. **5 语言扩展**：读 routing.ts + middleware.ts，识别正则遗漏 bug 并理解修复方案（洞察三）
7. **CSV 导出**：读 export/route.ts，理解大数据量导出的安全措施（escapeCsv/BOM/上限）（洞察四）

#### 🔴 部署运维层（Vercel 范式）
8. **外键策略**：对比两版 schema.prisma 的日志表外键差异，理解 SetNull 的审计合规逻辑（洞察五）
9. **Vercel 部署**：理解 outputFileTracingExcludes、Edge Config 集成、无 nginx 的部署拓扑（洞察六）
10. **Docker 兼容**：对比两版 Dockerfile/docker-compose/entrypoint，理解兼容性调整

---

### 概念文档与事实映射表

| 概念文档 | 覆盖事实编号 | 核心内容 |
|---|---|---|
| Edge Config 缓存层 | F-011, F-016, F-043, F-047, F-067~F-069 | Vercel Edge Config 集成、getDictionaries() 降级、sync-edge-config 同步 |
| 用户治理简化 | F-017, F-031~F-032, F-036, F-039, F-046 | 移除 ban.ts/封禁 API/域名屏蔽/双重封禁检查 |
| 五语言国际化 | F-018, F-048, F-050, F-056~F-058 | en-US 默认、新增 id-ID/vi-VN、翻译文件、isProtectedRoute 正则遗漏 |
| CSV 数据导出 | F-044, F-070~F-072 | 5000 条上限、UTF-8 BOM、escapeCsv、i18n 标签解析 |
| 外键策略变更 | F-026~F-028 | 日志表 onDelete Cascade→SetNull、DateTime 精度简化 |
| Vercel 部署适配 | F-062~F-066, F-019, F-073~F-074 | npm install、移除 --accept-data-loss、无 nginx、Lambda 体积优化、CI/测试 |
| 共享核心架构 | F-002~F-010, F-014~F-015, F-021~F-025, F-029~F-030, F-033~F-035, F-037~F-038, F-040~F-042, F-045, F-049, F-051~F-055, F-059~F-061 | 与中文版相同的架构（五表/RBAC/API/COS/前端/审核） |

---

### 示例文档规划表

| 示例名 | 内容描述 |
|---|---|
| 01-Vercel一键部署.md | 从 GitHub 导入到 Vercel → 配置环境变量 → 连接外部 PostgreSQL → 部署成功 → 同步 Edge Config |
| 02-Edge-Config缓存实践.md | 演示字典同步流程：修改字典 → 调用 sync API → 验证边缘缓存生效 → 模拟降级回退 |
| 03-修复中间件正则Bug.md | 演示 isProtectedRoute 正则硬编码问题的发现和修复：从 routing.locales 动态生成正则 |
| 04-CSV导出与数据分析.md | 演示管理员导出作品 CSV → Excel 打开 → 利用导出数据做运营分析的完整流程 |
| 05-添加第六种语言.md | 以添加韩语（ko-KR）为例，演示正确的多语言扩展流程：routing.ts → 翻译文件 → 字典 labelI18n → 验证正则自动覆盖 |
| 06-Docker自托管部署.md | 演示使用保留的 Docker 配置在自有服务器部署 intl 版：环境变量 → docker-compose → 无 nginx 下的反向代理配置 |
| 07-审计日志与GDPR合规.md | 演示 SetNull 外键策略下的审计查询：删除用户后日志保留 → 查询"已删除用户"的历史操作 |

---

### 引用文档规划表

| 文档名 | 来源/位置 | 用途 |
|---|---|---|
| **中文版洞察文档** | [demo-wall/spec/insights.md](../../trae-co-creation-demo-wall/spec/insights.md) | 共享核心架构的完整说明（必读前置） |
| Vercel Edge Config 文档 | https://vercel.com/docs/edge-config | Edge Config SDK、限制、API 参考 |
| Vercel Serverless Functions 限制 | https://vercel.com/docs/functions/runtimes | 执行时间、内存、包大小限制参考 |
| @vercel/edge-config SDK | https://vercel.com/docs/edge-config/sdk | get/ getAll/digest 等方法参考 |
| CSV 注入防护指南 | OWASP CSV Injection | 公式注入风险和 escapeCsv 最佳实践 |
| Prisma 关系 onDelete 策略 | https://www.prisma.io/docs/orm/prisma-schema/data-model/relations/referential-actions | Cascade/SetNull/Restrict/NoAction 选择参考 |
| GDPR 数据留存要求 | https://gdpr.eu/ | 审计日志留存与用户删除权（被遗忘权）的平衡参考 |
| next-intl 多语言最佳实践 | https://next-intl.dev/docs/getting-started | 动态语言列表、中间件配置参考 |
