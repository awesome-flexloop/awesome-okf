# Agent Reach 知识包变更日志

## 2026-10-08 · 初版生成（博文→OKF Bundle）

- **来源**：微信公众号「AI赋能干货铺」《9.2万星炸场：给AI装上眼睛，16个平台一个CLI全打通》（作者学生小孙，2026-10-06 15:03，6833 字）
- **方法论**：七概念场景 4 知识沉淀链路 R→I→E→V→C，由 seven-concepts-cmd 元编排 + blog-article-to-okf-wiki 七阶段执行
- **规模**：14 文件（4 concepts + 3 examples + 2 references + 3 目录 index + 根 index + 本日志）；F 编号事实 72 条（博文 54 + 官方核验 18）

### R（事实采集与核验）

- 微信公开文章（无 code/token）→ 公开内容标准工作流；经 browser_use 提取 `#js_content` innerText（6833 字，结尾完整，五条启示与全部命令块保留）
- 信源距离预判：第三方公众号综述（非厂商自宣通稿、非一手实测），以转述 README + 作者解读为主
- P0/P1 核验 21 项（GitHub REST API + main 分支 README 全文 15,086 字符 + docs/install.md + git tree + neodrop/GitCode/lobehub/deepwiki 旁证）：**16✅ / 5⚠️ / 0❌**
- 5 项 ⚠️：Star 动态时点（博文 92k vs 2026-10-08 实测 93,673）、**博文内部 6/7 零配置口径矛盾**、SKILL.md 实际在 `agent_reach/skill/`（非根目录）、channels 示意树 9/13 vs 实际 20 文件/17 实现、lobehub 旧镜像"13+ platforms"口径；pipx 命令出处仅 install.md（README 无）已注明
- 官方补充事实：v1.5.0（2026-06-11，7 个 release）、36 贡献者、TWITTER_AUTH_TOKEN/CT0、OpenClaw exec 前置、$1/月代理、PyPI 同名包警告、赞助商与业务合作商业化披露

### I（骨架与归属）

- 操作可复现性两问皆"是"（pipx/install/doctor/渠道命令可照做且经官方文档逐字确认）→ 技术教程类骨架，设 examples/
- 归属：`jishu/ai/products/agent-reach/`（同构先例 wigolo：本地 Web 情报层 CLI、博文转化、含安装实操）

### E（bundle 生成）

- 信源先行：article-source.md → verification.md → concepts×4 → examples×3 → 各级 index → 根 index 最后写
- 全部数字/命令/版本携带 F 编号；五条设计启示与"92k 真正原因"等显式标注 V（作者观点）并附适用边界；README 引文标 S
- 能力层架构含 1 张 Mermaid flowchart（有序后端列表示意）

### V（对抗审查与机械门禁）

四视角审查（独立 fresh-context 式自查）：

1. 🔴 魔鬼代言人 → 补"未实测 17 渠道当前可用性/未复现 doctor"局限、Cookie 账号风险、PyPI 供应链警告、赞助商影响"中立选型"叙事
2. 🟠 老板视角 → 补个人维护项目供应风险（owner=User、系于上游风控），建议锁版本 + dry-run + doctor 自检
3. 🔵 未来视角 → stale_after=2026-12-31，列明复核项（Star/默认激活数/channels 实现数/SKILL 路径/选型链）
4. 🔗 链接自检 → 跨束互链仅引用 products 下已存在束（wigolo/browseract/open-code-review/loopx/todesk-ai），相对深度核对

机械门禁（官方 invoke gates，cwd=子模块根，`python scripts/check-*.py` 直调）：

| 检查项 | 结果 |
|--------|------|
| `gates.utf8`（check-utf8.py，全 doc/） | ✅ 11,036 个文件均为有效 UTF-8 |
| `gates.toctrees`（check-toctrees.py，全 bundles） | ✅ 全部 index.md 引用有效、所有内容文档可达 |
| `gates.bundles`（check-bundles-index.py，三角对账） | ✅ **9 域 / 61 组 / 596 束**，frontmatter/计数行/节标题/分组表/toctree 五面一致 |
| 双份 F 编号正则核对（facts.md ↔ article-source.md） | ✅ F-001~F-072 连续无跳号、集合相等（各 72） |
| 正文 F 引用合法性 | ✅ 正文所有 F-NNN 均落在 1~72 合法集，无悬空引用 |
| 束内/跨束相对链接 | ✅ 59 条相对链接全部解析成功，无本地绝对路径链接 |
| frontmatter 完整 | ✅ okf_version/type/title/description/tags/generated/status/stale_after/sources 齐备 |
| 敏感信息 | ✅ 无绝对家目录（以 ~/ 与 %USERPROFILE% 表述）、无密钥/token 真值；"XXX" 命中均为博文本义示例 |
| 勘误落实 | ✅ 5 项 ⚠️ 根 index 速查 + 正文均呈现官方值并标注博文口径 |
| 三级索引计数接入 | ✅ products 20→21、ai 217→218（frontmatter+正文+六大类表）、total 595→596、jishu 438→439；另修正 jishu/index.md 滞后的 ai 描述 216→218（见冲突登记） |

### 并行会话冲突与在途状态登记（重要）

- 生成时子模块工作区有**他人未提交改动**：M `doc/bundles/index.md`、`jishu/ai/index.md`、`jishu/ai/products/index.md`、`sheke/index.md`、`sheke/personal-growth/index.md`；未跟踪 `jishu/ai/products/pixelle-video/`、`sheke/personal-growth/naval-learn-build-link/`、`wechat-presence-joy-meditation/`、`wechat-public-expression-lift/`。
- 上述均与本任务无关。**HEAD 基线核实**（`git show HEAD:`）：products=19、ai=216、total_bundles=591、jishu=437；并行会话未提交改动已把三个共享索引抬到 20/217/595/438（pixelle +1 与 sheke +3），本束再 +1 至工作区现值 21/218/596/439。
- **耦合结论**：本束对 `doc/bundles/index.md`、`jishu/ai/index.md`、`jishu/ai/products/index.md` 的计数改动与并行会话改动落在**同一文件同一计数行**（如 total 591→596 含他人 +4），无法用整文件 `git add` 干净剥离；非交互环境又不支持 `git add -p`。`jishu/index.md` 是唯一干净文件（HEAD 描述停在 216），已直接修正为 218，属本束纯 hunk。
- **提交裁决（C 阶段请用户定夺，不自动整文件暂存）**：① 仅提交本 bundle 14 文件 + jishu/index.md，三个共享索引待并行会话先行提交后再补（代价：该中间提交 gates.toctrees 暂时不绿，agent-reach 未挂 products toctree）；② 等并行会话提交后，rebase 到新基线再只提本束（最干净，推荐）；③ 一次性合提全部未跟踪束（会带走他人无签字工作，不推荐）。sheke 两个已修改索引与三个未跟踪 sheke 束任何方案下都不纳入本任务。

### C（提交）

- 待原子提交（用户确认后执行，不 push）：① 子模块 awesome-okf-xs（本 bundle 14 文件 + 三级索引本束增量行）→ ② 主仓库 spec（agent-reach-blog-okf-wiki/）→ ③ 主仓库 gitlink 指针

---

## 2026-10-26 · 第二篇博文并入 + v1.6.0 基线校正（更新，非重建）

- **来源**：微信公众号「架构文摘」《87.7k Stars！给 Agent 装上全网之眼，零 API 费，读遍16个国内外主流自媒体平台》（2026-10-17 09:08，约 3,594 字符）
- **方法论**：seven-concepts-cmd 元编排 + blog-article-to-okf-wiki 七阶段；场景为「知识沉淀 + 版本维护」混合链路
- **幂等判定**：目标实体已有本 bundle（首版 2026-10-08，源于另一篇文章）。同一项目建第二个 bundle 会割裂主题，故选择**并入更新**：保留 F-001~F-072 与既有 14 个文件，新增第二批登记与两篇概念，回改 5 处过期口径。
- **规模**：18 个 md（新增 2 篇 concepts、2 份 references，重写 3 篇 examples 与根 index、3 处目录 index）；F 编号 **F-001~F-120 连续无跳号**（新增 F-073~F-120，48 条）

### R（事实采集与核验）

- 微信公众号反爬：直接用 browser 取 `#js_content` innerText，正文 3,594 字符、结尾完整（F-073）
- 信源距离：第三方公众号综述 + **作者自陈未逐条真机复现**（F-074）→ 全部结论回官方材料复核，不采信二手转述
- 核验 20 项 P0/P1：**10 ✅ / 6 ⚠️ / 4 ❌**；证据为 GitHub API、main README/install.md/SKILL.md/sessions.md、v1.5.0 tag README 与 install.md、channels 目录树、releases 列表
- 4 项 ❌：Star 87,759（低于 9 天前 93,673）、`pip install agent-reach`（PyPI 同名包）、`--system`（参数不存在）、"不读取小红书浏览器 Cookie"（与自动复制会话矛盾）
- 复核顺带发现首版 5 处过期：`--system`×3、"不读 Cookie"、16/6 默认口径、v1.5.0/93.7k、`check-update`

### I（骨架与归属）

- 操作可复现性两问仍为"是" → 保留 examples/，但按 v1.6.0 重写（uv 安装、默认 5 渠道、专用浏览器）
- 新增知识层：团队落地（转化层）与版本漂移（判读规则层）；归属仍为 `jishu/ai/products/agent-reach/`，不新建分组、不新建 bundle

### E（bundle 生成）

- 信源先行：`article-source-02.md` → `verification-02.md` → `concepts/04`、`concepts/05` → 重写 examples → 目录 index → 根 index 最后写
- 新文档全部带 OKF v0.2 frontmatter、sources、stale_after（2027-01-31）；观点（V）与项目自述（S）逐条标注
- 首版两份 reference 顶部加"第二批复核补注"，保留历史记录同时指向新结论（不静默改写历史）

### V（对抗审查与机械门禁）

四视角审查：

1. **魔鬼代言人** → 补 "16 有代码依据但表格只列 13 行" 的双向论证，避免把口径差异写成造假
2. **老板视角** → 补团队基线锁版本、CI 不硬卡全绿、赞助商 6 家披露
3. **未来视角** → stale_after 延至 2027-01-31，列出 v1.7/安装器/渠道表三个复核触发点
4. **链接与引用** → 相对链接 0 断链，F 引用全部落在 1~120 且存在于登记表

机械门禁（官方脚本，cwd=子模块根）：

| 检查项 | 结果 |
|--------|------|
| `check-utf8.py doc` | ✅ 12,428 个文件均为有效 UTF-8 |
| `check-toctrees.py doc` | ✅ 全部 index.md 引用有效、内容文档可达 |
| `check-bundles-index.py doc` | ✅ 9 域 / 63 组 / 681 束，五面一致（首次运行有 3 处计数漂移来自并行会话未提交束，随后由该会话补齐；本任务新增束数 = 0） |
| F 编号自检 | ✅ F-001~F-120 共 120 条，无重复、无跳号；正文引用 109 个编号全部在集合内 |
| 相对链接 / toctree 条目 | ✅ 0 断链、0 缺失条目；无 `本地绝对路径` 绝对链接（仅 log 内文字提及） |
| frontmatter 完整 | ✅ 17 个内容/索引文档均含 okf_version/type/title/description/tags/generated/status/stale_after/sources（子目录 index 按规范免 frontmatter；log.md 仅变更日志） |
| 敏感信息 | ✅ 无家目录绝对路径、无密钥/token 真值；token 示例统一为 `"..."` |
| 勘误落实 | ✅ 4 项 ❌ 均在根 index 速查 + 对应正文呈现正确值，并标注原文口径 |

> spec 说明：首版 `.trae/specs/agent-reach-blog-okf-wiki/` 未入库（当前仓库不存在），故双份 F 登记不适用；本次以 bundle 内单一登记表 + 编号连续性/引用闭包自检替代，并在 `verification-02.md` 记录。

### C（提交）

- 未提交（按仓库规范等用户确认，不 push）。拟提交范围：本 bundle 18 个 md + `jishu/ai/products/index.md` 的本束描述行；`doc/bundles/index.md`、`jishu/index.md`、`jishu/ai/index.md` **不动**（避免带走并行会话未提交的计数改动）
