# 变更日志

## 2026-09-28

### 同主题合并：两束归一（seven-concepts 场景 3 重构，I→F→A→V→C）

- **触发**：用户判定 `inurl-unified-token/`（信源 A：09-02《省钱实录》）与 `inurl-byok-free-models/`（信源 B：09-04《一年省下5000块》）为同账号同产品同主题，不应分束。session=`sc-20260928-inurl-merge`。
- **F 决策（用户拍板）**：① 新建中性束名 **`inurl-byok-token-hub/`**（git mv 自主束保历史，byok 束吸收后删除，两旧路径均不保留）；② 第二文 F-001~F-035 经逐条去重，18 条产品/加密/CTA 类与信源 A 重复不另立编号，**17 条独有事实顺延 F-106~F-122**，H 区附完整「原 byok 编号→新编号/去重对应」映射表；③ byok spec 目录的 facts.md 并入主 spec（`.trae/specs/okf-wiki-ecosystem/inurl-free-models-blog-okf-wiki/`）后删除。
- **并入的独有资产**：第二博文档案与叙事骨架、「5000 块」❌ 查无出处（F-109）与 BYOK 价差逻辑、信源距离三层模型（mermaid 图入 concepts/00）、第三方独立证据为零与同号系列软文（F-116）、Agnes 国籍硬错与阶段性 $0 定价（F-117~F-119）、四家免费模型官方口径深卡（concepts/01 新增 §6）、BYOK vs API 中转架构对比图与托付前自查清单（concepts/02 新增 §7/§8）、第二文账单勘误（concepts/03 §1 增补）。
- **状态收敛**：`status: flagged` 维持（两束同为 flagged，核心勘误并集 E1–E6）；`stale_after` 取两束较早者 **2026-12-16**；sources 融合两篇博文与 9 个官方信源。
- **结构**：沿用信源 A 束 13 文件骨架（4 concepts + 1 example + 3 references + 各级 index/log），束名变更但目录深度不变，跨束相对链接全部仍可达；5 张 mermaid 图按仓库六规则统一合规化（信源距离图、BYOK 对比图随并迁入，原有 3 图 `<br/>` 改单行、边标签补引号）。
- **索引与入站**：删除 byok 束后全库 575→574 束（jishu 434→433、ai 组 214→213），组索引两旧行合一、总索引四面计数同步；`free-llm-api-roundup`、`token-economy-explosion` 两处入站链接改指新束。
- **历史日志处理**：他束 log.md 中对两旧束名的历史提及（aitokenbus/openhuman/free-llm-api-hands-on/llama-cpp/ai-agent-book）为 append-only 史实，一律不改；本文件下方完整保留两束各自的创建与复核记录。
- **R1 独立审查勘误（2026-09-28 同日补记，以本条为准）**：上文「18 条重复」应为 **14 条重复 + 21 条独有原文归并为 17 条 F-106~F-122**（权威口径以 [references/article-source.md](references/article-source.md) H.2 映射表为准）；「第三方独立证据为零（F-116）」应为 **F-117**；「Agnes 国籍硬错与阶段性 $0 定价（F-117~F-119）」应为 **F-118~F-119**（F-117=第三方证据真空）；「concepts/02 新增 §7/§8」应为仅新增 **§7**（§6–§8 属 examples/01）；「核心勘误并集 E1–E6」应作 **E1–E9**（合并新增 E7「5000 块」查无、E8 Agnes 新加坡国籍、E9 Agnes 阶段性 $0）。

### 三次复核 G5：四目标页面深度学习（/app、/#why、/models#paid、/guide）

> 以下为原 `inurl-unified-token/` 束历史记录，束名于本次合并变更，内容原样保留。

- **触发与方法**：用户指定对四目标「全面学习」（Spec Mode + seven-concepts 场景 4，session=`sc-20260928-inurl-g5`）。沿用 **curl 直打**（Chrome UA、GET 只读、未注册、未下载、未运行代理），新增：① catalog 全量计数 + SHA-256 哈希审计；② /app 前端渲染文本与内联 JS 接口枚举（证据形态限定为「界面显示」）；③ 对页面自认的外部参照 OmniRoute 做四源 WebSearch 交叉（官网/npm/GitHub/媒体）。四目标 HTTP 全 200。
- **新增事实 F-088~F-105（18 条，✅8/⚠️8/❌2/🔄0）**，双份登记于 spec `facts.md` G5 与本束 `references/article-source.md` G5，集合机械比对：两份均 105 条、001~105 连续、集合相等、与旧编号零交集。
- **裁决：`flagged` 第三次维持**（`stale_after: 2026-12-31` 不变；合并后统一为 2026-12-16）。catalog 与 G4 **字节级同一文件**（428,592 字节，SHA-256 `3F689C…BD0F1`，F-088）：定价/3 密钥（F-089）、46=17+29 结构与 10 家隐藏（F-090）、三处错误口径三审未改（F-092 ❌）、turnstile/短链/track.js（F-093/F-105）全部零迭代。
- **主要新增点**：① /app 仪表盘四组件（F-094）、19 路由策略 + 5 档压缩（Lite≈15%/Standard≈30%/Aggressive≈50%/Ultra≈75%/RTK 60–90%，均自述估算）+ Combo（F-095）、自定义厂商 OpenAI/Anthropic/Gemini 三协议（F-096）；② 系统管理后台八模块，含个人收款码人工核销与待核销订单（F-097）；③ 套餐页 `/api/billing/mock-paid` 与支付宝 checkout 并存、源同步 shared/catalog.json + refresh_catalog.mjs 自述（F-098）；④ 用户类 401/admin 类 403 分层，ads/news 无鉴权公开；news 首条标题（千问 3.8-MAX 首发）与摘要（GPT-4o 生图）文不对题（F-100 ❌）；⑤ /models#paid 付费卡整体落后当期旗舰 ≥1 大版本（F-103）；⑥ OmniRoute 开源对标实体经四源核实为真（MIT、npm v3.8.49、:20128、19 策略/RTK+Caveman 自述 15–95%，F-104）；⑦ guide 细化 AUTO_MODELS/AUTO_PROVIDER_ORDER、auto/default/inurl 别名、shell:startup/taskkill 保活停止（F-102）。
- **文件变更（11 个，其中新增 1 个）**：**新增** references/`omniroute-benchmark.md`（唯一新文件，四源信源专页，related_facts [F-095,F-104]）；根 `index.md`（reverified 双条 + G5 横幅 + 导航 + 边界 5–8）、`log.md`；concepts `00`（§3.2 G5 补注）、`01`（§5④ 付费区陈旧）、`02`（§3.1 路由/压缩/自定义厂商 + §6 OmniRoute 对标）、`03`（§5.1 三审时效指针）；examples `01`（§6–§8 路由变量/自定义厂商/保活停止）；references `article-source.md`（G5 双份登记）、`verification.md`（§8 三次复核全节）、`index.md`（OmniRoute 行 + toctree）。spec 侧同步更新 `facts.md`、`spec.md`（§10 G5 段）与 `tasks.md`。
- **纪律**：/app 一切能力均写「界面显示提供」未写后端实测；自述数字标「估算/约」；OmniRoute 小节显式不作抄袭/侵权判定；姊妹束 `inurl-byok-free-models/` 与三级索引计数当时一律不动；G5 改动经子模块提交 `ba7e6343`、主仓库 `062282031`+`1009507ac` 已入库。

### 二次复核 G4：站点直证（用户指令驱动，提前于 stale_after）

- **二次复核（用户指令驱动，提前于 stale_after）**：按 seven-concepts 场景 4（R→I→E→V）对产品站 `token.inurl.link` 做**直接实测式增量更新**（CMD-LOG session=`sc-20260928-inurl-site-refresh`），不再依赖推广博文。browser_use 子代理受站点防护拦截零产出，改用 **curl 直打**（Chrome UA；未注册、未下载、未填信息）抓取四页面 HTML 与公开 GET 接口（`/api/catalog[?all=1]`、`/api/billing/plans`、`/api/turnstile`、`/api/provider-meta`）及主域 `inurl.link/track.js`、inurl.link 根页，本地 HTMLParser/JSON 解析。
- **新增事实 F-071~F-087（17 条，✅6/⚠️8/❌2/🔄1）**，双份登记于 spec `facts.md` G4 与本束 `references/article-source.md` G4，编号连续无跳号。
- **复核裁决：维持 `flagged`**——核心 ❌ 原样成立：免费档 3 密钥与 ¥9.9/¥29.9 定价未变（F-072）、DeepSeek 仍 tier=paid（F-076）；站点目录继续重复 Agnes 百万上下文/百度每月 100 万/LongCat-2.0 免费 1M 三处已勘误口径且 12 天未修正（F-079 ❌）。
- **主要变更点**：①catalog 428,592 字节、46 家 = 17 free + 29 paid，10 家 public:false（含 localhost mock 测试厂商、通用 openai-compatible）随公开接口无鉴权下发（F-077）；②/guide 迭代——跨平台 byok-launch.sh（Node 18+）、6 条 FAQ、额度手填/用量统计、/v1/models 说明（F-081）；③inurl-video/inurl-audio 因 capabilities 仅 text/code/image 而当前空转（F-082）；④首页新增免注册「实时演示」（F-083）；⑤四页加载主域自研 track.js 分析器（F-084）；⑥F-057 工程信号订正：随机路径实为 401 裸 JSON、Vite HMR 残留已消失（F-085 🔄）；⑦主域变为「互联网精选导航」门户、获取 Key 链接系统化走短链（F-086）；⑧加密链 PBKDF2 10 万/SHA-256/AES-GCM-256/双 escrow 与 5 个博文模型 id 复核未变（F-074/F-075）。
- **文件变更（9 个）**：根 `index.md`（reverified frontmatter + 横幅 + 导航/时效边界）、`log.md`；concepts `00`（§3.1 复核摘要）、`01`（§5 站点目录复核）、`02`（跨平台启动器/空类别/track.js/定价）；examples `01`（截点/启动器/空类别注记）；references `article-source.md`（G4 双份登记）、`verification.md`（§7 二次复核全节 + 信源）、`index.md`（导航描述）。未改动：concepts `03`、concepts/examples 子 index。spec 侧同步更新 `.trae/specs/.../facts.md`（G4 + 裁决）与 `spec.md`（页首复核说明）。
- **门禁**：check-utf8.py / check-toctrees.py / check-bundles-index.py 三脚本 + 双份 F 编号集合机器比对（F-001~F-087 连续一致）+ 束内链接 Test-Path + 零 file:/// 检查。他人 WIP（tencent/lightvela、workbuddy 等未提交变更）未触碰。

## 2026-09-16

### 信源 A 束创建：《一个程序员的省钱实录：从月付 500 到 0 元》

- **创建**：微信公众号推广博文《一个程序员的省钱实录：从月付 500 到 0 元》（风信旗/检校千牛卫，2026-09-02）经 blog-article-to-okf-wiki 七阶段工作流（seven-concepts 场景 4：知识沉淀 R→I→E→V）转化为 OKF v0.2 知识包（原名 `inurl-unified-token/`）。
- **事实登记**：F-001~F-043 博文事实（browser_use 提取 `#js_content` 全文，绕过微信反爬）；F-044~F-070 三独立子代理核验补充（产品站点实测 / 国内模型官方口径 / 海外定价时效），双份登记于 spec `facts.md` 与本束 `references/article-source.md`，编号连续无跳号。
- **核验结果**：P0 共 11 ✅ / 7 ⚠️ / 4 ❌（F-060 时间线矛盾、F-064 DeepSeek 免费失实、F-069 旗舰型号过时、F-070「17 家 Key + 0 元」定价冲突）。核心声明证伪 → `status: flagged`，`stale_after: 2026-12-31`。
- **文件集（12 个）**：根 `index.md`、`log.md`（2）；concepts 4 篇 + 子 index（5）；examples 1 篇 + 子 index（2）；references 2 篇（article-source/verification）+ 子 index（3）。
- **门禁（2026-09-16 实测）**：直接运行子模块脚本（Python 3.13，无需 invocations）——`check-utf8.py` 通过（10407 文件）；`check-toctrees.py` 本束 14 文件全部可达（已接入组 index 导航表 L76 + toctree），残留告警均属其他并行会话未完成 WIP；`check-bundles-index.py` 本束已被工作树扫描计入，残留漂移为他会话新增束未同步，按「谁添加谁对账」不属本束债务。双份 F 编号集合机器比对一致（F-001~F-070 连续）、束内相对链接全部 Test-Pass、零 file:/// 与家目录泄露。
- **并行会话说明**：同库另有姊妹篇转化束 `inurl-byok-free-models`（同账号同产品的另一篇软文《同事偷偷用这个网站，一年省下5000块》2026-09-04）并行生产；两束完成后在「主题关联」段互链。组 index 编辑期间与他会话写入发生一次碰撞（粘连行），已修复。

### 信源 B 束创建：《同事偷偷用这个网站，一年省下5000块 Token 费用》

> 以下为原 `inurl-byok-free-models/` 束历史记录（2026-09-28 合并入本束），原样保留。

**Status**: `flagged`（F-007 标题省钱数字查无出处；F-017 Agnes 国籍与上下文两处硬错；F-026/F-029 产品匿名运营、第三方证据为零）

- **S0 预检**：微信公开文章（无访问控制参数）→ 公开内容；spec 落 `.trae/specs/okf-wiki-ecosystem/inurl-byok-free-models-blog-okf-wiki/`
- **R 信源+事实**：browser_use 取 `#js_content`（2090 字符，两轮交叉一致）；信源距离预判为**厂商自宣**（导流软文+注册 CTA+同号系列文）；F-001~F-025 博文事实登记
- **R 核验**：4 个独立子代理分组 P0 核验（产品/Agnes/智谱+硅基/美团）+ 本库 agnes-ai、free-llm-api-roundup 既有 bundle 交叉佐证；补充 F-026~F-035；12 组 P0：✅5 / ⚠️6 / ❌3
- **I 拆分**：操作可复现性两问皆"否"（PART 04 仅口号，无代码/配置/实测）→ 原束无 examples/；技术综述/资讯盘点骨架；归属直挂 `jishu/ai/`
- **E 生成**：references 先行（article-source + verification）→ concepts 三篇（事实/机制/资源）→ 各级 index；9 文件
- **V 审查**：四视角审查 + 机械门禁（UTF-8/双份 F 编号/toctree/相对链接/计数）；组索引与总索引接入；互链 4 个相关 bundle

核验关键发现：① 一年省 5000 块 ❌ 官网/同号软文/全网查无，BYOK 不经手 token 售卖归因不成立；② Agnes 美国 ❌ 新加坡 Sapiens Technology（PRNewswire/App Store/Tech in Asia 三源）；③ agnes-2.5-flash 百万上下文 ❌ 官方 512K（本库 agnes-ai bundle 同证）；④ Agnes 完全免费 ⚠️ 阶段性 $0（刊例 $0.05/$0.15）+20 RPM + 付费档并存；⑤ GLM-4-Flash ¥0 ✅ 250414 在线免费/128K/V0 并发 200，下线的是 GLM-4.5-Flash；⑥ 硅基 ✅ 9B 开源小模型全员 0 元，⚠️ 无 GLM-4-Flash/满血 DeepSeek，¥16 券为现行政策（180 天/至 2026-12-31）；⑦ LongCat 万亿/1M/1000 万 ⚠️ 均限 LongCat-2.0（1.6T 总参/48B 激活），1000 万须实名领、30 天有效、限时；⑧ inurl 加密/escrow ✅ 前端实测 PBKDF2(SHA-256,10 万)+AES-GCM256、escrow_pw/rec 双份；⑨ 零中转/互转/不封号 ⚠️ 仅厂商自述、本地代理闭源（localhost:3003，启动器内嵌凭据）；⑩ 运营主体/第三方证据 ❌ 无 ICP/公司/条款/联系方式，全网独立证据为零。

- **Mermaid 安全编码修复（2026-09-16）**：concepts/00 信源距离图、01 篇 BYOK vs 中转架构图按六规则修复（边标签双引号、去 `<br/>` 单行化、表情符号改文字）；`.agents/scripts/repo-check.py mermaid`（projects/ 全局排除，经 build/ 临时副本等效扫描）4 文件 0 错误 0 警告。两张图于 2026-09-28 合并时随对应章节迁入本束 concepts/00 与 concepts/02。
- **并行会话协调（2026-09-16）**：与信源 A 转化会话并行，共享文件 `jishu/ai/index.md` 两次行级粘连，稳定后统一修复并补回 8 行导航表条目；两束互链双向落地；free-llm-api-roundup、token-economy-explosion 加反向链接；官方门禁复跑 9 域/59 组/555 束五面一致。
- **原复核安排（flagged）**：2026-12-16 前复查 inurl 主体信息/第三方证据、Agnes $0 优惠、LongCat 1000 万活动续期、硅基 ¥16 券（官方至 2026-12-31）——合并后由本束统一承接，stale_after 取 2026-12-16。
