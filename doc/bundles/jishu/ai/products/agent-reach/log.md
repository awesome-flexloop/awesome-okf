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
| 束内/跨束相对链接 | ✅ 59 条相对链接全部解析成功，无 file:/// |
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
