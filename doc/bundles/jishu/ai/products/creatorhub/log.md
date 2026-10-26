# CreatorHub 知识包变更日志

## 2026-10-26 · 初版生成（博文→OKF Bundle）

- **来源**：微信公众号「明见如是」《发现一个自媒体效率神器：CreatorHub，一个本地面板，把抖音小红书快手视频号全管了》（2026-08-28 17:02，正文 1761 字）
- **方法论**：七概念场景 4 知识沉淀链路 R→I→E→V→C，由 seven-concepts-cmd 元编排 + blog-article-to-okf-wiki 七阶段执行
- **规模**：16 文件（5 concepts + 4 examples + 2 references + 3 目录 index + 根 index + 本日志）；F 编号事实 72 条（博文 19 + 官方核验 41 + 差异 8 + 补充 4）

### R（事实采集与核验）

- 微信公开文章（无 code/token）→ 公开内容标准工作流；browser 打开后提取 `#js_content` innerText，正文 1761 字，结尾完整，无截断
- 信源距离预判：**第三方公众号产品推介**（非厂商自宣通稿、非一手实测），以功能转述 + 作者使用感受为主
- P0/P1 核验 23 项（GitHub REST API + README 26,355 字节 + requirements.txt + CHANGELOG + git tree + 根目录 contents + MediaCrawler 旁证）：**14✅ / 7⚠️ / 2❌**
- 两项 ❌：① “开源”——根目录无 LICENSE、API license=null，默认版权保留；② “视频号全管”——仅本账号数据，不支持他人作品监控/下载
- 7 项 ⚠️：Star 动态值（1.7k→2,562）、Playwright→Patchright、Windows 安装版时效（08-28 无 Release，09-14 起可双击）、“统一发多平台”口径收窄、账号密码“不经第三方”绝对化、部署门槛分模式、版权归属表述过强
- 官方补充：6 个 Release（v0.1.0 2026-09-10 → v0.2.4 2026-10-16）、Windows 安装版与 WebView2、任务队列 + conservative 风控、风控中心、fingerprint-chromium、Bark/钉钉/Telegram、无代码签名提示、IPWO 赞助商披露

### I（骨架与归属）

- 操作可复现性两问皆“是”（安装、启动、账号、监控、采集、下载、发布均有官方步骤与命令）→ 技术教程类骨架，设 examples/（4 篇）
- 归属：`jishu/ai/products/creatorhub/`（同组先例 OpenCreator、VidBee、wigolo：本地优先工具 + 博文核验）
- 三层拆分：事实层（00）→ 机制层（01 架构 / 02 能力 / 03 风控）→ 边界层（04 许可合规）

### E（bundle 生成）

- 信源先行：article-source.md（由 facts.md 表格体生成，保证双份逐字一致）→ verification.md → concepts×5 → examples×4 → 各级 index → 根 index 最后写
- 全部数字/版本/命令携带 F 编号；作者感受与判断标 V（F-019）；官方自述标 O/S
- 1 张 Mermaid 架构图（四层）+ 1 张任务生命周期图（队列/风控）；示例命令均来自 README，未虚构

### V（对抗审查与机械门禁）

四视角审查：

1. 魔鬼代言人 → 补“未实机复跑”“Star 不等于可用性”“无签名安装包供应链风险”“赞助商影响中立性”边界
2. 老板视角 → 补供应风险（单维护者/平台改版）、无 LICENSE 导致不可分发、视频号缺口影响采购决策
3. 未来视角 → stale_after=2027-01-31，列明五项复核（LICENSE、视频号能力、Release、Star、安装要求）
4. 链接自检 → 跨束互链仅引用同组已存在束（opencreator/vidbee/wigolo），相对深度核对

机械门禁（手动等效验证，依赖不可用时不声称 gates 通过）：

| 检查项 | 结果 |
|--------|------|
| UTF-8 strict roundtrip | ✅ `python scripts/check-utf8.py`：12,428 个文件均为有效 UTF-8（exit 0） |
| 双份 F 编号一致 | F-001~F-072，两文件各 72 条，连续无跳号 |
| 三级 toctree 完整 | ✅ `python scripts/check-toctrees.py`：全部 index.md 引用有效、所有内容文档可达（exit 0） |
| 相对链接可达 | ✅ 束内 36 条相对链接全部解析成功；0 处 file 协议链接；跨束互链深度已核对 |
| 计数同步 | ✅ `python scripts/check-bundles-index.py`：9 域 / 63 组 / **681 束**（exit 0）；products 34→35、ai 268→270（含既有 practice 计数漂移 +1 修正）、jishu 500→502、total 679→681 |
| 敏感信息零残留 | ✅ 新增文档无家目录绝对路径、无 file 协议链接；无密钥/Cookie 真值 |
| frontmatter 完整 | ✅ 根 index 与 11 篇内容文档均含 okf_version/type/title/description/tags/generated/verified/status/stale_after/sources；子目录 index 按 OKF 约定不含 frontmatter |
| 勘误落实 | ✅ 6 项口径在根 index + 00 + 02 + verification 正文落实，采用官方值并标注源文口径 |

### 门禁结果（2026-10-26）

三项官方脚本全部 exit 0：`check-utf8.py`（12,428 文件）、`check-toctrees.py`（导航完整）、`check-bundles-index.py`（9 域 / 63 组 / 681 束，五面一致）。双份 F 编号 F-001~F-072 各 72 条。

### C（提交）

- **未提交（并发保护）**：开工后工作区出现并行会话对 gent-reach/ 的未提交改动（18 个修改 + 4 个新增文件），且与本任务共享 products/index.md、i/index.md、jishu/index.md、undles/index.md。整文件暂存会把他人未签字改动一并带入，故本任务不在该状态下提交。
- 待并行改动落定后，按显式文件列表提交：① 子模块（bundle 16 文件 + 四级索引本束增量）→ ② 主仓库 spec（creatorhub-blog-okf-wiki/）→ ③ 主仓库子模块指针。
- 用户未要求 push；不自动 push。

### 并发与基线登记

- 开工前子模块 `git status`：仅 `M README.md`（与本任务无关）；主仓库 `M projects/awesome-okf-xs`、`?? apps/jieban-zhilv-mp/`
- 索引基线：total_bundles 679、domains 9、groups 63；jishu 500、ai 268、products 34（读取时点 2026-10-26）
