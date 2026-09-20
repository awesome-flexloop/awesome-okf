# 变更日志（Log）

## 2026-09-20 · 初始生成（博文转化 R→I→E→V）

- **触发**：微信公众号「极客之家」推文《GitHub 6.7万 Star，一个多 Agent 协作、手机远程指挥的开源神器！》（2026-09-14 14:05，约 2635 字）经 blog-article-to-okf-wiki 七阶段工作流转化；方法论编排走七概念场景（知识沉淀 R→I→E→V）
- **spec**：主仓库 `.trae/specs/okf-wiki-ecosystem/orca-ade-okf-wiki/`（spec.md + facts.md + tasks.md + review.md）
- **信源获取**：微信公众号 WebFetch 会被反爬拦截，按 Skill §5 步骤4 改用浏览器子代理提取 `#js_content` innerText，一次成功
- **事实登记**：F-001~F-103 连续 103 条（博文事实 F-001~F-060 含 8 处作者观点标注；核验补充事实 F-061~F-103 共 43 条）；双份登记（spec facts.md ↔ references/article-source.md）编号集合一致
- **P0 核验**（核验日 2026-09-20）：8 条 P0 声明（F-002、F-005、F-008、F-010、F-043、F-044、F-049、F-059），去重后 7 项 → **2 ✅ / 6 ⚠️ / 0 ❌**
  - ✅ 关键证实：macOS 安装命令 `brew install --cask stablyai/orca/orca` 逐字命中官方 tap（F-070）；"Free and open source"无 pricing 页（F-049 / F-072）
  - ⚠️ **E-1 域名硬错误**：博文写 `onnorca.dev`，正确为 **`onorca.dev`**（仓库 homepage、Homebrew cask homepage、YC 页三方佐证）——照抄会把读者带到不存在域名
  - ⚠️ E-2 账号口径矛盾：桌面"no account system" vs 移动端配对需登录，官方文档自相矛盾
  - ⚠️ E-3 星标口径：博文 6.7 万（发文时点）/ 核验日 66,453 / 第三方 70.5K–71.4K
  - ⚠️ E-4 "ADE" 全称（Agent Development Environment）无官方出处，官方仅用缩写
  - ⚠️ E-5 具名 Agent 数三口径：README 29 / 官网 27 / docs 表 35 行
  - ⚠️ E-6 Android 无 Google Play 官方条目 + 官网 0.0.48 与 README 0.0.50 版本不一致
  - （E-7 为补充项：安装包形态 macOS dmg / Windows exe / Linux AppImage）
- **骨架判定**：操作可复现性两问 → Q1 是、Q2 是但含限定（作者仅声明 macOS 一行命令实测，无版本号、无命令输出，Win/Linux 为转述）→ 设 `examples/`（2 篇），并施加两条限定：① 每条命令须经官方文档逐字核验；② examples 顶部显式标注"非博文实测、本包制作中未真机执行"
- **归属判定**：`jishu/ai/orca-ade`（落既有分组，否决新建分组与 `jishu/dev`）；bundle 名带 `-ade` 后缀消歧——Homebrew 官方 cask `orca` 是 plotly 图表工具（F-071），裸名会在检索与引用上混淆
- **文件**：12 个（root index/log + concepts 4 + examples 3 + references 3）
- **状态**：stable；stale_after=2026-11-30（周级迭代 + 移动端版本口径尚未收敛，缩短复核窗口）

## 2026-09-20 · V 阶段机械门禁与索引接入

> 说明：以下门禁**直接运行仓库 stdlib 脚本**（`projects/awesome-okf-xs/scripts/`），未经 `invoke gates.*` / invocations 通道，故不声称"`invoke gates` 通过"。

- ✅ `scripts/check-bundles-index.py`：通过 —— **9 域 / 59 组 / 557 束**，frontmatter、计数行、节标题、分组表、toctree 五面一致（本束 +1；同步 `bundles/index.md` 的 `total_bundles`、jishu 节标题、mermaid 节点、ai 分组束数 204→205）
- ✅ `scripts/check-utf8.py`：通过 —— 10434 个文件均为有效 UTF-8（本束无 BOM、strict roundtrip 无乱码）
- ✅ `scripts/check-toctrees.py`：**本束 12 个文件零问题**（无孤立、无断链，根 index 已接入 ai 组 toctree）；脚本当次报出的 4 处问题**全部属于他会话进行中的 WIP**（`jishu/ai/jev` 缺 index.md 及 3 个文件未收录），按"谁添加谁对账"未代为修改
- ✅ **双份 F 编号集合一致**：`facts.md` ↔ `article-source.md` 正则提取均为 **F-001~F-103 连续 103 条**，Compare-Object 集合相等、无跳号、无缺号
- ✅ **相对链接全可达**：39 条 Markdown 相对链接逐一 Test-Path 通过（另有 11 条沿用分组既有的 `/concepts/` 根绝对形式，见下方备注）；**V 中发现并修复 3 条跨束链接层级错误**——`concepts/02-ecosystem-and-fit.md` 指向 echobird/loopx/codex-agent-workflow-practices 的链接原写作 `../<sibling>/index.md`（从 concepts/ 出发会解析到束内不存在的目录），已改为 `../../<sibling>/index.md`
- ✅ **`file:///` 零出现**；家目录绝对路径（`C:\Users`、`/Users/`、`D:\spaces`）零残留
- ✅ **frontmatter 十项齐备**：8 个带 frontmatter 的文档全部含 `okf_version/type/title/description/tags/generated/verified/status/stale_after/sources`；**V 中补齐 `references/verification.md` 缺失的 `verified` 字段**（其余 4 个 index.md 与 log.md 按本库约定不设 frontmatter）
- ✅ **勘误落实核对**：`onnorca.dev` 全束共 10 处出现，**逐处确认全部位于勘误/核验语境**（index.md 先读提示、log.md E-1 记录、examples/00 安装坑位提醒、article-source.md 与 verification.md 核验记录）；所有运营性表述统一使用正确域名 `onorca.dev`，博文硬错误未原样照搬
- ✅ **P0 统计一致**：index.md / verification.md / log.md 三处均为"8 条 P0（去重 7 项）→ 2✅/6⚠️/0❌"，与 spec `facts.md` 结论一致
- 备注：本束内跨目录引用沿用 `jishu/ai` 分组的既有约定（`/concepts/...` 根绝对形式，同分组内已有 704 处先例），未单独改动；束间互链统一使用相对路径