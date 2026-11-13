---
type: Log
title: "变更日志：TRAE「一键部署」"
description: "本知识包的生成、核验与门禁记录"
tags: [trae, one-click-deploy, changelog]
generated: 2026-11-12
status: draft
---

# 变更日志

## 2026-11-12

### 复核：飞书 Webhook 安全配置（用户要求验证）

- **触发**：用户要求验证飞书 Webhook 安全配置细节。
- **发现 1（我方错误）**：首版登记的信源 URL `/client-docs/bot-v3/use-custom-bots-in-a-group` 实测返回 "The documentation could not be found"（国际站变体路径）。已改正为 CN 站 `/client-docs/bot-v3/add-custom-bot?lang=zh-CN` 并实测抓取成功。
- **发现 2（口径可细化）**：官方文档比首版 F-045 细得多，新增 F-048~F-052：
  - F-048 关键词**最多 10 个**，只对 `text`/`title` 生效，**富文本 `href` 不过滤**，失败返回 `code 19024`
  - F-049 IP 白名单**最多 10 个**，支持 `123.12.1.*`、`123.1.1.1/24`
  - F-050 签名 = HmacSHA256(key=`timestamp+"\n"+密钥`, data=空串) → Base64；`timestamp` **限 1 小时**；请求体带 `timestamp`/`sign`
  - F-051 限流 **100 次/分钟、5 次/秒**；整点/半点易触发 `11232`
  - F-052 无需租户管理员审核；**无任何数据访问权限**
- **F-045 措辞修正**：由"提供三种安全配置"改为"同一机器人**可设置一种或多种**，官方'强烈建议'添加"。
- **数学影响**：事实总数 47 → **52**（原文 40 + 核验补充 12）；P0 结论不变（4 ✅ / 10 ⚠️ / 0 ❌，#11 仍为 ✅）。
- **同步面**：`references/article-source.md`、`references/index.md`（R7 URL + 映射区间 + 统计）、`index.md`（frontmatter `sources.feishu-bot`、F 范围、事实分级）、`concepts/03`（新增三种方式差别表 + 签名算法示例）、`references/verification.md`（核验表 #11、口径对照表、新增「信源可达性复核」段）。
- **预防措施**：凡在 `sources` 或信源表登记的 URL，必须实际抓取一次确认返回正文——搜索结果标题可读 ≠ 路径可达（等价于反模式「核验不过硬编官方 URL」）。

### 新增

- 初始创建 `trae-one-click-deploy` 知识包（OKF v0.2），来源为公众号「TRAE.ai」2026-11-12 公告。
- `concepts/` 4 篇：发布定位、部署工作流、支持范围与边界、三个示例与外部依赖。
- `references/` 2 篇：事实登记 F-001~F-052（复核后扩充）、P0 核验报告（4✅ 10⚠️ 0❌）。
- 归属判定：`jishu/ai/ecosystems/trae/` → 「📰 战略资讯」板块。理由：主线实体为 TRAE（字节 AI 编程产品），该分组已有同类的厂商动态/博文转化先例（`threeui`、`tushare-ai-office`、`bytedance-ai-consolidation`）；单篇公告不新建分组。

### 骨架判定

| 问 | 结论 | 说明 |
|----|------|------|
| ① 是否有读者可照做的安装/配置/代码/调用流程 | 是 | 升级 → 插件市场 → 一键部署 → 对话指令，三段 prompt 可复制 |
| ② 是否经作者实测、具备可复现性（版本/输入输出/步骤顺序） | **否** | 无客户端版本号、无实际站点链接、无构建日志与耗时 |
| 结论 | **不设 `examples/`** | 任一为否即不设；空 examples/ 制造伪结构 |

### 核验

- 信源距离：**厂商官方公告（一手）** → 存在性采信官方口径，能力细节一律单源标注。
- P0 14 项：4 ✅ / 10 ⚠️ / 0 ❌。无硬错误，故未置 `flagged`；因单源密集且公告与官方文档同日不同步，取 `status: draft`。
- 勘误四张清单完成：① 日期/版本表（客户端版本缺失、插件市场 2026-09-03 仅个人版）② 成效数字溯源表（**空项**，原文无任何提效/成本数字）③ 口径对照表（Node.js 20 已 EOL、Open-Meteo 免费额度与 CC BY 4.0 署名、飞书 Webhook 三种安全配置、限免政策无定价页）④ 引文逐字核对表（三段 prompt 逐字登记；无高管引语）。
- 源文错误：**0 项**——未发现与权威来源冲突的硬错误；发现的是"省略"而非"错误"，已全部在 [核验报告](references/verification.md) 的口径对照表中呈现。

### 索引与计数

| 文件 | 变更 |
|------|------|
| `doc/bundles/jishu/ai/ecosystems/trae/index.md` | 「📰 战略资讯」表新增本束 1 行；toctree 追加 `trae-one-click-deploy/index`；frontmatter `total_bundles` 16→17、`total_content_docs` 136→142、`total_md_files` 184→194；合计行同步 |
| `doc/bundles/jishu/ai/ecosystems/index.md` | trae 行 16→17；类内合计 105→106 |
| `doc/bundles/jishu/ai/index.md` | ecosystems 105→106；域合计 300→301 |
| `doc/bundles/jishu/index.md` | ai 行说明文字 299→301 |
| `doc/bundles/index.md` | `total_bundles` 733→734；计数行 733→734；技术域节标题 538→539；ai 表行 300→301；概览图 jishu 538→539 |
| `doc/index.md` | 首页与「关于知识包」两处 733→734 |
| `README.md` | Badge 733、正文 733 个知识包、733 束 / 64 组 / 9 域、完整 733 束清单、内容总览表 jishu 538→539 与合计 733→734 |
| `doc/_search/okf-userdict.txt` | 登记「一键部署」「Open-Meteo」，保证连写查询可命中 |

### 门禁状态

> ⚠️ **本机 Shell 工具不可用**（命令一律返回退出码 -1），`invoke gates.*` 与 `python scripts/*.py` 均无法执行。按 Skill 规范，**不得声称 gates 通过**，改以手动等效验证，结果如下：

| 检查项 | 手动等效验证 | 结果 |
|--------|--------------|------|
| UTF-8 编码 | 全部新增/修改文件以 UTF-8 无 BOM 写入 | ✅ 待 CI 复核 |
| 双份 F 编号一致 | `references/article-source.md` 内 F-001~F-052 连续无跳号（52 行表项，40 条原文 + 12 条核验补充）；`references/index.md` 区间映射覆盖同范围 | ✅ |
| 三级 toctree 完整 | 根 index 收 `concepts/index`、`references/index`、`log`；`concepts/index` 收 4 篇；`references/index` 收 2 篇；组索引已追加本束 | ✅ |
| 相对链接可达 | 全部正文链接按实际文件路径书写，无 `file:///`。**取舍说明**：OKF 允许 bundle 相对绝对路径（`/concepts/xx.md`），但本项目 Sphinx srcdir 为 `doc/`，`/` 开头会被解析到 `doc/concepts/`（不存在），故统一改用标准相对路径——concepts 内互链用同级文件名，跨目录用 `../references/`、`../concepts/`，同级束用 `../../<sibling>/index.md` | ✅ |
| 三级计数同步 | bundles/index.md(734) ↔ ai(301) ↔ ecosystems(106) ↔ trae(17) ↔ 新增 1 束 | ✅ |
| 敏感信息零残留 | 无家目录绝对路径、无凭据 | ✅ |
| frontmatter 完整 | okf_version / type / title / description / tags / generated / verified / status / stale_after / sources 齐备；sources 含博文 + 5 个核验权威源 | ✅ |
| 勘误落实 | 正文呈现的是正确值（Node.js 20 EOL、Open-Meteo 额度与署名、飞书三种安全配置），并标注源文省略 | ✅ |

### 待办

- [ ] 依赖可用的环境中补跑：`python scripts/check-bundles-index.py`、`python scripts/check-toctrees.py`、`python scripts/check-utf8.py`、`python scripts/check-asset-baseline.py`
- [ ] 2027-01-31 前复核：限免是否结束、Node.js 运行时是否升级、数据库/自定义域名是否开放
- [ ] 若官方文档补齐「一键部署」条目，将对应 ⚠️ 项升级为 ✅ 并把 `status` 转 `stable`
