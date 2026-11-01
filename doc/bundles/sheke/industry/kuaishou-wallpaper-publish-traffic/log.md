# 变更日志

## 2026-11-01

- **内容敏感度预检**：用户提供的 `mp.weixin.qq.com` 图文，无登录、验证码、邀请码或付费墙，判为**公开内容（Public）**，产出落 `doc/bundles/sheke/industry/`，规范件入 `.trae/specs/okf-wiki-ecosystem/kuaishou-wallpaper-publish-traffic-okf-wiki/`。
- **采集（降级通道）**：WebFetch 直取页面 `page.html`（3,466,253 字符）后实测发现 **`js_content` 仅约 3588 字符、正文无知识性文字**——内容为一个 **242.67 秒** `video_iframe`（`data-mpvid=wxv_4684122996708737027`）与两则红字警示。故取证降级为：从页面 HTML 提取视频地址 → 本地下载（`.temp/kuaishou-wx/video.mp4`，**不随包发布、正文不引用**）→ 本地离线 ASR（`local-asr`，Intel AIPC）转写音轨。
- **ASR 转写求全**：首轮全片转写止于 **137.547 秒**，与视频总长 242.67 秒不符（疑截断）。改用**三段拼合**策略补全——全片首段（137.547s）+ 桥接段（`-ss 140 -t 60` → 20.156s）+ 尾段（`-ss 190` → 25.127s），确认全文覆盖完整。三段原文均落 [article-source.md](references/article-source.md)「附：ASR 转写三段原文」。
- 按 `blog-article-to-okf-wiki` 模式执行 R → I → E → V：
  - **R**：[事实登记](references/article-source.md) F-001~F-053，连续无跳号；口径分布 `page_fact` 3 / `meta` 4 / `official_doc` 1 / `third_party` 5 / `video_claim` 40，**无 `reporter_test`**。
  - **P0**：完成 **C1~C9** 核验（**4 项通过**：C1、C3、C4、C5；**4 项部分通过**：C2、C7、C8、C9；**1 项未通过**：C6），另登记 **E1~E4** 口径差异与勘误、**G1~G4** 缺口，判定 `status: flagged`，有效期 `stale_after: 2027-03-31`。
  - **I**：骨架判定两问——① 有读者可照做的操作流程（**是**）；② 经信源演示可复现（**是**，讲师真机演示）→ **设 `examples/`**。三层拆分——小程序与口令层、快手端发布层（流程 / 文案 / 设置）、发布后与边界层。
  - **E**：**信源先行**——先写 `references/`（article-source + verification），再写 `concepts/` 七篇，再写 `examples/` 两篇，最后写 bundle 根 `index.md` 与 `log.md`。全程在 bundle 三处（[index.md](index.md)、[concepts/00](concepts/00-overview.md)、[article-source.md](references/article-source.md)）**强制声明信源性质为 ASR 转写**。
- **归属决策**：`sheke/industry/kuaishou-wallpaper-publish-traffic/`（同组已有 `wallpaper-selection-directions` 选题上游包；未选 `marketing`/`personal-growth`/`jishu`/新建分组，理由见 spec.md「归属判定」）。

### 核验摘要

- ✅ 通过（4 项）：源页面与视频元信息（C1）、页面正文无知识性文字与降级取证路径（C3）、小程序名称「推图社」多源确认（C4）、「发快手」能力经快手开放平台官方文档确认存在（C5）。
- ⚠️ 部分通过（4 项）：日期口径（C2，DOM `ct=1788787853` → 2026-09-07 21:30，与首轮 WebFetch 记 13:30 有差异，以 DOM 为准）、「允许下载」开关效果无官方规则文档（C7）、可见范围默认口径未见官方专述（C8）、ASR 疑误词（C9）。
- ❌ 未通过（1 项）：**图片数量三口径冲突（9 / 12 / 31）且无官方口径**（C6）——本报告唯一确定未通过项；正文与示例均**并列呈现、不裁决、不写成平台上限**。
- 口径差异 4 组（E1~E4）；已知缺口 4 项（G1~G4，见下文）。
- ASR 疑误词 5 组：推图设→推图社、推流社→推图社、三刀杠→三横杠、点查掉→点叉掉、高热高（⚠️疑似「热度高」连读），登记于[引文逐字核对表](references/article-source.md)。

### 勘误落实

- **未静默照搬**：图片数量三口径（9 / 12 / 31）在 [concepts/06](concepts/06-risks-and-open-questions.md) 与 [examples/02](examples/02-pre-publish-checklist.md) 均以**并列冲突表 + 明确提示**呈现，禁止写成「平台上限」；「当天只发一条」在 [concepts/05](concepts/05-post-publish-and-assignment.md) 明示为**课程作业约束而非平台规则**；「允许下载关闭」在 [concepts/04](concepts/04-pre-publish-settings.md) 明示**效果未获官方口径**。
- **无成效数字**：[成效数字溯源表](references/verification.md)明确「本包不含任何收益、涨粉、播放量成效数字」；讲师口播的「五点几亿 / 一点几亿」标注为**举例性描述、非阈值**。

### 门禁结果

- `invoke gates.*` 依赖不可用（仓库内无 `tasks.py`），按**等价命令**在 `projects/awesome-okf-xs/` 下直接执行底层脚本，结果见下方「执行记录」。

### 已知环境基线

- 计数更新按**磁盘实测真值 + 本包 +1** 计算（`check-bundles-index.py` 以目录树为唯一地面真值）：总索引 `total_bundles` **+1**、`sheke` 域 **+1**、`industry` 分组 **+1**。
- 本包未执行 Git 提交，等待用户明确提交请求。

## 2026-11-01 · 门禁执行记录

在 `projects/awesome-okf-xs/` 下按等价命令直接执行底层脚本（`invoke gates.*` 依赖不可用）：

| 门禁 | 命令 | 结果 |
|---|---|---|
| UTF-8 | `python scripts/check-utf8.py` | ✅ 12699 个文件均为有效 UTF-8 |
| toctree | `python scripts/check-toctrees.py` | ✅ 全部 index.md 引用有效，所有内容文档均可达 |
| 总索引对账 | `python scripts/check-bundles-index.py` | ✅ 9 域 / 64 组 / **700 束**，frontmatter、计数行、节标题、分组表、toctree 五面一致（首跑报 3 处漂移，按目录树真值修复后复跑通过） |
| 资产基线口径 | `python scripts/check-asset-baseline.py` | ⚠️ 未通过：工作区行尾归一后字节与 HEAD 残差 **+259768** 超容差，由**并发会话在途资产**导致，非本包内容引入；按项目约定不强行验收 |

- 双份 F 编号一致性：spec `facts.md` 与 bundle [references/article-source.md](references/article-source.md) 均为 **F-001~F-053**，连续无跳号，集合一致。
- 索引收尾实测：`total_bundles` 699→**700**、`sheke` 域 88→**89**、`industry` 分组 39→**40**（按磁盘实测真值 + 本包 +1）。
- 本包未执行 Git 提交，等待用户明确提交请求。

## 未闭环项

| 编号 | 项 | 状态 |
|---|---|---|
| G1 | 讲师身份与机构未确认（自称「老师」，无披露） | 未闭环 |
| G2 | 图片数量无官方口径（三口径 9 / 12 / 31 冲突） | 未闭环 |
| G3 | 「允许下载」开关效果无官方规则文档 | 未闭环 |
| G4 | 快手 App UI 版本未标注、未复现 | 未闭环 |

> 复核触发条件见[核验报告](references/verification.md)「七、复核触发条件」。
