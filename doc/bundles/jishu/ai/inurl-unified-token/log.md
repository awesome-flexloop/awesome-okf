# 变更日志

## 2026-09-28

### 三次复核 G5：四目标页面深度学习（/app、/#why、/models#paid、/guide）

- **触发与方法**：用户指定对四目标「全面学习」（Spec Mode + seven-concepts 场景 4，session=`sc-20260928-inurl-g5`）。沿用 **curl 直打**（Chrome UA、GET 只读、未注册、未下载、未运行代理），新增：① catalog 全量计数 + SHA-256 哈希审计；② /app 前端渲染文本与内联 JS 接口枚举（证据形态限定为「界面显示」）；③ 对页面自认的外部参照 OmniRoute 做四源 WebSearch 交叉（官网/npm/GitHub/媒体）。四目标 HTTP 全 200。
- **新增事实 F-088~F-105（18 条，✅8/⚠️8/❌2/🔄0）**，双份登记于 spec `facts.md` G5 与本束 `references/article-source.md` G5，集合机械比对：两份均 105 条、001~105 连续、集合相等、与旧编号零交集。
- **裁决：`flagged` 第三次维持**（`stale_after: 2026-12-31` 不变）。catalog 与 G4 **字节级同一文件**（428,592 字节，SHA-256 `3F689C…BD0F1`，F-088）：定价/3 密钥（F-089）、46=17+29 结构与 10 家隐藏（F-090）、三处错误口径三审未改（F-092 ❌）、turnstile/短链/track.js（F-093/F-105）全部零迭代。
- **主要新增点**：① /app 仪表盘四组件（F-094）、19 路由策略 + 5 档压缩（Lite≈15%/Standard≈30%/Aggressive≈50%/Ultra≈75%/RTK 60–90%，均自述估算）+ Combo（F-095）、自定义厂商 OpenAI/Anthropic/Gemini 三协议（F-096）；② 系统管理后台八模块，含个人收款码人工核销与待核销订单（F-097）；③ 套餐页 `/api/billing/mock-paid` 与支付宝 checkout 并存、源同步 shared/catalog.json + refresh_catalog.mjs 自述（F-098）；④ 用户类 401/admin 类 403 分层，ads/news 无鉴权公开；news 首条标题（千问 3.8-MAX 首发）与摘要（GPT-4o 生图）文不对题（F-100 ❌）；⑤ /models#paid 付费卡整体落后当期旗舰 ≥1 大版本（F-103）；⑥ OmniRoute 开源对标实体经四源核实为真（MIT、npm v3.8.49、:20128、19 策略/RTK+Caveman 自述 15–95%，F-104）；⑦ guide 细化 AUTO_MODELS/AUTO_PROVIDER_ORDER、auto/default/inurl 别名、shell:startup/taskkill 保活停止（F-102）。
- **文件变更（11 个，其中新增 1 个）**：**新增** references/`omniroute-benchmark.md`（唯一新文件，四源信源专页，related_facts [F-095,F-104]）；根 `index.md`（reverified 双条 + G5 横幅 + 导航 + 边界 5–8）、`log.md`；concepts `00`（§3.2 G5 补注）、`01`（§5④ 付费区陈旧）、`02`（§3.1 路由/压缩/自定义厂商 + §6 OmniRoute 对标）、`03`（§5.1 三审时效指针）；examples `01`（§6–§8 路由变量/自定义厂商/保活停止）；references `article-source.md`（G5 双份登记）、`verification.md`（§8 三次复核全节）、`index.md`（OmniRoute 行 + toctree）。spec 侧同步更新 `facts.md`、`spec.md`（§10 G5 段）与 `tasks.md`。
- **纪律**：/app 一切能力均写「界面显示提供」未写后端实测；自述数字标「估算/约」；OmniRoute 小节显式不作抄袭/侵权判定；姊妹束 `inurl-byok-free-models/` 与三级索引计数一律不动；改动**未提交**，待 review 后给原子提交建议。

### 二次复核 G4：站点直证（用户指令驱动，提前于 stale_after）

- **二次复核（用户指令驱动，提前于 stale_after）**：按 seven-concepts 场景 4（R→I→E→V）对产品站 `token.inurl.link` 做**直接实测式增量更新**（CMD-LOG session=`sc-20260928-inurl-site-refresh`），不再依赖推广博文。browser_use 子代理受站点防护拦截零产出，改用 **curl 直打**（Chrome UA；未注册、未下载、未填信息）抓取四页面 HTML 与公开 GET 接口（`/api/catalog[?all=1]`、`/api/billing/plans`、`/api/turnstile`、`/api/provider-meta`）及主域 `inurl.link/track.js`、inurl.link 根页，本地 HTMLParser/JSON 解析。
- **新增事实 F-071~F-087（17 条，✅6/⚠️8/❌2/🔄1）**，双份登记于 spec `facts.md` G4 与本束 `references/article-source.md` G4，编号连续无跳号。
- **复核裁决：维持 `flagged`**——核心 ❌ 原样成立：免费档 3 密钥与 ¥9.9/¥29.9 定价未变（F-072）、DeepSeek 仍 tier=paid（F-076）；站点目录继续重复 Agnes 百万上下文/百度每月 100 万/LongCat-2.0 免费 1M 三处已勘误口径且 12 天未修正（F-079 ❌）。
- **主要变更点**：①catalog 428,592 字节、46 家 = 17 free + 29 paid，10 家 public:false（含 localhost mock 测试厂商、通用 openai-compatible）随公开接口无鉴权下发（F-077）；②/guide 迭代——跨平台 byok-launch.sh（Node 18+）、6 条 FAQ、额度手填/用量统计、/v1/models 说明（F-081）；③inurl-video/inurl-audio 因 capabilities 仅 text/code/image 而当前空转（F-082）；④首页新增免注册「实时演示」（F-083）；⑤四页加载主域自研 track.js 分析器（F-084）；⑥F-057 工程信号订正：随机路径实为 401 裸 JSON、Vite HMR 残留已消失（F-085 🔄）；⑦主域变为「互联网精选导航」门户、获取 Key 链接系统化走短链（F-086）；⑧加密链 PBKDF2 10 万/SHA-256/AES-GCM-256/双 escrow 与 5 个博文模型 id 复核未变（F-074/F-075）。
- **文件变更（9 个）**：根 `index.md`（reverified frontmatter + 横幅 + 导航/时效边界）、`log.md`；concepts `00`（§3.1 复核摘要）、`01`（§5 站点目录复核）、`02`（跨平台启动器/空类别/track.js/定价）；examples `01`（截点/启动器/空类别注记）；references `article-source.md`（G4 双份登记）、`verification.md`（§7 二次复核全节 + 信源）、`index.md`（导航描述）。未改动：concepts `03`、concepts/examples 子 index。spec 侧同步更新 `.trae/specs/.../facts.md`（G4 + 裁决）与 `spec.md`（页首复核说明）。
- **门禁**：check-utf8.py / check-toctrees.py / check-bundles-index.py 三脚本 + 双份 F 编号集合机器比对（F-001~F-087 连续一致）+ 束内链接 Test-Path + 零 file:/// 检查（结果见本次会话 V 阶段记录）。他人 WIP（tencent/lightvela、workbuddy 等未提交变更）未触碰。

## 2026-09-16

- **创建**：微信公众号推广博文《一个程序员的省钱实录：从月付 500 到 0 元》（风信旗/检校千牛卫，2026-09-02）经 blog-article-to-okf-wiki 七阶段工作流（seven-concepts 场景 4：知识沉淀 R→I→E→V）转化为 OKF v0.2 知识包。
- **事实登记**：F-001~F-043 博文事实（browser_use 提取 `#js_content` 全文，绕过微信反爬）；F-044~F-070 三独立子代理核验补充（产品站点实测 / 国内模型官方口径 / 海外定价时效），双份登记于 spec `facts.md` 与本束 `references/article-source.md`，编号连续无跳号。
- **核验结果**：P0 共 11 ✅ / 7 ⚠️ / 4 ❌（F-060 时间线矛盾、F-064 DeepSeek 免费失实、F-069 旗舰型号过时、F-070「17 家 Key + 0 元」定价冲突）。核心声明证伪 → `status: flagged`，`stale_after: 2026-12-31`。
- **文件集（12 个）**：根 `index.md`、`log.md`（2）；concepts 4 篇 + 子 index（5）；examples 1 篇 + 子 index（2）；references 2 篇（article-source/verification）+ 子 index（3）。
- **门禁（2026-09-16 实测）**：直接运行子模块脚本（Python 3.13，无需 invocations）——`check-utf8.py` 通过（10407 文件）；`check-toctrees.py` 本束 14 文件全部可达（已接入组 index 导航表 L76 + toctree），残留告警均属其他并行会话未完成 WIP（firecrawl/inurl-byok-free-models/openhuman/oracle 缺根 index 等）；`check-bundles-index.py` 本束已被工作树扫描计入（束数在他会话的 549 次扫盘时即含本目录），残留 +1 漂移为他会话新增束（如 llama.cpp）未同步，按「谁添加谁对账」不属本束债务。双份 F 编号集合机器比对一致（F-001~F-070 连续）、束内相对链接全部 Test-Pass、零 file:/// 与家目录泄露。
- **并行会话说明**：同库另有姊妹篇转化束 `inurl-byok-free-models`（同账号同产品的另一篇软文《同事偷偷用这个网站，一年省下5000块》2026-09-04）正在并行生产；两束完成后应在「主题关联」段互链（本束暂不链接其未完成根 index，避免断链）。组 index 编辑期间与他会话写入发生一次碰撞（粘连行），已修复。
