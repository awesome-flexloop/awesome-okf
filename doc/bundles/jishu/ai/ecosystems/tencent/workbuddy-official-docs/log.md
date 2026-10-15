# 变更日志

## 2026-10-15 - 初始版本

- ✅ 按方法论编排知识沉淀链路 `R→I→E→V` 完成（七概念场景 4：知识沉淀；产品官方文档教程化骨架：index + concepts + examples + references + log）。
- ✅ 内容敏感度预检：`www.workbuddy.cn` 为腾讯官方公开站点（无访问控制、无 `code/token` 参数），判定**公开内容（Public）**，走标准工作流；spec 位于主仓 `.trae/specs/okf-wiki-ecosystem/workbuddy-official-docs-okf-wiki/`（spec.md / tasks.md / facts.md，Review 后补 review.md）。
- ✅ 覆盖范围经用户确认：**全站四区**（`/docs/workbuddy/` 主文档区 + `/docs/enterprise/` 企业版区 + `/docs/workbuddyapp/` 移动端 + `/docs/workbuddymini/` 小程序端）+ 官网首页；知识包归属经用户确认为 `jishu/ai/ecosystems/tencent/`（腾讯生态分组，与既有 3 个 WorkBuddy 束同组）。
- ✅ 信源获取：机械读取 `sitemap.xml`（官网）与 `docs/sitemap.xml`（文档站，下挂 5 个 urlset），枚举 **190 个 URL**（官网 12 + 文档站 178：root 1 / workbuddy 117 / enterprise 27 / workbuddyapp 15 / workbuddymini 18）；逐页采集 **183 页纯文本**（urllib + UTF-8 解码 + script/style/nav 剥离），7 页 HTTP 404 如实登记。
- ✅ 客户端渲染（SPA）页改用渲染抓取核实：企业版区 27 页全部为 SPA（纯 HTTP 仅得「正在加载文档…」占位），经 WebFetch 渲染 + 浏览器侦察 + 独立子代理批量抓取，取得 6 处真实正文（产品概述 `215844473657589760`、产品优势 `215846215905308672`、登录及更新、账号管理/企业管理员、Skill 管理、购买方式）；官网首页纯 HTTP 抽取仅 26 字符（SPA），改用渲染抓取取得产品定位、AI 场景、腾讯生态、隐私与安全、下载入口全部正文。
- ✅ 登记事实 **F-001 ~ F-520**（520 条），编号连续无跳号无重复。分区区间：W1-top F-001~F-104（104）、W1-features F-105~F-242（138）、W1-kb-publish F-243~F-312（70）、W3W4-clients F-313~F-421（109）、W0W2-site-enterprise F-422~F-514（93）、W0-homepage F-515~F-520（6）。spec `facts.md` 与本束 `references/article-source.md` **同源生成，各含 520 行表行**，编号集合机械相等。
- ✅ 四类口径分层全部落实：
  1. **官网宣传口径 vs 文档可配置项**：官网首页三项安全宣称（TLS/AES-256 与密钥托管 F-515、RBAC 与操作审计日志 F-516、ISO 27001 / SOC 2 / 等保三级 F-517）在文档站四区**零印证**且官网无证书查询入口；文档侧对应为安全中心 13 分组（F-202）、权限模式两档（F-198 ~ F-201）、资料库权限四档（F-166）。
  2. **三端差异**：桌面端 / App / 小程序端同名功能页 13 组主题差异逐条登记（执行环境命名、欢迎区形象、工具面板入口、发起任务方式、专家页名、模型页是否给倍率、定时任务添加方式、设置页集合、多端协同建联、产物分享、任务执行末节、微信文件打开等），原始事实 F-315 / F-323 / F-327 / F-332 / F-335 / F-338 / F-341 / F-345 / F-352 / F-356 / F-360 / F-364 / F-368 / F-372 / F-375 / F-379 / F-382 / F-384 / F-387 / F-390 / F-395 / F-399 / F-403~F-405 / F-409 / F-412 / F-415。
  3. **企业版 vs 个人版边界**：席位与起购量（F-505、F-508）、每成员默认 2000 积分限额（F-507）、腾讯统一身份（旗舰版接入 / 专享版未接入，F-490）、Skill 双层策略与优先级「黑名单 > 白名单 > 默认允许」（F-495、F-496）、模型管控（F-197）、三种交付形态（F-484）逐项归属；并显式提示「旗舰版」在个人套餐（F-068）与企业 SaaS 版（F-485）中同名不同义。
  4. **版本时效**：更新日志最新 5.7.7（2026-10-08，F-082）与历史版本下载页同版本 2026-10-09（F-042）相差 1 天；企业版页面页脚时间戳跨 2026-07-06 ~ 2026-09-19（F-488、F-503、F-511），与其 sitemap 时间戳 2026-10-14 不同步。
- ✅ 勘误清单 E-1 ~ E-6 全部登记：官网 sitemap 收录 7 个 404 着陆页、企业版语义路径与实时路由不成对应（实时站规范 URL 改用数字 ID）、SPA 页面纯 HTTP 抓取不可用、`/privacy` 实为《腾讯云代码助手隐私保护声明》且全文无 WorkBuddy 品牌、同版本 5.7.7 双日期、官网侧品牌命名不统一（`/blog` 与 `/docs` 标题为 CodeBuddy 品牌）。
- ✅ 无核心声明证伪；status 定 `stable`，`stale_after: 2027-04-15`（按快速迭代的产品文档设定）。信源距离评估明示「单一厂商自述、无第三方核验、认证声明无证书编号」。
- ✅ 操作可复现性两问判定为「**是**」（官方提供安装、任务创建、连接器/MCP 接入、技能与专家、知识库、定时任务、应用发布、企业后台配置等可照做链路）→ **设 `examples/`**，9 篇；但本束**未在本机安装或实跑**，所有用例逐段标注「未在本机实跑，依据官方文档（F-xxx）」。
- ✅ 产出 29 个 Markdown：根 `index.md` + `log.md` + `concepts/`（index + 12 篇）+ `examples/`（index + 9 篇）+ `references/`（index + article-source + source-manifest + verification）。
- ✅ 页级覆盖台账：**已学习 150 / 未取得 40**（客户端渲染占位 27、仅站点标题占位 6、HTTP 404 7，三类逐条注明原因）；sitemap 集合与已处理集合双向差集为 0；`Changelog-*` 版更明细页 **23 篇**（连同更新日志汇总页共 24 行）按「归纳覆盖」登记，未逐字转录。
- ✅ 与同分组既有束的关系：**互链不覆写**——本束根 index「主题关联」链 5.0.10/5.0.12、workbuddy-one-sentence-mvp、workbuddy-sandbox-public-endpoint、tencent-buddy-family、codebuddy、octop；`workbuddy-one-sentence-mvp/index.md` 仅回补一条指向本束的链接（最小改动，其事实与计数零改动）。本束独立复核确认更新日志止于 5.7.7，与 `wecom-5-0-12-release` 记录的「通稿先行、官方未同步（5.8.0）」口径**互证一致**。
- ⚠️ 观测记录（不扩大修复，非本束引入）：`/docs/enterprise/` 的 sitemap 语义路径大面积失效与实时站点改用数字 ID，属站点侧结构问题，本束只在 `verification.md` 勘误中记录，不尝试修复官方站点。
- ⚠️ `invoke gates.*` 未运行（子项目可选文档依赖 invocations 未确认安装）；已直接运行底层门禁脚本（`check-bundles-index.py` / `check-utf8.py` / `check-toctrees.py`）并完成 F 双份、相对链接、frontmatter、禁用路径等手动等效机械核对。
- ⚠️ 采集与复算过程中的临时产物（抓取缓存、合并脚本、复算脚本）全部位于工作区外（系统临时目录），未落入仓库；`facts.md` 为 spec 目录工作产物。

## 备注

- 本束的 `references/article-source.md` 体量较大（约 195 KB，520 行事实表），属**刻意**设计：口径分层与「未取得」逐条登记需要完整台账；检索时建议按 `F-\d{3}` 定位，或先读[核验报告](references/verification.md)按口径跳转。
- 复核时点建议：`stale_after: 2027-04-15`。复核优先级：①更新日志最新版本（F-081）；②企业版文档区是否已补齐独立正文（勘误 E-2）；③官网三项安全认证是否补充证书编号（口径 1）；④价格与限额（F-068、F-309、F-507）。
