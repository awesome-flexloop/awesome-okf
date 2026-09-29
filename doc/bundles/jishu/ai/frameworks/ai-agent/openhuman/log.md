# 变更日志（log.md）

## 2026-09-16 初始生成

- **信源**：微信公众号「开源先驱」（作者豆芽菜小萌）博文《又一个人AI助手炸了。连续9天GitHub Trending第一，3,900次提交，7,800+ Star》（2026-07-28 06:48）
- **工作流**：blog-article-to-okf-wiki Skill 七阶段（预检→R→I→E→V→C）
- **信源获取**：按 Skill 规则不试 WebFetch（微信反爬 13/13 确定拦截），直接 browser_use 子代理取 `#js_content` innerText，全文 5,324 字符，两次独立加载元数据与长度一致
- **信源距离预判**：第三方自媒体推广文（作者自陈"翻了翻社区讨论和评测"，未声明一手实测，营销叙事浓度中高）→ 数字/功能声明全部按 P0 核验
- **骨架判定**：操作可复现性两问——①有安装/构建命令（弱是）②作者实测可复现（否）→ **不设 examples/**，技术综述/产品介绍骨架，index 顶部性质声明
- **归属判定**：`jishu/ai/ai-agent/openhuman/`（GitHub About 自我定位即 "agent harness"；分组「📰 产品资讯」板块有 15+ 非源码先例；与 second-me/pi-agent-harness 互链）；不新建分组
- **事实登记**：F-001~F-064 共 64 条（博文 42 + 核验补充 22）；作者观点 6 条、博文测算 2 条显式分层
- **P0 核验**：12 项 = 6✅（GPL-3.0/9 天 Trending README 自认/Memory Tree 机制/TokenJuice 80%/四会议平台/安装命令）+ 6⚠️（版本口径、历史 star·commits、10 亿 token 弱源、金额测算、118→100+、17→15）；**0 ❌ 硬证伪** → status: stable
- **六条勘误**：①"六十多版本"（56 releases/106 tags）②金额为博文自算 ③10 亿 token/NeoCortex 官方无数字 ④7,800/3,926 历史值不可回溯（现值 39,814/20,551）⑤118+→官方现 100+ ⑥17→官方现 15；均已在概念篇正文呈现官方现值
- **核验手段**：browser_use 直取 GitHub 渲染页 + Contents/Releases/Tags API（star/fork/release 56/tag 106/commit 20,551/license/脚本 HTTP 200）+ GitBook 两功能页 WebFetch + openhuman.dev/readthedocs/honbul 三方旁证
- **文件集**：根 index + log + concepts/（index + 4 篇）+ references/（index + article-source + verification）= 10 文件
- **gates 状态（2026-09-16 实测直跑 scripts/）**：① `check-utf8.py` **PASS**（全库 10,409 文件含本束全部新文件）；② `check-bundles-index.py` FAIL——frontmatter 550 对目录树 553（差 +3），jishu 418 对 420（差 +2）：**3 个差值全部来自并行会话当日在飞、尚未登记顶层索引的他束**（ai-agent/oracle、ai-agent/show-me-skill、sheke/marketing/sell-before-build-validation，三者 index.md 均已在盘），本束仅按继承的已登记态 +1，不代登他会话半成品；③ `check-toctrees.py` FAIL——28 处问题全部属于他会话在飞束（show-me-skill 11、aitokenbus 7、inurl-byok-free-models 8 + 组/域 index 缺行 2），**openhuman 零问题、全文件可达**。结论：本束自身门禁等价项全绿，两项 FAIL 为跨会话瞬时漂移，待相关会话完成索引接入后自然收敛

## V 阶段审查记录

### 手动等效验证清单

- [x] **UTF-8 strict roundtrip**：全部 10 个新增 .md + 2 个修改索引，PowerShell `UTF8Encoding($false,$false)` strict 解码无异常（无 BOM）
- [x] **双份 F 编号一致**：spec `facts.md` 与 `references/article-source.md` 均为 F-001~F-064，正则集合相等、连续无跳号
- [x] **三级 toctree**：bundle 根/concepts/references 三个 index 各含 toctree 块；条目（排除 `:` 指令行）逐一对应实际文件；组 index frontmatter `total_bundles` 49→50 = toctree 条目数（50 条，openhuman 已在列）
- [x] **相对链接全可达**：bundle 内 12 处相对链接（含跨束 ../../second-me、../../pi-agent-harness、../../doubao-work，目标束均存在）逐一核对；`file:///` 零出现
- [x] **三级计数同步（按继承已登记态 +1）**：组 49→50（frontmatter=toctree=本束登记数；盘上另有并行会话在飞的 oracle/show-me-skill 未登记）；ai 域 198→199；jishu 417→418（mermaid 行+域表头两处）；全库 total_bundles 549→550（frontmatter+正文两处）。注：执行时刻目录树地面真值为 553/420，差 3/2 全部为他会话在飞束（见 gates 状态），不并入本束计数
- [x] **敏感信息零残留**：无 `/Users/`、`C:\Users\` 等家目录绝对路径（`~/.openhuman` 为产品官方路径写法）
- [x] **frontmatter 完整**：okf_version/type/title/description/tags/generated/verified/status/stale_after/sources 齐备；含博文 URL + GitHub/官方 GitBook 多信源
- [x] **勘误落实**：6 条 ⚠️ 在 00/01/02/03 篇均呈现官方现值并标注博文口径，无错误数字以事实身份流入主干

### 四视角审查

1. **事实溯源**：概念篇所有数字/功能名带 F 编号；10 亿 token、USDC、ChaCha20、React、Linux 沙箱等弱源项均降级标注
2. **结构规范**：无 examples 与两问判定一致；4 概念三层映射（事实→机制→设计→格局）；toctree 完整
3. **读者可用性**：双时点表格避免数字混用；安装命令区分"官方核验可用"与"博文口径"
4. **时效边界**：stale_after 2026-12-31 + index 已知边界 7 条 + 数字口径顶部提示块

### 索引接入

- `ai-agent/index.md`：frontmatter 49→50；「📰 产品资讯」表新增 openhuman 行；toctree 追加 openhuman/index；页脚计数同步为 50 束/355 文档（228 概念+64 示例+63 信源）
- `bundles/index.md`：total 549→550（frontmatter+正文）、jishu 417→418（mermaid+域表头）、ai 198→199（均为执行时刻的已登记态 +1；并行会话在飞束未计入）
